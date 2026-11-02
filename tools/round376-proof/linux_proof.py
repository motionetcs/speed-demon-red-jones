from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,shlex,subprocess
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round376';s=w/'source'
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,j):p.write_text(json.dumps(j,indent=2)+'\n')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['gnu','build','image','defaults']);mode=parser.parse_args().mode;out=w/'proof'/mode;out.mkdir(parents=True,exist_ok=True);out.chmod(0o777);assert not(out/'report.json').exists()
pre=read(w/'preflight.json');native=read(w/'native-proof/report.json');assert native['passed'];assert native['source_sha256']==pre['source_sha256']
for p,h in pre['source_sha256'].items():assert sha(s/p)==h,p
for p,h in pre['root_selected_bindings'].items():assert sha(r/p)==h,p
report={'started_at_utc':now(),'mode':mode,'track':'a','official_score':False,'selected_in_root':False,'source_sha256':pre['source_sha256'],'scope':pre['scope'],'commands':[]}
def command(argv,label,stdin=None,timeout=1800):
 argv=list(map(str,argv));assert not(out/(label+'.code')).exists(),'Never repeat completed command '+label;record={'label':label,'argv':argv,'stdin':stdin};report['commands'].append(record);dump(out/'partial.json',report);print('RUN376',mode,label,flush=True)
 with(out/(label+'.stdout')).open('w')as a,(out/(label+'.stderr')).open('w')as b:q=subprocess.run(argv,input=stdin,text=True,stdout=a,stderr=b,timeout=timeout)
 (out/(label+'.code')).write_text(str(q.returncode)+'\n');record['returncode']=q.returncode;dump(out/'partial.json',report);assert q.returncode==0,(label,q.returncode,(out/(label+'.stderr')).read_text()[-2500:]);return(out/(label+'.stdout')).read_text()
compiler='gcc:15@sha256:eb5e64286ad47187b32bda75c6b6916166ecb41da56559b8b09e0001748d2cce';tag='speed-demon-fresh/track-a:round376-dynamic4m';common=['docker','run','--rm','--pull=never','--platform','linux/amd64','--network=none','--read-only','--memory=8g','--memory-swap=8g','--pids-limit=512','--cap-drop=ALL','--security-opt=no-new-privileges','--user','65534:65534','--tmpfs','/tmp:rw,exec,size=1g']
if mode=='build':
 assert read(w/'proof/gnu/report.json')['passed'];assert sha(s/'track-a/training_generator.py')==sha(r/'tools/official/generators/a_ingest.py');spec=importlib.util.spec_from_file_location('policy376',r/'tools/official/harness/dockerfile_check.py');policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy);assert not policy.check((s/'track-a/Dockerfile').read_text(),read(r/'docs/allowlist.json')['images'])
 command(['docker','build','--platform','linux/amd64','--network=none','--pull=false','-t',tag,s/'track-a'],'build');info=json.loads(command(['docker','image','inspect',tag],'inspect'))[0];prior=read(r/'docs/round371-final-source-match.json');original=json.loads(command(['docker','image','inspect',prior['images']['a']],'original-config'))[0]
 for key in ['User','Env','Entrypoint','Cmd','WorkingDir']:assert info['Config'].get(key)==original['Config'].get(key),key
 assert info['Architecture']=='amd64'and info['Size']<=2*1024**3 and info['Config']['User']=='65534:65534'and info['Config']['Entrypoint']==['/app/solution'];elf=command([*common,'--entrypoint','sha256sum',info['Id'],'/app/solution'],'elf').split()[0];report.update(image_id=info['Id'],image_tag=tag,image_bytes=info['Size'],elf_sha256=elf,image_config=info['Config'],training='One unchanged generic/static -O3 A PGO full1000003 then sample130363/default12, byte-identical official generator. No publicseed1 or validation data trained; only executable in final image. Local image/ELF identity, not organizer identity.')
