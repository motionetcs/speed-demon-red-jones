from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,os,shlex,subprocess
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round384';s=w/'source';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();read=lambda p:json.loads(Path(p).read_text());dump=lambda p,x:Path(p).write_text(json.dumps(x,indent=2)+'\n');pre=read(w/'final-source.json');parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['gcc','build','image','defaults']);mode=parser.parse_args().mode;out=w/'proof'/mode;out.mkdir(parents=True,exist_ok=True);out.chmod(0o777);assert not(out/'report.json').exists(),'Do not repeat completed stage';assert read(w/'native-proof/report.json')['passed']
for p,h in pre['source_sha256'].items():assert sha(s/p)==h
for p,h in pre['root_selected_bindings'].items():assert sha(r/p)==h
report={'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'mode':mode,'official_score':False,'selected_in_root':False,'source_sha256':pre['source_sha256'],'manifest_sha256':sha(w/'final-source.json'),'scope':'New exact-final384 pinned offline GNU strict model/main, one unchanged allowed native PGO production image, exact-image bank/default replays. Source-independent saved reference/data bytes ONLY from370 plus fresh384 independent+official country fixtures/native matrix. No old runtime proof substitution; no generator/oracle/PGO repetition, publicseed1 never trained. Local replay image/ELF identities are not organizer binaries.','commands':[]}
def save():dump(out/'partial.json',report)
def cmd(argv,label,stdin=None,timeout=1200):
 row={'label':label,'argv':list(map(str,argv)),'stdin':stdin};report['commands'].append(row);save();code=out/(label+'.code')
 if code.exists():assert code.read_text().strip()=='0';row['returncode']=0;row['resumed_completed_command']=True;return(out/(label+'.stdout')).read_text()
 print('RUN384',mode,label,flush=True)
 with(out/(label+'.stdout')).open('w')as a,(out/(label+'.stderr')).open('w')as b:q=subprocess.run(row['argv'],input=stdin,text=True,stdout=a,stderr=b,timeout=timeout)
 code.write_text(str(q.returncode)+'\n');row['returncode']=q.returncode;save();assert q.returncode==0,(label,q.returncode,(out/(label+'.stderr')).read_text()[-2500:]);return(out/(label+'.stdout')).read_text()
GCC='gcc:15@sha256:eb5e64286ad47187b32bda75c6b6916166ecb41da56559b8b09e0001748d2cce';tag='speed-demon-fresh/track-c:round384-fixed-words4';common=['docker','run','--rm','--pull=never','--platform','linux/amd64','--network=none','--read-only','--memory=8g','--memory-swap=8g','--pids-limit=512','--cap-drop=ALL','--security-opt=no-new-privileges','--user','65534:65534','--tmpfs','/tmp:rw,exec,size=1g']
def inventory():
 jobs={};errors={};folders={};expected={}
 for path in [r/'docs/round370-c-image-proof.json',w/'native-proof/asan/matrix.json',w/'native-proof/tsan/matrix.json']:
  bank=read(path);assert bank['passed']
  for error,rows in [(False,bank['runs']),(True,bank['expected_failures'])]:
   for original in rows:
    row={k:v for k,v in original.items()if k in ['case','data_folder','threads','inputs_sha256','expected_sha256','reference_source']};data=(r/row['data_folder']).resolve();data.relative_to(r);hashes={p.name:sha(p)for p in data.iterdir()if p.is_file()};assert hashes==row['inputs_sha256'];content=tuple(sorted(hashes.items()));folders[str(data)]=hashes;row['data_folder']=str(data.relative_to(r));row['reference_source']=str(path.relative_to(r))+' saved input/expected bytes only; new image/source actually run'
    if error:errors[(content,row['threads'])]=row
    else:
     assert row['expected_sha256']
     if content in expected:assert expected[content]==row['expected_sha256']
     expected[content]=row['expected_sha256'];jobs[(content,row['threads'])]=row
 return list(jobs.values()),list(errors.values()),folders
if mode=='build':
 assert read(w/'proof/gcc/report.json')['passed'];assert sha(s/'track-c/training_generator.py')==sha(r/'tools/official/generators/c_join.py');assert sha(s/'track-c/Dockerfile')==pre['root_selected_bindings']['track-c/Dockerfile']
 spec=importlib.util.spec_from_file_location('policy384',r/'tools/official/harness/dockerfile_check.py');policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy);assert not policy.check((s/'track-c/Dockerfile').read_text(),read(r/'docs/allowlist.json')['images'])
 cmd(['docker','build','--pull=false','--platform','linux/amd64','--network=none','-t',tag,str(s/'track-c')],'build',timeout=900);info=json.loads(cmd(['docker','image','inspect',tag],'inspect'))[0];original=json.loads(cmd(['docker','image','inspect','sha256:263099fcbeecd9be03c762fc791651c246e2ec2ca2223f5940e186c13645dd63'],'original-config'))[0];assert info['Architecture']=='amd64'and info['Size']<=2*1024**3
 for key in ['User','Env','Entrypoint','Cmd','WorkingDir']:assert info['Config'].get(key)==original['Config'].get(key),key
 assert info['Config']['User']=='65534:65534'and info['Config']['Entrypoint']==['/app/solution']and not any(x.startswith('SPEED_DEMON_THREADS=')for x in info['Config']['Env']);elf=cmd([*common,'--entrypoint','sha256sum',info['Id'],'/app/solution'],'elf').split()[0];report.update(image_id=info['Id'],image_tag=tag,image_bytes=info['Size'],elf_sha256=elf,image_config=info['Config'],training='Exact unchanged Dockerfile: pinned native GCC15 BOTH passes, officialbyte-identical generator full1000003 then sample130363, default12. Public1/untrained data never available to build. Only solution executable enters unchanged Debian base final image.')
