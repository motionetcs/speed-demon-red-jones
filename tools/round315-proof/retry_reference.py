from pathlib import Path
import argparse,csv,hashlib,io,json,os,subprocess,sys
sys.path.insert(0,'tools');import verify
p=argparse.ArgumentParser();p.add_argument('--binary-dir',type=Path,required=True);p.add_argument('--run-id',required=True);p.add_argument('--report',type=Path,required=True);p.add_argument('--reference-report',type=Path);a=p.parse_args();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();binary=a.binary_dir.resolve()/'track-c';verify.BIN_DIR=a.binary_dir.resolve();verify.ACTIVE_TRACKS={'c'};verify.THREADS=[1,2,6,12];verify.RUN_ID=a.run_id;oracle=verify.load('test_c_join');checks=[];failures=[]
if a.reference_report:
 source=json.loads(a.reference_report.read_text());assert source['passed'];rows=source['checks']
else:
 rows=[]
 for label,unique,width,count in [('narrow-retry',132113,3,145129),('spill-retry',150013,257,165029),('all-country-retry',5003,17576,22579)]:
  codes=[chr(65+i//676)+chr(65+i//26%26)+chr(65+i%26) for i in range(width)];regions=('region_id,country\n'+''.join(f'{i+1},{c}\n' for i,c in enumerate(codes))).encode();stream=io.StringIO(newline='');stream.write('\ufeffid,name,note,region_id,amount\r\n');writer=csv.writer(stream,lineterminator='\r\n',quoting=csv.QUOTE_ALL)
  for i in range(count):
   k=i%unique;name='key'+str(k) if k%3 else 'long/'+str(k)+'/'+('x'*24)+'\"名\n ';note='note,\"line\"\nnext\ufeff' if i%11==0 else 'n'
   if i and i%997==0:stream.write('\ufeff')
   # Numeric columns must use the official unquoted numeric grammar.
   q=lambda s:'\"'+s.replace('\"','\"\"')+'\"'
   stream.write(str(i+1)+','+q(name)+','+q(note)+','+str(i%(width+1)+1)+','+('-0.05' if i%7==0 else '1.25')+('\r\n' if i+1<count else ''))
  records=stream.getvalue().encode();expected=oracle.run_reference(records,regions);expected=expected.encode() if isinstance(expected,str) else expected;case='round315-reference-'+label;folder=verify.ROOT/'.data/cases'/case;assert not folder.exists();folder.mkdir();(folder/'records.csv').write_bytes(records);(folder/'regions.csv').write_bytes(regions);expected_path=folder.parent/(case+'.expected');expected_path.write_bytes(expected);rows.append({'track':'c','case':case,'data_folder':str(folder.relative_to(verify.ROOT)),'inputs_sha256':{'records.csv':sha(folder/'records.csv'),'regions.csv':sha(folder/'regions.csv')},'reference_sha256':hashlib.sha256(expected).hexdigest(),'expected_file':str(expected_path.relative_to(verify.ROOT)),'unique_names':unique,'country_count_without_unmatched':width,'initial_capacity':131072 if width<256 else 65536 if width==257 else 2048,'minimum_capacity_retries':1 if width<256 else 2,'runs':[]})
 # References are durable before execution; a failed test never requires regeneration/oracle repetition.
 a.report.with_suffix('.references.json').write_text(json.dumps({'passed':True,'input_reference_only':True,'checks':rows},indent=2)+'\n')
for row in rows:
 folder=verify.ROOT/row['data_folder'];expected=(verify.ROOT/row['expected_file']).read_bytes();assert sha(verify.ROOT/row['expected_file'])==row['reference_sha256'];assert {p.name:sha(p) for p in folder.iterdir() if p.is_file()}==row['inputs_sha256'];entry={**row,'runs':[]}
 for threads in [1,2,6,12]:
  out=verify.ROOT/'.out'/a.run_id/row['case']/str(threads);out.mkdir(parents=True);env=dict(os.environ,SPEED_DEMON_THREADS=str(threads),ASAN_OPTIONS='halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1',TSAN_OPTIONS='halt_on_error=1');q=subprocess.run([str(binary),'--data',str(folder),'--out',str(out)],capture_output=True,env=env,timeout=180);assert q.returncode==0 and not q.stdout and not q.stderr,(row['case'],threads,q.returncode,q.stderr[-3000:]);assert [p.name for p in out.iterdir()]==['aggregates.txt'] and (out/'aggregates.txt').read_bytes()==expected;entry['runs'].append({'requested_threads':threads,'sha256':row['reference_sha256'],'returncode':0})
 checks.append(entry);print('PASS315 actual whole-attempt retry',row['case'],flush=True)
# Error appears after more unique keys than original capacity. With one worker the capacity retry must precede the normal parse error. No partial output permitted.
base=rows[0];folder=verify.ROOT/base['data_folder'];records=(folder/'records.csv').read_bytes()+b'\r\n999999,"late","note",1,bad\r\n';regions=(folder/'regions.csv').read_bytes();bad_case='round315-reference-late-error';bad=verify.ROOT/'.data/cases'/bad_case
if not bad.exists():bad.mkdir();(bad/'records.csv').write_bytes(records);(bad/'regions.csv').write_bytes(regions)
assert (bad/'records.csv').read_bytes()==records and (bad/'regions.csv').read_bytes()==regions
for threads in [1,2,6,12]:
 out=verify.ROOT/'.out'/a.run_id/bad_case/str(threads);out.mkdir(parents=True);q=subprocess.run([str(binary),'--data',str(bad),'--out',str(out)],capture_output=True,text=True,env=dict(os.environ,SPEED_DEMON_THREADS=str(threads),ASAN_OPTIONS='halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1',TSAN_OPTIONS='halt_on_error=1'),timeout=180);assert q.returncode==1 and not q.stdout and q.stderr.startswith('track-c: invalid money') and not any(out.iterdir()) and not any(x in q.stderr for x in ['Sanitizer','runtime error:','DEADLYSIGNAL']),(threads,q.returncode,q.stderr);failures.append({'case':bad_case,'data_case':bad_case,'data_folder':str(bad.relative_to(verify.ROOT)),'threads':threads,'inputs_sha256':{p.name:sha(p) for p in bad.iterdir()},'returncode':1,'stderr':q.stderr})
a.report.write_text(json.dumps({'passed':True,'official_score':False,'binary_sha256':sha(binary),'scope':'Independent Python official CSV/set/cents reference, created once and reused by input/output hashes. Distinct counts132113/150013/5003 exceed actual narrow/spill/all-country initial capacities131072/65536/2048 and require whole-attempt retries, duplicate rows validate no leaked partial totals. Allcountry17576 plus unmatched, inline/long/escaped/UTF8/BOM/LF/CRLF/EOF. Runs1/2/6/12. Late normal error after capacity pressure produces no partial output; worker1 necessarily retries before late error. No protocol instrumentation or forced-scheduling claim.','checks':checks,'expected_failures':failures},indent=2)+'\n')
