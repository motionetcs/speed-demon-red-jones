from pathlib import Path
import datetime,hashlib,json,os,subprocess
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round395';s=w/'source';out=w/'native-proof';out.mkdir(exist_ok=True);read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();m=read(w/'frozen.json');plan=read(w/'proof-plan.json');bank=read(w/'proof-bank.json');assert not(out/'report.json').exists()
report={'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'official_score':False,'scope':plan['scope'],'source_sha256':m['source_sha256'],'model_sha256':sha(w/'loader_hints_model.cpp'),'proof_plan_sha256':sha(w/'proof-plan.json'),'modes':{}}
def dump(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
def save():dump(out/'partial.json',report)
def verify_inputs():
 assert all(sha(w/p)==h for p,h in m['source_sha256'].items());assert all(sha(r/p)==h for p,h in m['root_inputs_sha256'].items());assert sha(s/'Makefile')==plan['candidate_Makefile_sha256'];assert sha(w/'proof-bank.json')==plan['proof_bank_sha256'];assert sha(w/'loader_hints_model.cpp')==plan['model_sha256']
verify_inputs();env=dict(os.environ,ASAN_OPTIONS='halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1',TSAN_OPTIONS='halt_on_error=1')
for mode,flags in [('asan',['-fsanitize=address,undefined','-fno-sanitize-recover=all']),('tsan',['-fsanitize=thread'])]:
 folder=out/mode;folder.mkdir(exist_ok=True);state={'compiles':[],'runs':[],'errors':[]};report['modes'][mode]=state;save()
 common=['clang++','-std=c++20','-O1','-g','-Wall','-Wextra','-Wpedantic','-Werror','-pthread','-fno-omit-frame-pointer',*flags]
 for label,source in [('model',w/'loader_hints_model.cpp'),('track-d',s/'track-d/main.cpp')]:
  binary=folder/label;marker=folder/(label+'-compile.json');cmd=[*common,str(source),'-o',str(binary)]
  if marker.exists():compiled=read(marker);assert compiled['returncode']==0 and compiled['command']==cmd and sha(binary)==compiled['binary_sha256']
  else:
   assert not binary.exists(),'Inspect uncheckpointed existing ELF instead of repeating compiler';q=subprocess.run(cmd,capture_output=True,text=True,timeout=240);compiled={'command':cmd,'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr};dump(folder/(label+'-compile-attempt.json'),compiled);assert q.returncode==0 and not q.stdout and not q.stderr,q.stderr;compiled['binary_sha256']=sha(binary);dump(marker,compiled)
  state['compiles'].append(compiled);save()
  if label=='model':
   marker=folder/'model-pass.json'
   if marker.exists():model=read(marker);assert model['passed']and model['binary_sha256']==sha(binary)
   else:
    q=subprocess.run([str(binary)],capture_output=True,text=True,env=env,timeout=300);model={'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr,'binary_sha256':sha(binary)};dump(folder/'model-run-attempt.json',model);assert q.returncode==0 and not q.stderr,(mode,q.stdout[-1000:],q.stderr[-2000:]);model['passed']=True;dump(marker,model)
   state['model']=model;save();print('PASS395',mode,'actual-header loader models',flush=True)
 binary=folder/'track-d';binary_hash=sha(binary)
 jobs=[row for row in bank['valid']if mode!='tsan' or 'full-'not in row['case']or(row['case']in['public-full-seed1','full-seed3473']and row['threads']==12)]
 for number,row in enumerate(jobs):
  dest=folder/('valid-'+str(number));marker=dest/'pass.json'
  if marker.exists():done=read(marker);assert done['binary_sha256']==binary_hash and done['expected_sha256']==row['expected_sha256']==sha(dest/'distances.txt');state['runs'].append(done);continue
  dest.mkdir(parents=True,exist_ok=True);q=subprocess.run([str(binary),'--data',str(r/row['data_folder']),'--out',str(dest)],capture_output=True,text=True,env=dict(env,SPEED_DEMON_THREADS=str(row['threads'])),timeout=180);(dest/'stdout').write_text(q.stdout);(dest/'stderr').write_text(q.stderr);assert q.returncode==0 and not q.stdout and not q.stderr,(mode,row['case'],row['threads'],q.returncode,q.stderr[-2000:]);assert sha(dest/'distances.txt')==row['expected_sha256'];done={**row,'binary_sha256':binary_hash,'sha256':row['expected_sha256'],'returncode':0};dump(marker,done);state['runs'].append(done);save()
 for number,row in enumerate(bank['errors']):
  dest=folder/('error-'+str(number));marker=dest/'pass.json'
  if marker.exists():done=read(marker);assert done['binary_sha256']==binary_hash and done['returncode']==1;state['errors'].append(done);continue
  dest.mkdir(parents=True,exist_ok=True);q=subprocess.run([str(binary),'--data',str(r/row['data_folder']),'--out',str(dest)],capture_output=True,text=True,env=dict(env,SPEED_DEMON_THREADS=str(row['threads'])),timeout=90);(dest/'stdout').write_text(q.stdout);(dest/'stderr').write_text(q.stderr);assert q.returncode==1 and not q.stdout and q.stderr.startswith('track-d:')and not any(x in q.stderr for x in ['Sanitizer','runtime error:','DEADLYSIGNAL']),(mode,row,q.returncode,q.stderr);done={**row,'binary_sha256':binary_hash,'returncode':1,'stderr':q.stderr};dump(marker,done);state['errors'].append(done);save()
 state['passed']=True;save();print('PASS395',mode,'exact main',len(state['runs']),'valid',len(state['errors']),'normalerrors',flush=True)
for p,h in bank['folders'].items():assert {q.name:sha(q)for q in(r/p).iterdir()if q.is_file()}==h,p
verify_inputs();report.update(passed=True,completed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());dump(out/'report.json',report);dump(r/'docs/round395-d-native-proof.json',report);print('PASS395 native strict/race proof complete; pinnedGNU/image/defaults still required',flush=True)
