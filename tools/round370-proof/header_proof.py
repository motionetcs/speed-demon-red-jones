from pathlib import Path
import datetime,hashlib,importlib.util,json,os,subprocess
r=Path.cwd();w=r/'.build/round370';out=w/'header-proof';out.mkdir(exist_ok=True);data=w/'header-data';data.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,j):p.write_text(json.dumps(j,indent=2)+'\n')
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
test=load('c370_header_fixtures',r/'tools/official/tests/test_c_join.py');ref=test.ref
pre=json.loads((w/'preflight.json').read_text());report={'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'New actual-main compatibility fixtures for all32 quoted-record-header masks plus BOM/terminator/EOF and quoted-region-header extensions. These extensions exceed the frozen literal generator header; no narrower generator-only acceptance is used. Supported new fixtures official-reference compared once; BOM+quoted-first-header extensions use unchanged official hand-computed worked payload output plus original-control executions because reference assumes unquoted first field; oldcontrol and new370 ASAN/TSAN actually run. No new compiler or old generator/oracle repetition.','official_score':False,'source_sha256':pre['source_sha256'],'checks':[],'expected_failures':[]}
for p,h in pre['source_sha256'].items():assert sha(w/'source'/p)==h
for p,h in pre['root_selected_bindings'].items():assert sha(r/p)==h
labels=[b'id',b'name',b'note',b'region_id',b'amount'];payload=test.WORKED_RECORDS.split(b'\n',1)[1];regions=test.WORKED_REGIONS
def encode(parts,mask):return b','.join(b'"'+p.replace(b'"',b'""')+b'"' if mask>>i&1 else p for i,p in enumerate(parts))
fixtures=[]
for mask in range(32):fixtures.append((f'mask-{mask}',(test.BOM if mask&1 else b'')+encode(labels,mask)+(b'\r\n' if mask&2 else b'\n')+payload,regions,test.WORKED_OUTPUT))
for mask in [0,31]:
 for bom in [False,True]:
  for crlf in [False,True]:fixtures.append((f'cross-{mask}-{int(bom)}-{int(crlf)}',(test.BOM if bom else b'')+encode(labels,mask)+(b'\r\n' if crlf else b'\n')+payload,regions,test.WORKED_OUTPUT))
for mask in range(4):
 for crlf in [False,True]:fixtures.append((f'region-{mask}-{int(crlf)}',test.WORKED_RECORDS,encode([b'region_id',b'country'],mask)+(b'\r\n' if crlf else b'\n')+regions.split(b'\n',1)[1],test.WORKED_OUTPUT))
for mask in [0,31]:
 for bom in [False,True]:fixtures.append((f'empty-eof-{mask}-{int(bom)}',(test.BOM if bom else b'')+encode(labels,mask),regions,b''))
seen=set();bank=[]
for label,records,reg,expected in fixtures:
 key=(records,reg)
 if key in seen:continue
 seen.add(key);folder=data/label;folder.mkdir(exist_ok=True);(folder/'records.csv').write_bytes(records);(folder/'regions.csv').write_bytes(reg)
 oracle=out/'references'/label;oracle.mkdir(parents=True,exist_ok=True)
 if records.startswith(test.BOM+b'"'):
  # Official reference assumes an unquoted first field before stripping BOM.
  # This is an extra compatibility case, with unchanged hand-computed payload.
  (oracle/'aggregates.txt').write_bytes(expected);reference_kind='hand-computed official WORKED_OUTPUT or empty-output invariant; official reference does not support BOM+quoted-first-header extension'
 elif (oracle/'aggregates.txt').exists():
  assert label=='mask-0';reference_kind='exact saved successful first-attempt official-reference output, not rerun'
 else:
  ref.main(str(folder),str(oracle));reference_kind='new fixture official reference executed once'
 assert(oracle/'aggregates.txt').read_bytes()==expected,label
 bank.append({'case':'round370-header-'+label,'data_folder':str(folder.relative_to(r)),'inputs_sha256':{p.name:sha(p)for p in folder.iterdir()},'reference_sha256':sha(oracle/'aggregates.txt'),'reference_kind':reference_kind,'runs':[]})
errors=[]
for col in range(5):
 for kind in ['suffix','quote']:
  parts=list(labels);parts[col]+=b'x' if kind=='suffix' else b'"';label=f'bad-{col}-{kind}';folder=data/label;folder.mkdir(exist_ok=True);(folder/'records.csv').write_bytes(test.BOM+encode(parts,31)+b'\r\n'+payload);(folder/'regions.csv').write_bytes(regions)
  oracle=out/'references'/label;oracle.mkdir(parents=True)
  try:ref.main(str(folder),str(oracle))
  except (ValueError,AssertionError):pass
  else:raise AssertionError('Reference unexpectedly accepted '+label)
  errors.append({'case':'round370-header-'+label,'data_folder':str(folder.relative_to(r)),'inputs_sha256':{p.name:sha(p)for p in folder.iterdir()},'expected_error':'bad records header'})
env=dict(os.environ,ASAN_OPTIONS='halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1',TSAN_OPTIONS='halt_on_error=1')
for mode,binary in [('original',Path(pre['control_binary'])),('asan',w/'native-proof/asan/track-c'),('tsan',w/'native-proof/tsan/track-c')]:
 for error,rows in [(False,bank),(True,errors)]:
  for n,row in enumerate(rows):
   for threads in [1,6,12]:
    dest=out/mode/('error-' if error else 'valid-')/(str(n)+'-'+str(threads));dest.mkdir(parents=True);q=subprocess.run([str(binary),'--data',str(r/row['data_folder']),'--out',str(dest)],capture_output=True,text=True,env=dict(env,SPEED_DEMON_THREADS=str(threads)),timeout=90)
    assert q.returncode==(1 if error else 0)and not q.stdout,(mode,row['case'],q.returncode,q.stderr)
    trial={'mode':mode,'requested_threads':threads,'returncode':q.returncode,'binary_sha256':sha(binary)}
    if error:
     assert q.stderr.startswith('track-c: bad records header')and not any(x in q.stderr for x in ['Sanitizer','runtime error:','DEADLYSIGNAL']);trial['stderr']=q.stderr;row.setdefault('runs',[]).append(trial)
    else:
     assert not q.stderr and[p.name for p in dest.iterdir()]==['aggregates.txt'];trial['sha256']=sha(dest/'aggregates.txt');assert trial['sha256']==row['reference_sha256'];row['runs'].append(trial)
 report.update(checks=bank,expected_failures=errors);dump(out/'partial.json',report)
for row in bank+errors:assert{p.name:sha(p)for p in(r/row['data_folder']).iterdir()}==row['inputs_sha256']
for p,h in pre['source_sha256'].items():assert sha(w/'source'/p)==h
for p,h in pre['root_selected_bindings'].items():assert sha(r/p)==h
report.update(passed=True,completed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),distinct_valid_fixtures=len(bank),distinct_invalid_fixtures=len(errors),valid_calls=sum(len(x['runs'])for x in bank),normal_error_calls=sum(len(x['runs'])for x in errors))
dump(out/'report.json',report);dump(r/'docs/round370-c-header-integration.json',report);print('PASS370 actual header compatibility',report['valid_calls'],report['normal_error_calls'],flush=True)
