from pathlib import Path
import datetime,hashlib,json,os,subprocess,sys
r=Path.cwd();w=r/'.build/round315';s=w/'source';o=w/'native-main';o.mkdir(exist_ok=True);read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();pre=read(w/'source-freeze.json');report={'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'official_score':False,'source_sha256':pre['source_sha256'],'scope':'Exact C315 current main ASAN/UBSAN(no recovery) andTSAN. Full CSV/country/all-worker topology/pressure/error plus fresh untrained sample and independent forced-capacity-retry checks. Old fixtures are independent inputs/references only, never queue-protocol proof after queue removal. Full public and4 untrained full references reused without generators/oracles/training. Shared-header model is separate and required.','compiles':[],'runs':[],'full_public_untrained_runs':[]};env=dict(os.environ,ASAN_OPTIONS='halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1',TSAN_OPTIONS='halt_on_error=1',PYTHONPATH=str(r/'tools'))
def save():(o/'partial.json').write_text(json.dumps(report,indent=2)+'\n')
for rel,h in pre['source_sha256'].items():assert sha(s/rel)==h
for mode,flags in [('asan',['-fsanitize=address,undefined','-fno-sanitize-recover=all']),('tsan',['-fsanitize=thread'])]:
 folder=o/mode;folder.mkdir(exist_ok=True);binary=folder/'track-c';cmd=['clang++','-std=c++20','-O1','-g','-Wall','-Wextra','-Wpedantic','-Werror','-pthread','-fno-omit-frame-pointer',*flags,str(s/'track-c/main.cpp'),'-o',str(binary)];marker=folder/'compile.json'
 if marker.exists():d=read(marker);assert d['command']==cmd and d['returncode']==0 and d['binary_sha256']==sha(binary)
 else:
  q=subprocess.run(cmd,capture_output=True,text=True,timeout=240);d={'command':cmd,'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr};(folder/'compile-attempt.json').write_text(json.dumps(d,indent=2)+'\n');assert q.returncode==0 and not q.stdout and not q.stderr,(mode,q.returncode,q.stderr);d['binary_sha256']=sha(binary);marker.write_text(json.dumps(d,indent=2)+'\n')
 report['compiles'].append(d);save();print('PASS315 compile',mode,flush=True)
 def suite(label,cmd,path):
  if path.exists():assert read(path)['passed'];report['runs'].append({'suite':label,'command':cmd,'report':str(path.relative_to(r)),'reuse':'Exact completed source-specific stage, not rerun'});save();return
  print('RUN315',label,flush=True);q=subprocess.run(cmd,capture_output=True,text=True,env=env,timeout=1000);(o/(label+'.stdout')).write_text(q.stdout);(o/(label+'.stderr')).write_text(q.stderr);report['runs'].append({'suite':label,'command':cmd,'report':str(path.relative_to(r)),'returncode':q.returncode});save();assert q.returncode==0,(label,q.returncode,q.stdout[-1500:],q.stderr[-2500:]);assert read(path)['passed']
 seed='3413' if mode=='asan' else '3433';path=r/f'docs/round315-c-{mode}-sample.json';suite(mode+'-sample',[sys.executable,'tools/verify.py','--run-id','round315-'+mode,'--source-root',str(s),'--binary-dir',str(folder),'--tracks','c','--threads','1','6','12','--scale','sample','--seeds',seed,'--report',str(path)],path)
 path=r/f'docs/round315-c-{mode}-countries.json';code="import sys;sys.path.insert(0,'tools');import verify;verify.RUN_ID='round315-"+mode+"';import test_country_codes;test_country_codes.main()";suite(mode+'-countries',[sys.executable,'-c',code,'--binary-dir',str(folder),'--report',str(path)],path)
 for tool,label in [('test_name_pipeline.py','grammar'),('test_cooperative_pipeline.py','topology'),('test_name_ring_pressure.py','pressure')]:
  path=r/f'docs/round315-c-{mode}-{label}.json';suite(mode+'-'+label,[sys.executable,'tools/'+tool,'--binary-dir',str(folder),'--run-id','round315-'+mode+'-'+label,'--report',str(path)],path)
 path=r/f'docs/round315-c-{mode}-retry.json';cmd=[sys.executable,str(w/'retry_reference.py'),'--binary-dir',str(folder),'--run-id','round315-'+mode+'-retry','--report',str(path)]
 if mode=='tsan':cmd+=['--reference-report',str(r/'docs/round315-c-asan-retry.references.json')]
 suite(mode+'-retry',cmd,path)
full=read(r/'.build/round314/confirmation/report.json')['cases'];fresh=read(r/'docs/round314-c-fresh-confirmation.json');assert fresh['passed'];full=full+[{'case':'full-seed3407','data_folder':str(r/'.data/c/full-seed3407'),'expected_sha256':fresh['expected_sha256'],'inputs_sha256':fresh['inputs_sha256']}];binary=o/'asan/track-c'
for item in full:
 data=Path(item['data_folder']);assert {p.name:sha(p) for p in data.iterdir() if p.is_file()}==item['inputs_sha256']
 for threads in [1,6,12]:
  dest=o/'full'/item['case']/str(threads);marker=dest.parent/(str(threads)+'.json')
  if marker.exists():row=read(marker);assert row['binary_sha256']==sha(binary) and row['sha256']==item['expected_sha256']==sha(dest/'aggregates.txt')
  else:
   dest.mkdir(parents=True);q=subprocess.run([str(binary),'--data',str(data),'--out',str(dest)],capture_output=True,text=True,env=dict(env,SPEED_DEMON_THREADS=str(threads)),timeout=240);assert q.returncode==0 and not q.stdout and not q.stderr,(item['case'],threads,q.returncode,q.stderr);assert [p.name for p in dest.iterdir()]==['aggregates.txt'] and sha(dest/'aggregates.txt')==item['expected_sha256'];row={**item,'threads':threads,'sha256':item['expected_sha256'],'binary_sha256':sha(binary)};marker.write_text(json.dumps(row,indent=2)+'\n')
  report['full_public_untrained_runs'].append(row);save()
 assert {p.name:sha(p) for p in data.iterdir() if p.is_file()}==item['inputs_sha256']
for rel,h in pre['source_sha256'].items():assert sha(s/rel)==h
report.update(passed=True,completed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());(o/'report.json').write_text(json.dumps(report,indent=2)+'\n');(r/'docs/round315-c-native-main.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS315 native main source-specific strict/race/fresh/retry/full proof',flush=True)
