from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,os,shlex,subprocess,sys
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round357';s=w/'source';pre=json.loads((w/'preflight.json').read_text());pre['original_C_image']='sha256:263099fcbeecd9be03c762fc791651c246e2ec2ca2223f5940e186c13645dd63';native=json.loads((w/'native-proof/report.json').read_text());assert native['passed']
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['model','gcc','build','image','defaults']);mode=parser.parse_args().mode;out=w/'proof'/mode;out.mkdir(parents=True,exist_ok=True);out.chmod(0o777);assert not (out/'report.json').exists(),'Do not repeat completed mode'
for p,h in pre['source_sha256'].items():assert sha(s/p)==h,p
for p,h in pre['root_selected_bindings'].items():assert sha(r/p)==h,p
report={'started_at_utc':now(),'official_score':False,'selected_in_root':False,'mode':mode,'track':'c','scope':'C357 boundedstandardatomicbatchwaits, stickyqueuecancel, uint32owner-epoch/directGNUplatformword and C-onlynoexceptlaunchfailurecancellation. NEWsource-specific pinnedGCCfailfastASANmodels/main, separateplainfault/oldcontrol reproduction, oneexactunchangedallowednativePGOimage/defaults. Native357ASAN/TSANwrap/ownership/currentmainprooffresh; savedreferencebanks areinput/referencebytesONLY. No emulated/Intel timing, organizerELF or scoregain claim.','manifest_sha256':sha(w/'preflight.json'),'source_sha256':pre['source_sha256'],'commands':[]}
def command(argv,label,stdin=None,timeout=1200,env=None):
 argv=list(map(str,argv));assert not (out/(label+'.code')).exists(),'Never repeat completed '+label;row={'label':label,'argv':argv,'stdin':stdin};report['commands'].append(row);dump(out/'partial.json',report);print('RUN357',mode,label,flush=True)
 with (out/(label+'.stdout')).open('w') as a,(out/(label+'.stderr')).open('w') as b:q=subprocess.run(argv,input=stdin,text=True,stdout=a,stderr=b,timeout=timeout,env=env)
 (out/(label+'.code')).write_text(str(q.returncode)+'\n');row['returncode']=q.returncode;dump(out/'partial.json',report);assert q.returncode==0,(label,q.returncode,(out/(label+'.stderr')).read_text()[-2500:]);return (out/(label+'.stdout')).read_text()