else:
 jobs,errors,folders=inventory();report['content_thread_deduplication']=True
 if mode=='gcc':
  jobs=[x for x in jobs if x['threads']in[1,6,12]];errors=[x for x in errors if x['threads']in[1,6,12]];image=GCC
 else:assert read(w/'proof/build/report.json')['passed'];image=read(w/'proof/build/report.json')['image_id']
 report['image_id']=image
 if mode=='defaults':
  assert read(w/'proof/image/report.json')['passed'];allowed=read(r/'docs/round370-c-defaults-proof.json');content=lambda x:tuple(sorted(x['inputs_sha256'].items()));selected={content(x)for x in allowed['runs']}|{content(x)for x in pre['fixtures']};selected_errors={content(x)for x in allowed['expected_failures']};jobs=list({content(x):x for x in jobs if content(x)in selected}.values());errors=list({content(x):x for x in errors if content(x)in selected_errors}.values());runs=[];fails=[]
  for error,rows in [(False,jobs),(True,errors)]:
   for n,row in enumerate(rows):
    label=('error-'if error else'default-')+str(n);dest=out/label;dest.mkdir(exist_ok=True);dest.chmod(0o777);stdout=cmd([*common,'-v',str(r/row['data_folder'])+':/data:ro','-v',str(dest)+':/out:rw',image],label,timeout=180)if not error else None
    if error:
     marker=out/(label+'.result.json')
     if marker.exists():trial=read(marker);assert trial['returncode']==1
     else:
      argv=[*common,'-v',str(r/row['data_folder'])+':/data:ro','-v',str(dest)+':/out:rw',image];q=subprocess.run(argv,capture_output=True,text=True,timeout=180);trial={'argv':argv,'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr};dump(marker,trial)
     assert trial['returncode']==1 and not trial['stdout']and trial['stderr'].startswith('track-c:')and not any(t in trial['stderr']for t in ['Sanitizer','runtime error:','DEADLYSIGNAL']);row=dict(row,stderr=trial['stderr']);fails.append(row)
    else:
     assert not stdout and not(out/(label+'.stderr')).read_bytes()and[p.name for p in dest.iterdir()]==['aggregates.txt'];row=dict(row,sha256=sha(dest/'aggregates.txt'));assert row['sha256']==row['expected_sha256'];runs.append(row)
    row['source_fixture_threads']=row.pop('threads');row['configured_default_threads']=12
    if n%10==0:report.update(runs=runs,expected_failures=fails);save()
  report.update(runs=runs,expected_failures=fails,arguments=[],thread_override=False)
 else:
  script=['set -eu','mkdir -p /out/stdio','export ASAN_OPTIONS=halt_on_error=1','export UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1'];binary='/app/solution'
  if mode=='gcc':
   flags='g++ -std=c++20 -O1 -g -march=native -Wall -Wextra -Wpedantic -Werror -pthread -fsanitize=address,undefined -fno-sanitize-recover=all -fno-omit-frame-pointer '
   for name,unit in [('names-model',w/'fixed_words_model.cpp'),('solution',s/'track-c/main.cpp')]:
    script+=['if test -f /out/'+name+'.sha256; then sha256sum -c /out/'+name+'.sha256; else '+flags+shlex.quote('/repo/'+str(unit.relative_to(r)))+' -o /out/'+name+'; sha256sum /out/'+name+' >/out/'+name+'.sha256; fi']
   script+=['g++ --version >/out/gcc.txt','if ! test -f /out/model.pass; then /out/names-model >/out/model.stdout 2>/out/model.stderr; touch /out/model.pass; fi'];binary='/out/solution';report['strict_flags']=flags
  for error,rows in [(False,jobs),(True,errors)]:
   for n,row in enumerate(rows):
    label=('error-'if error else'valid-')+str(n);expected_code=1 if error else 0;launch='SPEED_DEMON_THREADS='+str(row['threads'])+' '+binary+' --data '+shlex.quote('/repo/'+row['data_folder'])+' --out /out/'+label+' >/out/stdio/'+label+'.stdout 2>/out/stdio/'+label+'.stderr';script+=['if ! test -f /out/stdio/'+label+'.code; then','set +e',launch,'code=$?','set -e','echo "$code" >/out/stdio/'+label+'.code','fi','test "$(cat /out/stdio/'+label+'.code)" -eq '+str(expected_code)]
  cmd([*common,'-i','--entrypoint','/bin/sh','-v',str(r)+':/repo:ro','-v',str(out)+':/out:rw',image,'-s'],'replay','\n'.join(script)+'\n',timeout=1800);assert not(out/'replay.stderr').read_bytes(),(out/'replay.stderr').read_text()[-3000:]
  for error,rows in [(False,jobs),(True,errors)]:
   for n,row in enumerate(rows):
    label=('error-'if error else'valid-')+str(n);assert(out/'stdio'/(label+'.code')).read_text().strip()==('1'if error else'0')and not(out/'stdio'/(label+'.stdout')).read_bytes();stderr=(out/'stdio'/(label+'.stderr')).read_text()
    if error:assert stderr.startswith('track-c:')and not any(t in stderr for t in ['Sanitizer','runtime error:','DEADLYSIGNAL']);row['stderr']=stderr
    else:assert not stderr and[p.name for p in(out/label).iterdir()]==['aggregates.txt'];row['sha256']=sha(out/label/'aggregates.txt');assert row['sha256']==row['expected_sha256']
  if mode=='gcc':assert 'PASS384'in(out/'model.stdout').read_text()and not(out/'model.stderr').read_bytes();report.update(compiled_binary_sha256=sha(out/'solution'),compiled_model_sha256=sha(out/'names-model'),model_stdout=(out/'model.stdout').read_text(),gcc=(out/'gcc.txt').read_text())
  report.update(runs=jobs,expected_failures=errors)
 for data,hashes in folders.items():assert{p.name:sha(p)for p in Path(data).iterdir()if p.is_file()}==hashes
for p,h in pre['source_sha256'].items():assert sha(s/p)==h
for p,h in pre['root_selected_bindings'].items():assert sha(r/p)==h
report.update(passed=True,completed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());dump(out/'report.json',report);dump(r/f'docs/round384-c-{mode}-proof.json',report);print('PASS384 Linux',mode,len(report.get('runs',[])),len(report.get('expected_failures',[])),flush=True)
