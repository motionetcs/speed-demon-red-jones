from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,os,shlex,subprocess
r=Path.cwd();w=r/'.build/round315';source=w/'source';pre=json.loads((w/'preflight.json').read_text());native=json.loads((w/'native-main/report.json').read_text());assert native['passed'];native_models=json.loads((w/'native-models/report.json').read_text());assert native_models['passed'];work=w/'linux-proof';work.mkdir(exist_ok=True)
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
for rel,digest in pre['source_sha256'].items():assert sha(source/rel)==digest
p=argparse.ArgumentParser();p.add_argument('mode',choices=['model','gcc','build','image','defaults']);mode=p.parse_args().mode;out=work/mode;out.mkdir(exist_ok=True);out.chmod(0o777);assert not (out/'report.json').exists(),'Do not repeat completed mode'
gcc='gcc:15@sha256:eb5e64286ad47187b32bda75c6b6916166ecb41da56559b8b09e0001748d2cce';tag='speed-demon-fresh/track-c:round315-shared-inline';common=['docker','run','--rm','--pull=never','--platform','linux/amd64','--network=none','--read-only','--memory=8g','--memory-swap=8g','--pids-limit=512','--cap-drop=ALL','--security-opt=no-new-privileges','--user','65534:65534','--tmpfs','/tmp:rw,exec,size=1g'];flags='g++ -std=c++20 -O1 -g -march=native -Wall -Wextra -Wpedantic -Werror -pthread -fsanitize=address,undefined -fno-sanitize-recover=all -fno-omit-frame-pointer '
report={'started_at_utc':now(),'official_score':False,'mode':mode,'track':'c','source_sha256':pre['source_sha256'],'manifest_sha256':sha(w/'preflight.json'),'native_proof_sha256':sha(w/'native-main/report.json'),'native_models_sha256':sha(w/'native-models/report.json'),'scope':'Fresh exact C315 all-reader shared inline24/owned-long/lazy-block name index under pinned offline Linux/amd64 strict GCC and unique unchanged allowed-PGO image. Candidate-specific independent shared publication/lifetime/collision/country/cancel/retry models and current main execute. Old queue fixture banks supply independent data/reference bytes only. Native/emulated timing or memory are not organizer K/ELF proof.'}
identity={'source_sha256':pre['source_sha256'],'compiler_image':gcc,'strict_flags':flags,'allocation_fault_flags':'g++ -std=c++20 -O1 -g -march=native -Wall -Wextra -Wpedantic -Werror -pthread -fno-omit-frame-pointer (plain allocator interposition; no sanitizer claim)','mode':mode};ip=out/'source-identity.json'
if ip.exists():assert read(ip)==identity
else:ip.write_text(json.dumps(identity,indent=2)+'\n')
def run(cmd,label,stdin=None,timeout=1200):
 print('RUN315',mode,label,flush=True);cmd=list(map(str,cmd));report.setdefault('commands',[]).append({'label':label,'argv':cmd,'stdin':stdin});(out/'partial.json').write_text(json.dumps(report,indent=2)+'\n')
 with (out/(label+'.stdout')).open('w') as stdout,(out/(label+'.stderr')).open('w') as stderr:q=subprocess.run(cmd,input=stdin,text=True,stdout=stdout,stderr=stderr,timeout=timeout,env=dict(os.environ,PYTHONPATH=str(r/'tools')))
 (out/(label+'.code')).write_text(str(q.returncode)+'\n');assert q.returncode==0,(label,q.returncode,(out/(label+'.stderr')).read_text()[-3000:]);return (out/(label+'.stdout')).read_text()