compiler='gcc:15@sha256:eb5e64286ad47187b32bda75c6b6916166ecb41da56559b8b09e0001748d2cce';tag='speed-demon-fresh/track-c:round357-atomic-waits';common=['docker','run','--rm','--pull=never','--platform','linux/amd64','--network=none','--read-only','--memory=8g','--memory-swap=8g','--pids-limit=512','--cap-drop=ALL','--security-opt=no-new-privileges','--user','65534:65534','--tmpfs','/tmp:rw,exec,size=1g']
if mode=='model':
 assert sha(w/'counter32-review.md')=='203b1dd8e309b1e1ff91df58f7a5a7f83142dc9fc4371e9abad1bc6fc2ed9960'
 flags='g++ -std=c++20 -O1 -g -march=native -Wall -Wextra -Wpedantic -Werror -pthread -fsanitize=address,undefined -fno-sanitize-recover=all -fno-omit-frame-pointer '
 plain='g++ -std=c++20 -O1 -g -Wall -Wextra -Wpedantic -Werror -pthread -static -DTEST_PTHREAD_WRAP -Wl,--wrap=pthread_create '
 script=['set -eu','export ASAN_OPTIONS=halt_on_error=1','export UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1','g++ --version >/out/gcc.txt','getconf GNU_LIBC_VERSION >/out/glibc.txt','for header in /usr/local/include/c++/*/bits/atomic_wait.h; do sha256sum "$header" >/out/pinned-wait-header.sha256; cp "$header" /out/pinned-atomic_wait.h; done',flags+shlex.quote('/repo/'+str((w/'queue_model_gcc.cpp').relative_to(r)))+' -o /out/queue-model','/out/queue-model >/out/queue.out 2>/out/queue.err',plain+shlex.quote('/repo/'+str((w/'startup_failure_main_gcc.cpp').relative_to(r)))+' '+shlex.quote('/repo/'+str((w/'fault_allocator_gcc.cpp').relative_to(r)))+' -o /out/startup-model','/out/startup-model >/out/startup.out 2>/out/startup.err',plain+'-DCONTROL_OLD '+shlex.quote('-DPARALLEL_HEADER="/repo/.build/round353/submitted-source/track-c/parallel.hpp"')+' '+shlex.quote('/repo/'+str((w/'startup_failure_main_gcc.cpp').relative_to(r)))+' '+shlex.quote('/repo/'+str((w/'fault_allocator_gcc.cpp').relative_to(r)))+' -o /out/old-startup-control','set +e','timeout -k 1 3 /out/old-startup-control >/out/old-control.out 2>/out/old-control.err','code=$?','set -e','echo "$code" >/out/old-control.code','test "$code" -eq 124']
 command([*common,'-i','--entrypoint','/bin/sh','-v',str(r)+':/repo:ro','-v',str(out)+':/out:rw',compiler,'-s'],'models','\n'.join(script)+'\n')
 assert not(out/'models.stderr').read_bytes(),(out/'models.stderr').read_text()[-3000:]
 assert(out/'queue.out').read_text().startswith('PASS357')and not(out/'queue.err').read_bytes()
 assert(out/'startup.out').read_text().startswith('PASS356')and not(out/'startup.err').read_bytes()
 assert(out/'old-control.code').read_text().strip()=='124'and(out/'old-control.out').read_text().startswith('CONTROL356')and not(out/'old-control.err').read_bytes()
 report.update(queue_stdout=(out/'queue.out').read_text(),startup_stdout=(out/'startup.out').read_text(),queue_binary_sha256=sha(out/'queue-model'),startup_binary_sha256=sha(out/'startup-model'),old_control_binary_sha256=sha(out/'old-startup-control'),old_control_expected_timeout=124,old_control_scope='Controlledtest-only secondpthread_create EAGAIN usingEXACTold353parallel header reproduces pre-existing startupjoinhang; newactual357parallel callback handlesall17forcedpthreadfailures plusallocationfailures beforejoin. No production fault hooks.',fresh_model_sha256={name:sha(w/name)for name in ['queue_model_gcc.cpp','startup_failure_main_gcc.cpp','fault_allocator_gcc.cpp','cancel_body.inc','counter32-review.md']},compiler_version=(out/'gcc.txt').read_text(),libc_version=(out/'glibc.txt').read_text(),pinned_wait_header_sha256=(out/'pinned-wait-header.sha256').read_text(),platform_path='NewactualGCCmodel static_asserts publicatomicvalue uint32 usesdirectplatformword and uint64 doesnot; typepath evidence only, not dynamiccost/organizerELF.',model_copy_scope='GNUqueuecopy adds ONLY2private-library-trait staticasserts. GNUplainstartupcopy adds ONLY(void)cancel toallowCONTROL_OLD strictunused diagnostics. Nativefrozenmodels unchanged. These aretest-only sourcecopies, not runtimemodifications or a sanitizersuppression.')
elif mode=='build':
 assert read(w/'proof/model/report.json')['passed'] and read(w/'proof/gcc/report.json')['passed'];assert sha(s/'track-c/training_generator.py')==sha(r/'tools/official/generators/c_join.py')
 spec=importlib.util.spec_from_file_location('policy',r/'tools/official/harness/dockerfile_check.py');policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy);assert not policy.check((s/'track-c/Dockerfile').read_text(),read(r/'docs/allowlist.json')['images'])
 command(['docker','build','--platform','linux/amd64','--network=none','-t',tag,s/'track-c'],'build');info=json.loads(command(['docker','image','inspect',tag],'inspect'))[0];original=json.loads(command(['docker','image','inspect',pre['original_C_image']],'original-config'))[0]
 for key in ['User','Env','Entrypoint','Cmd','WorkingDir']:assert info['Config'].get(key)==original['Config'].get(key),key
 assert info['Architecture']=='amd64' and info['Size']<=2*1024**3 and info['Config']['User']=='65534:65534' and info['Config']['Entrypoint']==['/app/solution'];elf=command([*common,'--entrypoint','sha256sum',info['Id'],'/app/solution'],'elf').split()[0];report.update(image_id=info['Id'],image_tag=tag,image_bytes=info['Size'],elf_sha256=elf,image_config=info['Config'],training='Only byteidentical official1000003/full then130363/sample/default12, exactlyonce newimage; original-march=native bothpasses and executableonlyfinalimage. Neverpublicseed1.')