else:
 jobs={};folders={};origins=[]
 def add(row,origin):
  data=r/row['data_folder'];hashes={p.name:sha(p)for p in data.iterdir()if p.is_file()};assert hashes==row['inputs_sha256']and set(hashes)=={'requests.log'};key=(tuple(sorted(hashes.items())),int(row['threads']));item={k:row[k]for k in ['case','data_folder','threads','inputs_sha256','expected_sha256']};item['reference_source']=origin
  if key in jobs:assert jobs[key]['expected_sha256']==item['expected_sha256']
  jobs[key]=item;folders[str(data)]=hashes
 for matrix in native['matrices']:
  path=r/matrix['path'];assert sha(path)==matrix['sha256'];x=read(path);assert x['passed'];origins.append({'path':matrix['path'],'sha256':sha(path),'scope':'Only saved input/reference bytes, not native-source execution proof'})
  for row in x['runs']:add(row,matrix['path'])
 for suite in native['fresh_suites']:
  path=r/suite['path'];assert sha(path)==suite['sha256'];x=read(path);assert x['passed'];origins.append({'path':suite['path'],'sha256':sha(path),'scope':'Only independently generated reference/input bytes, not repeated generator/oracle'})
  for row in x['checks']:
   data=next(p for p in[r/'.data/a'/row['case'],r/'.data/cases'/row['case']]if p.is_dir());inputs={p.name:sha(p)for p in data.iterdir()if p.is_file()}
   for trial in row['runs']:add({'case':row['case'],'data_folder':str(data.relative_to(r)),'threads':trial['requested_threads'],'inputs_sha256':inputs,'expected_sha256':row.get('reference_sha256')or trial['sha256']},suite['path'])
 alljobs=list(jobs.values());fixtures=read(w/'dynamic-fixtures/report.json');errors=[{'case':name,'data_folder':fixtures['invalid'if name=='late-invalid'else'empty']['data_folder'],'inputs_sha256':fixtures['invalid'if name=='late-invalid'else'empty']['inputs_sha256'],'threads':threads}for name in ['late-invalid','output-open']for threads in [1,6,12]];report['reference_inputs']=origins;report['content_thread_deduplication']=True
 if mode=='gnu':jobs=[x for x in alljobs if x['threads']in[1,6,12]];image=compiler
 else:assert read(w/'proof/build/report.json')['passed'];jobs=alljobs;image=read(w/'proof/build/report.json')['image_id']
 report['image_id']=image
 if mode=='defaults':
  assert read(w/'proof/image/report.json')['passed'];unique={tuple(sorted(x['inputs_sha256'].items())):dict(x)for x in jobs};jobs=list(unique.values());errors=[dict(x)for x in errors if x['threads']==12];runs=[];failures=[]
  for n,row in enumerate(jobs):
   dest=out/f'valid-{n}';dest.mkdir();dest.chmod(0o777);command([*common,'-v',str(r/row['data_folder'])+':/data:ro','-v',str(dest)+':/out:rw',image],'default-'+str(n),timeout=180);assert not(out/f'default-{n}.stdout').read_bytes()and not(out/f'default-{n}.stderr').read_bytes();assert[p.name for p in dest.iterdir()]==['summary.txt'];row['sha256']=sha(dest/'summary.txt');assert row['sha256']==row['expected_sha256'];row['source_fixture_threads']=row.pop('threads');row['true_ENTRYPOINT_noargs_no_thread_override_default12']=True;runs.append(row);report['runs']=runs;dump(out/'partial.json',report)
  for n,row in enumerate(errors):
   dest=out/f'error-{n}';dest.mkdir();dest.chmod(0o777)
   if row['case']=='output-open':(dest/'summary.txt').mkdir();(dest/'summary.txt').chmod(0o777)
   q=subprocess.run([*common,'-v',str(r/row['data_folder'])+':/data:ro','-v',str(dest)+':/out:rw',image],capture_output=True,text=True,timeout=180);assert q.returncode==1 and not q.stdout and q.stderr.startswith('track-a:')and not any(x in q.stderr for x in ['Sanitizer','runtime error:','DEADLYSIGNAL']);row['stderr']=q.stderr;row['true_ENTRYPOINT_noargs_no_thread_override_default12']=True;failures.append(row)
  report.update(runs=runs,expected_failures=failures)
 else:
  script=['set -eu','mkdir -p /out/stdio','export ASAN_OPTIONS=halt_on_error=1','export UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1'];binary='/app/solution'
  if mode=='gnu':
   flags='g++ -std=c++20 -O3 -g -Wall -Wextra -Wpedantic -Werror -pthread -fsanitize=address,undefined -fno-sanitize-recover=all -fno-omit-frame-pointer ';script+=['g++ --version >/out/gcc.txt',flags+'/repo/.build/round376/partitions_model.cpp -o /out/partition-model','/out/partition-model >/out/model.stdout 2>/out/model.stderr',flags+'/repo/.build/round376/source/track-a/main.cpp -o /out/solution','sha256sum /out/solution >/out/solution.sha256'];binary='/out/solution';report['strict_flags']=flags;report['model_manifest_sha256']=sha(w/'partition-model-manifest.json')
  for n,row in enumerate(jobs):script+=['set +e','SPEED_DEMON_THREADS='+str(row['threads'])+' '+binary+' --data '+shlex.quote('/repo/'+row['data_folder'])+' --out /out/valid-'+str(n)+' >/out/stdio/'+str(n)+'.out 2>/out/stdio/'+str(n)+'.err','code=$?','set -e','echo "$code" >/out/stdio/'+str(n)+'.code','test "$code" -eq 0']
  for n,row in enumerate(errors):
   if row['case']=='output-open':script+=['mkdir -p /out/error-'+str(n)+'/summary.txt']
   script+=['set +e','SPEED_DEMON_THREADS='+str(row['threads'])+' '+binary+' --data '+shlex.quote('/repo/'+row['data_folder'])+' --out /out/error-'+str(n)+' >/out/stdio/error-'+str(n)+'.out 2>/out/stdio/error-'+str(n)+'.err','code=$?','set -e','echo "$code" >/out/stdio/error-'+str(n)+'.code','test "$code" -eq 1']
  text='\n'.join(script)+'\n';(out/'executed.sh').write_text(text);command([*common,'-i','--entrypoint','/bin/sh','-v',str(r)+':/repo:ro','-v',str(out)+':/out:rw',image,'-s'],'replay',text);assert not(out/'replay.stderr').read_bytes(),(out/'replay.stderr').read_text()[-2000:]
  for n,row in enumerate(jobs):
   dest=out/f'valid-{n}';assert[p.name for p in dest.iterdir()]==['summary.txt'];assert(out/'stdio'/f'{n}.code').read_text().strip()=='0'and not(out/'stdio'/f'{n}.out').read_bytes()and not(out/'stdio'/f'{n}.err').read_bytes();row['sha256']=sha(dest/'summary.txt');assert row['sha256']==row['expected_sha256'],row['case']
  for n,row in enumerate(errors):
   assert(out/'stdio'/f'error-{n}.code').read_text().strip()=='1'and not(out/'stdio'/f'error-{n}.out').read_bytes();err=(out/'stdio'/f'error-{n}.err').read_text();assert err.startswith('track-a:')and not any(x in err for x in ['Sanitizer','runtime error:','DEADLYSIGNAL']);row['stderr']=err
  if mode=='gnu':assert(out/'model.stdout').read_text().startswith('PASS376')and not(out/'model.stderr').read_bytes();report['model_stdout']=(out/'model.stdout').read_text();report['compiler_version']=(out/'gcc.txt').read_text();report['compiled_binary_sha256']=sha(out/'solution')
  report.update(runs=jobs,expected_failures=errors)
 for folder,hashes in folders.items():assert{p.name:sha(p)for p in Path(folder).iterdir()if p.is_file()}==hashes
for p,h in pre['source_sha256'].items():assert sha(s/p)==h,p
for p,h in pre['root_selected_bindings'].items():assert sha(r/p)==h,p
report.update(passed=True,completed_at_utc=now());dump(out/'report.json',report);dump(r/f'docs/round376-a-{mode}-proof.json',report);print('PASS376',mode,len(report.get('runs',[])),len(report.get('expected_failures',[])),flush=True)