def inventory():
 jobs={};errors={};folders={};expected_content={};fresh=set()
 def folder(label,explicit=None):
  if explicit:
   data=Path(explicit);data=data if data.is_absolute() else r/data
  else:data=next(p for p in [r/'.data/cases'/label,r/'.data/c'/label] if p.is_dir())
  data=data.resolve();data.relative_to(r);assert {p.name for p in data.iterdir() if p.is_file()}=={'records.csv','regions.csv'}
  if str(data) not in folders:folders[str(data)]={p.name:sha(p) for p in data.iterdir() if p.is_file()}
  return data,folders[str(data)]
 def add(label,expected,threads,origin,recorded=None,explicit=None,error=False,isfresh=False):
  data,hashes=folder(label,explicit);threads=int(threads);assert 1<=threads<=12
  if recorded:assert hashes==recorded,(label,'input changed')
  content=tuple(sorted(hashes.items()));row={'case':label,'data_folder':str(data.relative_to(r)),'threads':threads,'inputs_sha256':hashes,'reference_source':origin}
  if error:row['returncode']=1;errors[(content,threads)]=row
  else:
   assert expected
   if content in expected_content:assert expected_content[content]==expected,(label,'conflicting reference')
   expected_content[content]=expected;row['expected_sha256']=expected;jobs[(content,threads)]=row
   if isfresh:fresh.add(content)
 old=read(r/'docs/round234-c-image-matrix.json');assert old['passed'] and len(old['runs'])==630
 for row in old['runs']:add(row['case'],row.get('expected_sha256') or row['sha256'],row['threads'],'docs/round234-c-image-matrix.json input/reference only',row.get('inputs_sha256'),row.get('data_folder'))
 for row in old['expected_failures']:add(row['case'],None,row['threads'],'docs/round234-c-image-matrix.json error input only',row['inputs_sha256'],row['data_folder'],error=True)
 reports=[(r/item['report'],item['command']) for item in native['runs']]
 model_report=read(work/'model/report.json');assert model_report['passed']
 assert model_report['source_sha256']==pre['source_sha256']
 reports +=[(r/path,[]) for path in model_report['native_gcc_pair_reports']]
 for path,cmd in reports:
  data=read(path);assert data['passed'];prefix=cmd[cmd.index('--run-id')+1] if '--run-id' in cmd else None
  for row in data.get('checks',[]):
   if row.get('track')!='c':continue
   for sample in row['runs']:add(row['case'],row.get('reference_sha256') or sample['sha256'],sample['requested_threads'],str(path.relative_to(r)),row.get('inputs_sha256'),row.get('data_folder'),isfresh=True)
  for row in data.get('expected_failures',[]):
   label=row.get('data_case') or (prefix+'-'+row['case'] if prefix else row['case']);add(label,None,row['threads'],str(path.relative_to(r)),row.get('inputs_sha256'),row.get('data_folder'),error=True)
 screen=read(r/'.build/round314/confirmation/report.json');assert screen['passed']
 for row in screen['cases']:
  for threads in [1,6,12]:add(row['case'],row['expected_sha256'],threads,'314 saved independent full-input references only, not315 execution/timing proof',row['inputs_sha256'],row['data_folder'],isfresh=True)
 for row in native['full_public_untrained_runs']:
  add(row['case'],row['expected_sha256'],row['threads'],'Exact315 strict ASAN execution against saved independent full references',row['inputs_sha256'],row['data_folder'],isfresh=True)
 pub=read(r/'docs/public-sha256.json')['tracks']['c']
 for threads in [1,6,12]:add('public-full-seed1',pub['expected_output_sha256'][0],threads,'Published official full-public hashes',pub['inputs_sha256'])
 return list(jobs.values()),list(errors.values()),folders,fresh

if mode=='model':
 for rel,h in pre['model_files_sha256'].items():assert sha(w/rel)==h
 script=['set -eu','export ASAN_OPTIONS=halt_on_error=1','export UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1']
 for unit in ['shared_index_model','allocation_failure_model']:
  model=w/('shared_index_model_gcc.cpp' if unit=='shared_index_model' else unit+'.cpp');binary=out/unit;marker=out/(unit+'.sha256')
  if unit=='shared_index_model':style=read(w/'gcc-model-style.json');assert sha(w/'shared_index_model.cpp')==style['native_original_model_sha256'] and sha(model)==style['strict_gcc_style_model_sha256']
  if marker.exists():assert sha(binary)==marker.read_text().split()[0]
  else:script +=[(flags if unit=='shared_index_model' else 'g++ -std=c++20 -O1 -g -march=native -Wall -Wextra -Wpedantic -Werror -pthread -fno-omit-frame-pointer ')+'-I '+shlex.quote('/repo/'+str((source/'track-c').relative_to(r)))+' '+shlex.quote('/repo/'+str(model.relative_to(r)))+' -o /out/'+unit,'sha256sum /out/'+unit+' >/out/'+unit+'.sha256.tmp','mv /out/'+unit+'.sha256.tmp /out/'+unit+'.sha256']
  if (out/(unit+'.out')).exists() and (out/(unit+'.out')).read_text().startswith('PASS shared') and not (out/(unit+'.err')).read_bytes():continue
  script+=['/out/'+unit+' >/out/'+unit+'.out 2>/out/'+unit+'.err']
 run([*common,'-i','--entrypoint','/bin/sh','-v',str(r)+':/repo:ro','-v',str(out)+':/out:rw',gcc,'-s'],'model','\n'.join(script)+'\n',timeout=900)
 models=[]
 for unit in ['shared_index_model','allocation_failure_model']:
  assert (out/(unit+'.out')).read_text().startswith('PASS shared') and not (out/(unit+'.err')).read_bytes();models.append({'unit':unit,'binary_sha256':sha(out/unit),'stdout':(out/(unit+'.out')).read_text(),'stderr':'','sanitizers':'ASAN/UBSAN(no recovery)' if unit=='shared_index_model' else 'None: isolated plain allocator-interposition fault behavior; no sanitizer certificate'})
 report.update(model_files_sha256=pre['model_files_sha256'],models=models,gcc_model_style_binding=read(w/'gcc-model-style.json'),native_gcc_pair_reports=[],model_scope='Exact315 shared-index models: full key/fingerprint/index/inline/long/guard/owned storage/country spill/capacity and concurrent publication/cancellation; separate allocation fault test details are bound in source/native reports. No old owner queue protocol claim.')