else:
 assert read(w/'proof/model/report.json')['passed'];jobs={};errors={};folders={};expected_by_content={};fresh_content=set()
 def add(case,expected,threads,origin,explicit=None,recorded=None,error=False,isfresh=False):
  data=Path(explicit)if explicit else next(p for p in [r/'.data/cases'/case,r/'.data/c'/case]if p.is_dir());data=data if data.is_absolute()else r/data;data=data.resolve();data.relative_to(r);hashes={p.name:sha(p)for p in data.iterdir()if p.is_file()};assert set(hashes)=={'records.csv','regions.csv'}
  if recorded:assert hashes==recorded,(case,'inputchanged')
  content=tuple(sorted(hashes.items()));folders[str(data)]=hashes;row={'case':case,'data_folder':str(data.relative_to(r)),'threads':int(threads),'inputs_sha256':hashes,'reference_source':origin}
  if error:row['returncode']=1;errors[(content,int(threads))]=row
  else:
   assert expected
   if content in expected_by_content:assert expected_by_content[content]==expected
   expected_by_content[content]=expected;row['expected_sha256']=expected;jobs[(content,int(threads))]=row
  if isfresh:fresh_content.add(content)
 bank=read(r/'docs/round234-c-image-matrix.json');assert bank['passed'] and len(bank['runs'])==630
 for row in bank['runs']:add(row['case'],row.get('expected_sha256')or row['sha256'],row['threads'],'234 saveddata/referencebytes only',row.get('data_folder'),row.get('inputs_sha256'))
 for row in bank['expected_failures']:add(row['case'],None,row['threads'],'234 savednormalerrorinput only',row.get('data_folder'),row['inputs_sha256'],error=True)
 for item in native['matrices']:
  assert sha(r/item['path'])==item['sha256'];x=read(r/item['path']);assert x['passed']
  for row in x['runs']:add(row['case'],row['expected_sha256'],row['threads'],item['path']+'input/referenceONLY',row['data_folder'],row['inputs_sha256'],isfresh=True)
  for row in x['expected_failures']:add(row['case'],None,row['threads'],item['path']+'errorinputONLY',row['data_folder'],row['inputs_sha256'],error=True,isfresh=True)
 for row in read(r/'.build/round346/confirmation/report.json')['cases']:
  for threads in [1,6,12]:add(row['case'],row['expected_sha256'],threads,'Official/saved independent full referencehashes only',row['data_folder'],row['inputs_sha256'])
 alljobs=list(jobs.values());allerrors=list(errors.values());report['reference_bank_rows_before_deduplication']=630;report['content_thread_deduplication']=True
 if mode=='gcc':jobs=[x for x in alljobs if x['threads']in[1,6,12]];errors=[x for x in allerrors if x['threads']in[1,6,12]];image=compiler
 else:assert read(w/'proof/build/report.json')['passed'];jobs=alljobs;errors=allerrors;image=read(w/'proof/build/report.json')['image_id']
 report['image_id']=image
 if mode=='defaults':
  assert read(w/'proof/image/report.json')['passed'];base=read(r/'docs/round234-c-default-matrix.json');allowed={tuple(sorted(x['inputs_sha256'].items()))for x in base['runs']}|fresh_content;allowed_errors={tuple(sorted(x['inputs_sha256'].items()))for x in base['expected_failures']};unique={tuple(sorted(x['inputs_sha256'].items())):dict(x)for x in jobs if tuple(sorted(x['inputs_sha256'].items()))in allowed};errunique={tuple(sorted(x['inputs_sha256'].items())):dict(x)for x in errors if tuple(sorted(x['inputs_sha256'].items()))in (allowed_errors|fresh_content)};runs=[];fails=[]
  for n,row in enumerate(unique.values()):
   dest=out/f'valid-{n}';dest.mkdir();dest.chmod(0o777);command([*common,'-v',str(r/row['data_folder'])+':/data:ro','-v',str(dest)+':/out:rw',image],'default-'+str(n),timeout=180);assert not(out/f'default-{n}.stdout').read_bytes()and not(out/f'default-{n}.stderr').read_bytes();assert[p.name for p in dest.iterdir()]==['aggregates.txt'];row['sha256']=sha(dest/'aggregates.txt');assert row['sha256']==row['expected_sha256'];row['source_fixture_threads']=row.pop('threads');row['configured_default_threads']=12;runs.append(row);report['runs']=runs;dump(out/'partial.json',report)
  for n,row in enumerate(errunique.values()):
   dest=out/f'error-{n}';dest.mkdir();dest.chmod(0o777);argv=[*common,'-v',str(r/row['data_folder'])+':/data:ro','-v',str(dest)+':/out:rw',image];q=subprocess.run(argv,capture_output=True,text=True,timeout=180);assert q.returncode==1 and not q.stdout and q.stderr.startswith('track-c:')and not any(t in q.stderr for t in ['Sanitizer','runtime error:','DEADLYSIGNAL']);row['stderr']=q.stderr;row['source_fixture_threads']=row.pop('threads');row['configured_default_threads']=12;fails.append(row)
  report.update(runs=runs,expected_failures=fails)
 else:
  script=['set -eu','mkdir -p /out/stdio','export ASAN_OPTIONS=halt_on_error=1','export UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1'];binary='/app/solution';modelids=[]
  if mode=='gcc':
   flags='g++ -std=c++20 -O1 -g -march=native -Wall -Wextra -Wpedantic -Werror -pthread -fsanitize=address,undefined -fno-sanitize-recover=all -fno-omit-frame-pointer '
   script +=[flags+shlex.quote('/repo/'+str((s/'track-c/main.cpp').relative_to(r)))+' -o /out/solution','sha256sum /out/solution >/out/solution.sha256'];binary='/out/solution'
   report['strict_flags']=flags
  for n,row in enumerate(jobs):script+=['set +e','SPEED_DEMON_THREADS='+str(row['threads'])+' '+binary+' --data '+shlex.quote('/repo/'+row['data_folder'])+' --out /out/valid-'+str(n)+' >/out/stdio/'+str(n)+'.out 2>/out/stdio/'+str(n)+'.err','code=$?','set -e','echo "$code" >/out/stdio/'+str(n)+'.code','test "$code" -eq 0']
  for n,row in enumerate(errors):script+=['set +e','SPEED_DEMON_THREADS='+str(row['threads'])+' '+binary+' --data '+shlex.quote('/repo/'+row['data_folder'])+' --out /out/error-'+str(n)+' >/out/stdio/error-'+str(n)+'.out 2>/out/stdio/error-'+str(n)+'.err','code=$?','set -e','echo "$code" >/out/stdio/error-'+str(n)+'.code','test "$code" -eq 1']
  command([*common,'-i','--entrypoint','/bin/sh','-v',str(r)+':/repo:ro','-v',str(out)+':/out:rw',image,'-s'],'replay','\n'.join(script)+'\n');assert not(out/'replay.stderr').read_bytes(),(out/'replay.stderr').read_text()[-3000:]
  for n,row in enumerate(jobs):
   dest=out/f'valid-{n}';assert[p.name for p in dest.iterdir()]==['aggregates.txt'];assert(out/'stdio'/f'{n}.code').read_text().strip()=='0'and not(out/'stdio'/f'{n}.out').read_bytes()and not(out/'stdio'/f'{n}.err').read_bytes();row['sha256']=sha(dest/'aggregates.txt');assert row['sha256']==row['expected_sha256'],row['case']
  for n,row in enumerate(errors):
   assert(out/'stdio'/f'error-{n}.code').read_text().strip()=='1'and not(out/'stdio'/f'error-{n}.out').read_bytes();err=(out/'stdio'/f'error-{n}.err').read_text();assert err.startswith('track-c:')and not any(t in err for t in ['Sanitizer','runtime error:','DEADLYSIGNAL']);row['stderr']=err
  if mode=='gcc':report['compiled_binary_sha256']=sha(out/'solution')
  report.update(runs=jobs,expected_failures=errors)
 for folder,hashes in folders.items():assert{p.name:sha(p)for p in Path(folder).iterdir()if p.is_file()}==hashes
for p,h in pre['source_sha256'].items():assert sha(s/p)==h,p
for p,h in pre['root_selected_bindings'].items():assert sha(r/p)==h,p
report.update(passed=True,completed_at_utc=now());dump(out/'report.json',report);dump(r/f'docs/round357-c-{mode}-proof.json',report);print('PASS357',mode,len(report.get('runs',[])),len(report.get('expected_failures',[])),flush=True)
