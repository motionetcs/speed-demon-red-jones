from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,os,shlex,subprocess
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round391';s=w/'source';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();read=lambda p:json.loads(Path(p).read_text());dump=lambda p,x:Path(p).write_text(json.dumps(x,indent=2)+'\n');pre=read(w/'preflight.json');parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['native','gcc','build','image','defaults']);mode=parser.parse_args().mode;out=w/'proof'/mode;out.mkdir(parents=True,exist_ok=True);out.chmod(0o777);assert not(out/'report.json').exists(),'Never repeat completed mode'
for p,h in pre['source_sha256'].items():assert sha(s/p)==h
for p,h in pre['root_selected_bindings'].items():assert sha(r/p)==h
for p,h in pre['unchanged_A_cpp_sha256'].items():assert sha(s/p)==sha(r/p)==h
report={'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'official_score':False,'selected_in_root':False,'mode':mode,'track':'a','source_sha256':pre['source_sha256'],'unchanged_A_cpp_sha256':pre['unchanged_A_cpp_sha256'],'scope':pre['scope'],'commands':[]}
def save():dump(out/'partial.json',report)
def command(argv,label,stdin=None,timeout=1200):
 record={'label':label,'argv':list(map(str,argv)),'stdin':stdin};report['commands'].append(record);save();code=out/(label+'.code')
 if code.exists():assert code.read_text().strip()=='0';record.update(returncode=0,resumed_completed_command=True);return(out/(label+'.stdout')).read_text()
 print('RUN391',mode,label,flush=True)
 with(out/(label+'.stdout')).open('w')as a,(out/(label+'.stderr')).open('w')as b:q=subprocess.run(record['argv'],input=stdin,text=True,stdout=a,stderr=b,timeout=timeout)
 code.write_text(str(q.returncode)+'\n');record['returncode']=q.returncode;save();assert q.returncode==0,(label,q.returncode,(out/(label+'.stderr')).read_text()[-2500:]);return(out/(label+'.stdout')).read_text()
def inventory():
 jobs={};errors={};folders={};expected={}
 sources=[('docs/round343-a-linux-image.json','runs','expected_failures'),('docs/round376-a-image-proof.json','runs','expected_failures'),('.build/round376/native-proof/asan/matrix.json','runs','expected_failures'),('.build/round376/native-proof/tsan/matrix.json','runs','expected_failures')]
 for path,validkey,errkey in sources:
  bank=read(r/path);assert bank['passed']
  for error,rows in[(False,bank[validkey]),(True,bank.get(errkey,[]))]:
   for original in rows:
    row={k:v for k,v in original.items()if k in['case','data_folder','inputs_sha256','expected_sha256']};data=(r/row['data_folder']).resolve();data.relative_to(r);hashes={p.name:sha(p)for p in data.iterdir()if p.is_file()};assert hashes==row['inputs_sha256']and set(hashes)=={'requests.log'};content=tuple(sorted(hashes.items()));folders[str(data)]=hashes;row['data_folder']=str(data.relative_to(r));row['threads']=8;row['reference_source']=path+' input/expected bytes ONLY; no rejected source proof'
    if error:errors[content]=row
    else:
     assert row['expected_sha256']
     if content in expected:assert expected[content]==row['expected_sha256']
     expected[content]=row['expected_sha256'];jobs[content]=row
 for case in read(w/'report.json')['cases']:
  data=Path(case['data_folder']);hashes={p.name:sha(p)for p in data.iterdir()if p.is_file()};assert hashes==case['inputs_sha256'];content=tuple(sorted(hashes.items()));folders[str(data)]=hashes;row={k:case[k]for k in['case','inputs_sha256','expected_sha256']};row.update(data_folder=str(data.relative_to(r)),threads=8,reference_source=case['reference_source']);assert content not in expected or expected[content]==row['expected_sha256'];expected[content]=row['expected_sha256'];jobs[content]=row
 return list(jobs.values()),list(errors.values()),folders
GCC='gcc:15@sha256:eb5e64286ad47187b32bda75c6b6916166ecb41da56559b8b09e0001748d2cce';common=['docker','run','--rm','--pull=never','--platform','linux/amd64','--network=none','--read-only','--memory=8g','--memory-swap=8g','--pids-limit=512','--cap-drop=ALL','--security-opt=no-new-privileges','--user','65534:65534','--tmpfs','/tmp:rw,exec,size=1g']
if mode=='build':
 assert read(w/'proof/native/report.json')['passed']and read(w/'proof/gcc/report.json')['passed'];original_df=(r/'track-a/Dockerfile').read_text();candidate_df=(s/'track-a/Dockerfile').read_text();assert candidate_df==original_df.replace('USER 65534:65534\nENTRYPOINT','USER 65534:65534\nENV SPEED_DEMON_THREADS=8\nENTRYPOINT');assert candidate_df.split('\nFROM debian:')[0]==original_df.split('\nFROM debian:')[0];assert sha(s/'track-a/training_generator.py')==sha(r/'tools/official/generators/a_ingest.py')
 spec=importlib.util.spec_from_file_location('policy391',r/'tools/official/harness/dockerfile_check.py');policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy);assert not policy.check(candidate_df,read(r/'docs/allowlist.json')['images']);tag='speed-demon-fresh/track-a:round391-runtime8';command(['docker','build','--pull=false','--platform','linux/amd64','--network=none','--progress=plain','-t',tag,str(s/'track-a')],'build',timeout=900);info=json.loads(command(['docker','image','inspect',tag],'inspect'))[0];original=json.loads(command(['docker','image','inspect',pre['original_image_id']],'original-config'))[0];assert info['Architecture']=='amd64'and info['Size']<=2*1024**3
 for key in['User','Entrypoint','Cmd','WorkingDir']:assert info['Config'].get(key)==original['Config'].get(key),key
 assert not any(x.startswith('SPEED_DEMON_THREADS=')for x in original['Config']['Env']);assert info['Config']['Env']==original['Config']['Env']+['SPEED_DEMON_THREADS=8'];elf=command([*common,'--entrypoint','sha256sum',info['Id'],'/app/solution'],'elf').split()[0];oldelf=command([*common,'--entrypoint','sha256sum',pre['original_image_id'],'/app/solution'],'original-elf').split()[0];logs=(out/'build.stdout').read_text()+(out/'build.stderr').read_text();report.update(image_id=info['Id'],image_tag=tag,image_bytes=info['Size'],elf_sha256=elf,original_image_id=pre['original_image_id'],original_elf_sha256=oldelf,elf_equals_original=elf==oldelf,image_config=info['Config'],cache_observation='See exact BuildKit logs; CACHED lines identify actual reused instructions, never inferred compilation. '+('Exact executable equals cached original.'if elf==oldelf else'Executable differs; no unchanged-ELF claim.'),training='Build-stage Dockerfile/official generator/C++/flags exact original GENERIC recipe: full1000003 then sample130363, nativefallback12/default12 build training; final ENV8 only. Source and exact build receipts preserved; public1 never trained. Only executable enters allowlisted finalbase.')