elif mode=='build':
 assert read(work/'gcc/report.json')['passed']
 spec=importlib.util.spec_from_file_location('policy',r/'tools/official/harness/dockerfile_check.py');policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy);assert not policy.check((source/'track-c/Dockerfile').read_text(),read(r/'docs/allowlist.json')['images'])
 run(['docker','build','--platform','linux/amd64','--network=none','-t',tag,source/'track-c'],'build',timeout=1200)
 info=json.loads(run(['docker','image','inspect',tag],'inspect'))[0];original=json.loads(run(['docker','image','inspect','sha256:263099fcbeecd9be03c762fc791651c246e2ec2ca2223f5940e186c13645dd63'],'original-config'))[0];assert info['Architecture']=='amd64' and info['Size']<=2*1024**3
 for key in ['User','Env','Entrypoint','Cmd','WorkingDir']:assert info['Config'].get(key)==original['Config'].get(key),key
 assert info['Config']['User']=='65534:65534' and info['Config']['Entrypoint']==['/app/solution'] and not any(v.startswith('SPEED_DEMON_THREADS=') for v in info['Config']['Env']);elf=run([*common,'--entrypoint','sha256sum',info['Id'],'/app/solution'],'elf').split()[0];report.update(image_id=info['Id'],image_tag=tag,image_bytes=info['Size'],elf_sha256=elf,image_config=info['Config'],training='Unchanged pinned original native GCC/full1000003 then sample130363/default12; only executable copied to final image; no publicseed1 training.')
