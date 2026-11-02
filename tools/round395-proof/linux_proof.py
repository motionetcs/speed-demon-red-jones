from pathlib import Path
import datetime,hashlib,importlib.util,json,os,shlex,subprocess,sys
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round395';s=w/'source';mode=sys.argv[1];assert mode in['gcc','build','image','defaults'];out=w/'linux-proof'/mode;out.mkdir(parents=True,exist_ok=True);out.chmod(0o777)
read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
m=read(w/'frozen.json');plan=read(w/'proof-plan.json');native=read(w/'native-proof/report.json');bank=read(w/'proof-bank.json');assert native['passed']and not(out/'report.json').exists();assert all(sha(w/p)==h for p,h in m['source_sha256'].items());assert sha(s/'Makefile')==plan['candidate_Makefile_sha256'];assert sha(w/'loader_hints_model.cpp')==plan['model_sha256'];assert sha(w/'proof-bank.json')==plan['proof_bank_sha256']
GCC='gcc:15@sha256:eb5e64286ad47187b32bda75c6b6916166ecb41da56559b8b09e0001748d2cce';tag='speed-demon-fresh/track-d:round395-loader-read-hints';common=['docker','run','--rm','--pull=never','--platform','linux/amd64','--network=none','--read-only','--memory=8g','--memory-swap=8g','--pids-limit=512','--cap-drop=ALL','--security-opt=no-new-privileges','--user','65534:65534','--tmpfs','/tmp:rw,exec,size=1g','-e','MALLOC_ARENA_MAX=2']
report={'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'official_score':False,'mode':mode,'source_sha256':m['source_sha256'],'source_manifest_sha256':sha(w/'frozen.json'),'proof_plan_sha256':sha(w/'proof-plan.json'),'native_report_sha256':sha(w/'native-proof/report.json'),'scope':'Exact395 loader read-prefetch/high-locality operands, unchanged actual addresses/atomic writes/synchronization, strict pinned offline Linux proof and one allowed nativePGO production image. Saved independent input/reference bytes are reused only by content hash; every current code replay is fresh. No Mac/emulated timing or local ELF represents organizer timing/chargedM/ELF. Actual defaults use the true entrypoint without arguments or worker override.','commands':[]}
def save():dump(out/'partial.json',report)
def run(cmd,label,stdin=None,timeout=1200):
 report['commands'].append({'label':label,'argv':list(map(str,cmd)),'script_sha256':hashlib.sha256(stdin.encode()).hexdigest()if stdin else None});save();print('RUN395',mode,label,flush=True)
 with(out/(label+'.stdout')).open('w')as stdout,(out/(label+'.stderr')).open('w')as stderr:q=subprocess.run(list(map(str,cmd)),input=stdin,text=True,stdout=stdout,stderr=stderr,timeout=timeout)
 dump(out/(label+'-attempt.json'),{'returncode':q.returncode,'stdout_path':str((out/(label+'.stdout')).relative_to(r)),'stderr_path':str((out/(label+'.stderr')).relative_to(r))});assert q.returncode==0,(mode,label,q.returncode,(out/(label+'.stderr')).read_text()[-2000:]);return(out/(label+'.stdout')).read_text()
if mode=='build':
 assert read(w/'linux-proof/gcc/report.json')['passed'];assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,11,2,14,15,tzinfo=datetime.timezone.utc)
 spec=importlib.util.spec_from_file_location('policy395',r/'tools/official/harness/dockerfile_check.py');policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy);assert not policy.check((s/'track-d/Dockerfile').read_text(),read(r/'docs/allowlist.json')['images'])
 run(['docker','build','--platform','linux/amd64','--network=none','--progress=plain','-t',tag,str(s/'track-d')],'build',timeout=600);info=json.loads(run(['docker','image','inspect',tag],'inspect'))[0];old=json.loads(run(['docker','image','inspect','sha256:2f14abcd438cafffb10cd86a0e8a7601275fa9ada765b9576eaf2cc29e0431cf'],'original-config'))[0];assert info['Architecture']=='amd64'and info['Size']<=2*1024**3
 for key in['User','Env','Entrypoint','Cmd','WorkingDir']:assert info['Config'].get(key)==old['Config'].get(key),key
 assert info['Config']['User']=='65534:65534'and info['Config']['Entrypoint']==['/app/solution']and not any(x.startswith('SPEED_DEMON_THREADS=')for x in info['Config']['Env']);elf=run([*common,'--entrypoint','sha256sum',info['Id'],'/app/solution'],'elf').split()[0]
 report.update(image_id=info['Id'],image_bytes=info['Size'],image_config=info['Config'],elf_sha256=elf,training='Unchanged byte-identical official generator full1000003 then sample130363/default12, both original -march=native PGO passes, one normal offline image build. Only executable enters runtime. Published seed1 and reference outputs are never training inputs or runtime cached answers.')