else:
 jobs,errors,folders=inventory();report.update(reference_content_deduplication=True,input_cases=len(jobs),normal_error_cases=len(errors))
 if mode=='native':
  report['matrices']=[];env=dict(os.environ,ASAN_OPTIONS='halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1',TSAN_OPTIONS='halt_on_error=1',SPEED_DEMON_THREADS='8')
  for kind in['asan','tsan']:
   binding=pre['native_strict'][kind];binary=r/binding['binary'];assert sha(binary)==binding['binary_sha256'];doc=read(r/binding['report']);assert doc['passed']and all(doc['source_sha256'].get(p)==h for p,h in pre['unchanged_A_cpp_sha256'].items());folder=out/kind;folder.mkdir(exist_ok=True);matrix={'mode':kind,'requested_threads':8,'binary':binding['binary'],'binary_sha256':sha(binary),'cached_source_binding':binding,'runs':[],'expected_failures':[],'scope':'FRESH requested8 executions of cached exact original178 C++/headers binary; no new compile/model/generator/reference, no former source proof substitution.'}
   for error,rows in[(False,jobs),(True,errors)]:
    for n,row in enumerate(rows):
     label=('error-'if error else'valid-')+str(n);dest=folder/label;marker=folder/(label+'.json')
     if marker.exists():trial=read(marker);assert trial['inputs_sha256']==row['inputs_sha256'];assert error or sha(dest/'summary.txt')==row['expected_sha256']==trial['sha256']
     else:
      dest.mkdir();q=subprocess.run([str(binary),'--data',str(r/row['data_folder']),'--out',str(dest)],capture_output=True,text=True,env=env,timeout=180);assert q.returncode==(1 if error else 0)and not q.stdout,(kind,row['case'],q.returncode,q.stderr[-1500:]);trial=dict(row)
      if error:assert q.stderr.startswith('track-a:')and not any(x in q.stderr for x in['Sanitizer','runtime error:','DEADLYSIGNAL']);trial['stderr']=q.stderr
      else:assert not q.stderr and[p.name for p in dest.iterdir()]==['summary.txt'];trial['sha256']=sha(dest/'summary.txt');assert trial['sha256']==row['expected_sha256']
      dump(marker,trial)
     matrix['expected_failures'if error else'runs'].append(trial)
   matrix['passed']=True;dump(folder/'matrix.json',matrix);report['matrices'].append({'mode':kind,'path':str((folder/'matrix.json').relative_to(r)),'sha256':sha(folder/'matrix.json'),'valid_calls':len(jobs),'normal_errors':len(errors)});save();print('PASS391 cached native',kind,len(jobs),len(errors),flush=True)
 elif mode=='gcc':
  assert read(w/'proof/native/report.json')['passed'];g=pre['gnu_strict'];binary=r/g['binary'];assert sha(binary)==g['binary_sha256'];report['cached_binary_binding']=g;image=GCC
  script=['set -eu','mkdir -p /out/stdio','export ASAN_OPTIONS=halt_on_error=1','export UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1'];command_path='/repo/'+g['binary']
  for error,rows in[(False,jobs),(True,errors)]:
   for n,row in enumerate(rows):
    label=('error-'if error else'valid-')+str(n);script+=['if ! test -f /out/stdio/'+label+'.code; then','set +e','SPEED_DEMON_THREADS=8 '+shlex.quote(command_path)+' --data '+shlex.quote('/repo/'+row['data_folder'])+' --out /out/'+label+' >/out/stdio/'+label+'.stdout 2>/out/stdio/'+label+'.stderr','code=$?','set -e','echo "$code" >/out/stdio/'+label+'.code','fi','test "$(cat /out/stdio/'+label+'.code)" -eq '+str(1 if error else 0)]
  command([*common,'-i','--entrypoint','/bin/sh','-v',str(r)+':/repo:ro','-v',str(out)+':/out:rw',image,'-s'],'replay','\n'.join(script)+'\n',timeout=1200);assert not(out/'replay.stderr').read_bytes()
  for error,rows in[(False,jobs),(True,errors)]:
   for n,row in enumerate(rows):
    label=('error-'if error else'valid-')+str(n);assert not(out/'stdio'/(label+'.stdout')).read_bytes();stderr=(out/'stdio'/(label+'.stderr')).read_text()
    if error:assert stderr.startswith('track-a:')and not any(x in stderr for x in['Sanitizer','runtime error:','DEADLYSIGNAL']);row['stderr']=stderr
    else:assert not stderr and[p.name for p in(out/label).iterdir()]==['summary.txt'];row['sha256']=sha(out/label/'summary.txt');assert row['sha256']==row['expected_sha256']
  report.update(image_id=image,runs=jobs,expected_failures=errors,compilation=False,model_reexecution=False)
 elif mode=='image':
  build=read(w/'proof/build/report.json');assert build['passed'];image=build['image_id'];report.update(image_id=image,elf_sha256=build['elf_sha256']);script=['set -eu','mkdir -p /out/stdio'];extra=[];pub=read(r/'docs/public-sha256.json')['tracks']['a'];fresh=next(x for x in jobs if x['case']=='full-seed3911')
  for row in[jobs[0],{'case':'public-full-seed1','data_folder':'.data/a/public-full-seed1','inputs_sha256':pub['inputs_sha256'],'expected_sha256':pub['expected_output_sha256'][0]},fresh]:
   for threads in[1,6,8,12]:extra.append(dict(row,threads=threads))
  unique={(tuple(sorted(x['inputs_sha256'].items())),x['threads']):x for x in jobs+extra};jobs=list(unique.values())
  for error,rows in[(False,jobs),(True,errors)]:
   for n,row in enumerate(rows):
    label=('error-'if error else'valid-')+str(n);script+=['if ! test -f /out/stdio/'+label+'.code; then','set +e','SPEED_DEMON_THREADS='+str(row['threads'])+' /app/solution --data '+shlex.quote('/repo/'+row['data_folder'])+' --out /out/'+label+' >/out/stdio/'+label+'.stdout 2>/out/stdio/'+label+'.stderr','code=$?','set -e','echo "$code" >/out/stdio/'+label+'.code','fi','test "$(cat /out/stdio/'+label+'.code)" -eq '+str(1 if error else 0)]
  command([*common,'-i','--entrypoint','/bin/sh','-v',str(r)+':/repo:ro','-v',str(out)+':/out:rw',image,'-s'],'replay','\n'.join(script)+'\n',timeout=1200);assert not(out/'replay.stderr').read_bytes()
  for error,rows in[(False,jobs),(True,errors)]:
   for n,row in enumerate(rows):
    label=('error-'if error else'valid-')+str(n);assert not(out/'stdio'/(label+'.stdout')).read_bytes();stderr=(out/'stdio'/(label+'.stderr')).read_text()
    if error:assert stderr.startswith('track-a:')and not any(x in stderr for x in['Sanitizer','runtime error:','DEADLYSIGNAL']);row['stderr']=stderr
    else:assert not stderr and[p.name for p in(out/label).iterdir()]==['summary.txt'];row['sha256']=sha(out/label/'summary.txt');assert row['sha256']==row['expected_sha256']
  report.update(runs=jobs,expected_failures=errors)
 else:
  build=read(w/'proof/build/report.json');assert build['passed']and read(w/'proof/image/report.json')['passed'];image=build['image_id'];report.update(image_id=image,configured_production_default=8,native_cli_fallback=12,argv=[],thread_override=False);runs=[];fails=[]
  for error,rows in[(False,jobs),(True,errors)]:
   for n,row in enumerate(rows):
    label=('error-'if error else'default-')+str(n);dest=out/label;dest.mkdir(exist_ok=True);dest.chmod(0o777);marker=out/(label+'.json')
    if marker.exists():trial=read(marker)
    else:
     argv=[*common,'-v',str(r/row['data_folder'])+':/data:ro','-v',str(dest)+':/out:rw',image];q=subprocess.run(argv,capture_output=True,text=True,timeout=180);trial={'argv':argv,'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr,'inputs_sha256':row['inputs_sha256']};dump(marker,trial)
    assert trial['returncode']==(1 if error else 0)and not trial['stdout'],(label,trial)
    if error:assert trial['stderr'].startswith('track-a:')and not any(x in trial['stderr']for x in['Sanitizer','runtime error:','DEADLYSIGNAL']);fails.append(dict(row,stderr=trial['stderr']))
    else:assert not trial['stderr']and[p.name for p in dest.iterdir()]==['summary.txt'];actual=sha(dest/'summary.txt');assert actual==row['expected_sha256'];runs.append(dict(row,sha256=actual))
    if n%10==0:report.update(runs=runs,expected_failures=fails);save()
  report.update(runs=runs,expected_failures=fails);sinks=[]
  for number,row in enumerate([next(x for x in jobs if x['case']=='public-full-seed1'),fresh if 'fresh'in locals()else next(x for x in jobs if x['case']=='full-seed3911')]):
   dest=out/f'sink-{number}';dest.mkdir(exist_ok=True);dest.chmod(0o777);link=dest/'summary.txt'
   if not link.is_symlink():link.symlink_to('/dev/full')
   argv=[*common,'-v',str(r/row['data_folder'])+':/data:ro','-v',str(dest)+':/out:rw',image];q=subprocess.run(argv,capture_output=True,text=True,timeout=180);assert q.returncode==1 and not q.stdout and q.stderr.startswith('track-a:')and not any(x in q.stderr for x in['Sanitizer','runtime error:','DEADLYSIGNAL']);sinks.append({'case':row['case'],'argv':argv,'returncode':q.returncode,'stderr':q.stderr,'true_ENTRYPOINT_noargs_nooverride_default8':True})
  report['expected_sink_failures']=sinks
 for data,hashes in folders.items():assert{p.name:sha(p)for p in Path(data).iterdir()if p.is_file()}==hashes
for p,h in pre['source_sha256'].items():assert sha(s/p)==h
for p,h in pre['root_selected_bindings'].items():assert sha(r/p)==h
report.update(passed=True,completed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());dump(out/'report.json',report);dump(r/f'docs/round391-a-{mode}-proof.json',report);print('PASS391',mode,len(report.get('runs',[])),len(report.get('expected_failures',[])),flush=True)