else:
 jobs,errors,folders,fresh=inventory();report.update(original_bank_rows=630,deduplication='Complete input content hashes plus worker count; expected hashes must agree; archived inputs/reference bytes only reused.')
 image=gcc if mode=='gcc' else read(work/'build/report.json')['image_id'];report['image_id']=image
 if mode=='defaults':
  assert read(work/'image/report.json')['passed'];base=read(r/'docs/round234-c-default-matrix.json');allowed={tuple(sorted(x['inputs_sha256'].items())) for x in base['runs']}|fresh;allowed_errors={tuple(sorted(x['inputs_sha256'].items())) for x in base['expected_failures']};unique={tuple(sorted(x['inputs_sha256'].items())):dict(x) for x in jobs if tuple(sorted(x['inputs_sha256'].items())) in allowed};errunique={tuple(sorted(x['inputs_sha256'].items())):dict(x) for x in errors if tuple(sorted(x['inputs_sha256'].items())) in allowed_errors}
  runs=[];fails=[]
  for n,row in enumerate(unique.values()):
   dest=out/f'valid-{n}';dest.mkdir(exist_ok=True);dest.chmod(0o777);run([*common,'-v',str(r/row['data_folder'])+':/data:ro','-v',str(dest)+':/out:rw',image],f'default-{n}',timeout=180);assert not (out/f'default-{n}.stdout').read_bytes() and not (out/f'default-{n}.stderr').read_bytes();assert [p.name for p in dest.iterdir()]==['aggregates.txt'];row['sha256']=sha(dest/'aggregates.txt');assert row['sha256']==row['expected_sha256'];row['source_fixture_threads']=row.pop('threads');row['configured_default_workers']=12;runs.append(row);report['runs']=runs;(out/'partial.json').write_text(json.dumps(report,indent=2)+'\n')
  for n,row in enumerate(errunique.values()):
   dest=out/f'error-{n}';dest.mkdir(exist_ok=True);dest.chmod(0o777);q=subprocess.run([*common,'-v',str(r/row['data_folder'])+':/data:ro','-v',str(dest)+':/out:rw',image],capture_output=True,text=True,timeout=180);assert q.returncode==1 and not q.stdout and q.stderr.startswith('track-c:') and not any(t in q.stderr for t in ['Sanitizer','runtime error:','DEADLYSIGNAL']);row.update(returncode=q.returncode,stdout=q.stdout,stderr=q.stderr,source_fixture_threads=row.pop('threads'),configured_default_workers=12);fails.append(row)
  report.update(runs=runs,expected_failures=fails,arguments=[],thread_override=False,default_selection='Original72 unique default reference inputs plus every fresh native/country/topology/full case, deduplicated by content. Complete production bank is separately image-replayed. No claim that every monetary alias is an independent timing sample.')
 else:
  if mode=='gcc':jobs=[x for x in jobs if x['threads'] in [1,6,12]];errors=[x for x in errors if x['threads'] in [1,6,12]]
  script=['set -eu','export ASAN_OPTIONS=halt_on_error=1','export UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1','mkdir -p /out/stdio'];binary='/app/solution'
  if mode=='gcc':
   marker=out/'solution.sha256';saved=out/'solution'
   if marker.exists():assert sha(saved)==marker.read_text().split()[0]
   else:script +=[flags+shlex.quote('/repo/'+str((source/'track-c/main.cpp').relative_to(r)))+' -o /out/solution','sha256sum /out/solution >/out/solution.sha256.tmp','mv /out/solution.sha256.tmp /out/solution.sha256']
   script+=['g++ -march=native -dM -E -x c++ /dev/null >/out/compiler-macros.txt'];binary='/out/solution'
  for n,row in enumerate(jobs):
   marker=out/'stdio'/f'{n}.code';dest=out/f'valid-{n}'
   if marker.exists():assert marker.read_text().strip()=='0' and sha(dest/'aggregates.txt')==row['expected_sha256'] and not (out/'stdio'/f'{n}.out').read_bytes() and not (out/'stdio'/f'{n}.err').read_bytes();continue
   script+=['set +e','SPEED_DEMON_THREADS='+str(row['threads'])+' '+binary+' --data '+shlex.quote('/repo/'+row['data_folder'])+' --out /out/'+dest.name+' >/out/stdio/'+str(n)+'.out 2>/out/stdio/'+str(n)+'.err','code=$?','set -e','echo "$code" >/out/stdio/'+str(n)+'.code','test "$code" -eq 0']
  for n,row in enumerate(errors):
   marker=out/'stdio'/f'error-{n}.code'
   if marker.exists():assert marker.read_text().strip()=='1';continue
   script+=['set +e','SPEED_DEMON_THREADS='+str(row['threads'])+' '+binary+' --data '+shlex.quote('/repo/'+row['data_folder'])+' --out /out/error-'+str(n)+' >/out/stdio/error-'+str(n)+'.out 2>/out/stdio/error-'+str(n)+'.err','code=$?','set -e','echo "$code" >/out/stdio/error-'+str(n)+'.code','test "$code" -eq 1']
  run([*common,'-i','--entrypoint','/bin/sh','-v',str(r)+':/repo:ro','-v',str(out)+':/out:rw',image,'-s'],'replay','\n'.join(script)+'\n',timeout=1200);assert not (out/'replay.stderr').read_bytes(),(out/'replay.stderr').read_text()
  for n,row in enumerate(jobs):
   dest=out/f'valid-{n}';assert [p.name for p in dest.iterdir()]==['aggregates.txt'];assert (out/'stdio'/f'{n}.code').read_text().strip()=='0' and not (out/'stdio'/f'{n}.out').read_bytes() and not (out/'stdio'/f'{n}.err').read_bytes();row['sha256']=sha(dest/'aggregates.txt');assert row['sha256']==row['expected_sha256']
  for n,row in enumerate(errors):
   assert (out/'stdio'/f'error-{n}.code').read_text().strip()=='1' and not (out/'stdio'/f'error-{n}.out').read_bytes();err=(out/'stdio'/f'error-{n}.err').read_text();assert err.startswith('track-c:') and not any(t in err for t in ['Sanitizer','runtime error:','DEADLYSIGNAL']);row['stderr']=err
  report.update(runs=jobs,expected_failures=errors)
  if mode=='gcc':report['compiled_binary_sha256']=sha(out/'solution')
 for folder,hashes in folders.items():assert {p.name:sha(p) for p in Path(folder).iterdir() if p.is_file()}==hashes
for rel,digest in pre['source_sha256'].items():assert sha(source/rel)==digest
report.update(passed=True,completed_at_utc=now());(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(r/f'docs/round315-c-linux-{mode}.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS315',mode,len(report.get('runs',[])),len(report.get('expected_failures',[])),flush=True)