elif mode in['gcc','image']:
 image=GCC if mode=='gcc'else read(w/'linux-proof/build/report.json')['image_id'];report['image_id']=image;binary='/out/solution'if mode=='gcc'else'/app/solution';script=['set -eu','export ASAN_OPTIONS=halt_on_error=1','export UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1']
 if mode=='gcc':
  flags=['g++','-std=c++20','-O1','-g','-march=native','-Wall','-Wextra','-Wpedantic','-Werror','-pthread','-fsanitize=address,undefined','-fno-sanitize-recover=all','-fno-omit-frame-pointer']
  for label,source in [('model',w/'loader_hints_model.cpp'),('solution',s/'track-d/main.cpp')]:
   target=out/label;marker=out/(label+'.sha256')
   if marker.exists():assert sha(target)==marker.read_text().split()[0]
   else:
    assert not target.exists(),'Inspect uncheckpointed ELF before repeating compiler';script+=[shlex.join([*flags,'/repo/'+str(source.relative_to(r)),'-o','/out/'+label]),'sha256sum /out/'+label+' >/out/'+label+'.sha256.tmp','mv /out/'+label+'.sha256.tmp /out/'+label+'.sha256']
  if not(out/'model.passed').exists():script+=['/out/model >/out/model.stdout 2>/out/model.stderr','echo 0 >/out/model.passed']
  else:assert(out/'model.passed').read_text().strip()=='0'and not(out/'model.stderr').read_bytes()
 (out/'stdio').mkdir(exist_ok=True);(out/'stdio').chmod(0o777)
 for number,row in enumerate(bank['valid']):
  dest=out/('valid-'+str(number));dest.mkdir(exist_ok=True);dest.chmod(0o777);marker=out/'stdio'/(str(number)+'.code')
  if marker.exists():assert marker.read_text().strip()=='0'and sha(dest/'distances.txt')==row['expected_sha256'];continue
  cmd=['env','SPEED_DEMON_THREADS='+str(row['threads']),binary,'--data','/repo/'+row['data_folder'],'--out','/out/'+dest.name];script+=['set +e',shlex.join(cmd)+' >/out/stdio/'+str(number)+'.out 2>/out/stdio/'+str(number)+'.err','code=$?','set -e','echo "$code" >/out/stdio/'+str(number)+'.code','test "$code" -eq 0']
 for number,row in enumerate(bank['errors']):
  dest=out/('error-'+str(number));dest.mkdir(exist_ok=True);dest.chmod(0o777);marker=out/'stdio'/('error-'+str(number)+'.code')
  if marker.exists():assert marker.read_text().strip()=='1';continue
  cmd=['env','SPEED_DEMON_THREADS='+str(row['threads']),binary,'--data','/repo/'+row['data_folder'],'--out','/out/'+dest.name];script+=['set +e',shlex.join(cmd)+' >/out/stdio/error-'+str(number)+'.out 2>/out/stdio/error-'+str(number)+'.err','code=$?','set -e','echo "$code" >/out/stdio/error-'+str(number)+'.code','test "$code" -eq 1']
 payload='\n'.join(script)+'\n';(out/'replay.sh').write_text(payload);run([*common,'-i','--entrypoint','/bin/sh','-v',str(r)+':/repo:ro','-v',str(out)+':/out:rw',image,'-s'],'replay',payload,timeout=1200);assert not(out/'replay.stderr').read_bytes();assert not(out/'replay.stdout').read_bytes()
 valid=[];errors=[]
 for number,row in enumerate(bank['valid']):
  assert(out/'stdio'/(str(number)+'.code')).read_text().strip()=='0'and not(out/'stdio'/(str(number)+'.out')).read_bytes()and not(out/'stdio'/(str(number)+'.err')).read_bytes();assert sorted(p.name for p in(out/('valid-'+str(number))).iterdir())==['distances.txt'];h=sha(out/('valid-'+str(number))/'distances.txt');assert h==row['expected_sha256'];valid.append({**row,'sha256':h})
 for number,row in enumerate(bank['errors']):
  err=(out/'stdio'/('error-'+str(number)+'.err')).read_text();assert(out/'stdio'/('error-'+str(number)+'.code')).read_text().strip()=='1'and not(out/'stdio'/('error-'+str(number)+'.out')).read_bytes()and err.startswith('track-d:')and not any(x in err for x in['Sanitizer','runtime error:','DEADLYSIGNAL']);errors.append({**row,'stderr':err})
 report.update(runs=valid,expected_failures=errors)
 if mode=='gcc':
  assert(out/'model.passed').read_text().strip()=='0'and not(out/'model.stderr').read_bytes();report.update(compiled_binary_sha256=sha(out/'solution'),model_binary_sha256=sha(out/'model'),model_stdout=(out/'model.stdout').read_text())
else:
 built=read(w/'linux-proof/build/report.json');assert read(w/'linux-proof/image/report.json')['passed'];image=built['image_id'];report['image_id']=image
 suffixes=['public-full-seed1','full-seed3473','sample-seed3467','sample-seed3469','sample-seed3481','d-worked','d-sparse-large-id-weight-boundaries','d-wide-id-weight-boundaries','d-degree-cursor-65535','d-degree-cursor-65536','d-wide-id-large-degree','d-degree-spills-wide-out','d-degree-spills-wide-in','d-empty-queries','d-long-chain-reused-workspaces','query-budget-0','query-budget-1','query-budget-13','query-budget-25','empty-graph','d-pipeline-spread-batch-65544']
 chosen={}
 for suffix in suffixes:
  options=[row for row in bank['valid']if row['case'].endswith(suffix)];assert options,suffix;row=options[0];chosen[tuple(sorted(row['inputs_sha256'].items()))]=row
 runs=[]
 for number,row in enumerate(chosen.values()):
  dest=out/('default-'+str(number));dest.mkdir(exist_ok=True);dest.chmod(0o777);marker=dest/'pass.json'
  if marker.exists():done=read(marker);assert done['image_id']==image and sha(dest/'distances.txt')==row['expected_sha256'];runs.append(done);continue
  assert not(dest/'distances.txt').exists(),'Inspect completed uncheckpointed invocation instead of repeating it';cmd=[*common,'-v',str((r/row['data_folder']).resolve())+':/data:ro','-v',str(dest)+':/out:rw',image];run(cmd,'default-'+str(number),timeout=180);assert not(out/('default-'+str(number)+'.stdout')).read_bytes()and not(out/('default-'+str(number)+'.stderr')).read_bytes();assert sorted(p.name for p in dest.iterdir())==['distances.txt'];assert sha(dest/'distances.txt')==row['expected_sha256'];done={**row,'threads':None,'true_default12':True,'arguments':[],'worker_env_override':False,'entrypoint_override':False,'image_id':image,'sha256':row['expected_sha256']};dump(marker,done);runs.append(done)
 report['runs']=runs;report['scope']+=' Content-deduplicated21 chosen default configurations, actual executed count recorded; not every earlier topology is a distinct default case.'
for p,h in bank['folders'].items():assert {q.name:sha(q)for q in(r/p).iterdir()if q.is_file()}==h,p
assert all(sha(w/p)==h for p,h in m['source_sha256'].items());assert sha(s/'Makefile')==plan['candidate_Makefile_sha256'];report.update(passed=True,completed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());dump(out/'report.json',report);dump(r/('docs/round395-d-linux-'+mode+'.json'),report);print('PASS395 Linux',mode,len(report.get('runs',[])),len(report.get('expected_failures',[])),flush=True)
