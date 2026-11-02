from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,os,shlex,subprocess,sys
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round362';s=w/'source';pre=json.loads((w/'frozen.json').read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['fresh','gcc','build','image','defaults']);mode=parser.parse_args().mode;out=w/'proof'/mode;out.mkdir(parents=True,exist_ok=True);out.chmod(0o777);assert not (out/'report.json').exists(),'Do not repeat completed mode'
for p,h in pre['source_sha256'].items():assert sha(s/p)==h,p
for p,h in pre['root_selected_bindings'].items():assert sha(r/p)==h,p
report={'started_at_utc':now(),'official_score':False,'selected_in_root':False,'mode':mode,'track':'c','scope':pre['scope'],'manifest_sha256':sha(w/'frozen.json'),'source_sha256':pre['source_sha256'],'commands':[]}
def command(argv,label,stdin=None,timeout=1200,env=None):
 argv=list(map(str,argv));assert not (out/(label+'.code')).exists(),'Never repeat completed '+label;row={'label':label,'argv':argv,'stdin':stdin};report['commands'].append(row);dump(out/'partial.json',report);print('RUN362',mode,label,flush=True)
 with (out/(label+'.stdout')).open('w') as a,(out/(label+'.stderr')).open('w') as b:q=subprocess.run(argv,input=stdin,text=True,stdout=a,stderr=b,timeout=timeout,env=env)
 (out/(label+'.code')).write_text(str(q.returncode)+'\n');row['returncode']=q.returncode;dump(out/'partial.json',report);assert q.returncode==0,(label,q.returncode,(out/(label+'.stderr')).read_text()[-2500:]);return (out/(label+'.stdout')).read_text()
compiler='gcc:15@sha256:eb5e64286ad47187b32bda75c6b6916166ecb41da56559b8b09e0001748d2cce';tag='speed-demon-fresh/track-c:round362-noplt';common=['docker','run','--rm','--pull=never','--platform','linux/amd64','--network=none','--read-only','--memory=8g','--memory-swap=8g','--pids-limit=512','--cap-drop=ALL','--security-opt=no-new-privileges','--user','65534:65534','--tmpfs','/tmp:rw,exec,size=1g']
if mode=='fresh':
 report['reference_reports']=[]
 for name in ['docs/round352-c-fresh-sample3593.json','docs/round352-c-fresh-sample3599.json','docs/round352-c-fresh-full3607.json','docs/round356-c-asan-sample.json','docs/round356-c-asan-fresh-full.json']:
  path=r/name;x=read(path);assert x['passed'];report['reference_reports'].append({'path':name,'sha256':sha(path),'source_specific_target_execution':False})
 report['scope']='Saved source-independent input/reference bank manifest only; no compiler/program/generator/oracle execution. Newly compiled362 strict/image modes actually execute these cases. Existing234 contains independent adversarial/normalerror data;356 includes untrained3623.'
elif mode=='build':
 assert read(w/'proof/gcc/report.json')['passed'];assert sha(s/'track-c/training_generator.py')==sha(r/'tools/official/generators/c_join.py')
 spec=importlib.util.spec_from_file_location('policy',r/'tools/official/harness/dockerfile_check.py');policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy);assert not policy.check((s/'track-c/Dockerfile').read_text(),read(r/'docs/allowlist.json')['images'])
 command(['docker','build','--platform','linux/amd64','--network=none','-t',tag,s/'track-c'],'build');info=json.loads(command(['docker','image','inspect',tag],'inspect'))[0];original=json.loads(command(['docker','image','inspect',pre['original_C_image']],'original-config'))[0]
 for key in ['User','Env','Entrypoint','Cmd','WorkingDir']:assert info['Config'].get(key)==original['Config'].get(key),key
 assert info['Architecture']=='amd64' and info['Size']<=2*1024**3 and info['Config']['User']=='65534:65534' and info['Config']['Entrypoint']==['/app/solution'];elf=command([*common,'--entrypoint','sha256sum',info['Id'],'/app/solution'],'elf').split()[0];report.update(image_id=info['Id'],image_tag=tag,image_bytes=info['Size'],elf_sha256=elf,image_config=info['Config'],training='Only byteidentical official1000003/full then130363/sample/default12, exactlyonce newimage; original-march=native bothpasses and executableonlyfinalimage. Neverpublicseed1.')
else:
 fresh=read(w/'proof/fresh/report.json');assert fresh['passed'];jobs={};errors={};folders={};expected_by_content={};fresh_content=set()
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
 for item in fresh['reference_reports']:
  assert sha(r/item['path'])==item['sha256'];x=read(r/item['path']);assert x['passed']
  for row in x['checks']:
   assert row['track']=='c'
   for trial in row['runs']:add(row['case'],row.get('reference_sha256')or trial['sha256'],trial['requested_threads'],item['path'],row.get('data_folder'),row.get('inputs_sha256'),isfresh=True)
 for row in read(r/'.build/round346/confirmation/report.json')['cases']:
  for threads in [1,6,12]:add(row['case'],row['expected_sha256'],threads,'Official/saved independent full referencehashes only',row['data_folder'],row['inputs_sha256'])
 alljobs=list(jobs.values());allerrors=list(errors.values());report['reference_bank_rows_before_deduplication']=630;report['content_thread_deduplication']=True
 if mode=='gcc':jobs=[x for x in alljobs if x['threads']in[1,6,12]];errors=[x for x in allerrors if x['threads']in[1,6,12]];image=compiler
 else:assert read(w/'proof/build/report.json')['passed'];jobs=alljobs;errors=allerrors;image=read(w/'proof/build/report.json')['image_id']
 report['image_id']=image
 if mode=='defaults':
  assert read(w/'proof/image/report.json')['passed'];base=read(r/'docs/round234-c-default-matrix.json');allowed={tuple(sorted(x['inputs_sha256'].items()))for x in base['runs']}|fresh_content;allowed_errors={tuple(sorted(x['inputs_sha256'].items()))for x in base['expected_failures']};unique={tuple(sorted(x['inputs_sha256'].items())):dict(x)for x in jobs if tuple(sorted(x['inputs_sha256'].items()))in allowed};errunique={tuple(sorted(x['inputs_sha256'].items())):dict(x)for x in errors if tuple(sorted(x['inputs_sha256'].items()))in allowed_errors};runs=[];fails=[]
  for n,row in enumerate(unique.values()):
   dest=out/f'valid-{n}';dest.mkdir();dest.chmod(0o777);command([*common,'-v',str(r/row['data_folder'])+':/data:ro','-v',str(dest)+':/out:rw',image],'default-'+str(n),timeout=180);assert not(out/f'default-{n}.stdout').read_bytes()and not(out/f'default-{n}.stderr').read_bytes();assert[p.name for p in dest.iterdir()]==['aggregates.txt'];row['sha256']=sha(dest/'aggregates.txt');assert row['sha256']==row['expected_sha256'];row['source_fixture_threads']=row.pop('threads');row['configured_default_threads']=12;runs.append(row);report['runs']=runs;dump(out/'partial.json',report)
  for n,row in enumerate(errunique.values()):
   dest=out/f'error-{n}';dest.mkdir();dest.chmod(0o777);argv=[*common,'-v',str(r/row['data_folder'])+':/data:ro','-v',str(dest)+':/out:rw',image];q=subprocess.run(argv,capture_output=True,text=True,timeout=180);assert q.returncode==1 and not q.stdout and q.stderr.startswith('track-c:')and not any(t in q.stderr for t in ['Sanitizer','runtime error:','DEADLYSIGNAL']);row['stderr']=q.stderr;row['source_fixture_threads']=row.pop('threads');row['configured_default_threads']=12;fails.append(row)
  report.update(runs=runs,expected_failures=fails)
 else:
  script=['set -eu','mkdir -p /out/stdio','export ASAN_OPTIONS=halt_on_error=1','export UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1'];binary='/app/solution';modelids=[]
  if mode=='gcc':
   flags='g++ -std=c++20 -O3 -g -march=native -fno-plt -Wall -Wextra -Wpedantic -Werror -pthread -fsanitize=address,undefined -fno-sanitize-recover=all -fno-omit-frame-pointer '
   script+=['g++ --version >/out/gcc.txt',flags+shlex.quote('/repo/'+str((s/'track-c/main.cpp').relative_to(r)))+' -o /out/solution','sha256sum /out/solution >/out/solution.sha256']
   for name,source,defs in [('fields',r/'tools/test_csv_scalar_modes.cpp','-DCSV_HEADER="'+str(w/'csv_model.hpp').replace(str(r),'/repo')+'"'),('numeric',r/'tools/test_csv_numeric.cpp','-DCSV_MODEL_HEADER="'+str(w/'csv_model.hpp').replace(str(r),'/repo')+'"'),('names',r/'tools/test_name_store.cpp','-DNAMES_HEADER="'+str(s/'track-c/names.hpp').replace(str(r),'/repo')+'"')]:
    assert source.is_file();modelids.append({'model':name,'source':str(source.relative_to(r)),'source_sha256':sha(source),'definitions':defs});script+=[flags+shlex.quote(defs)+' '+shlex.quote('/repo/'+str(source.relative_to(r)))+' -o /out/'+name,'/out/'+name+' >/out/'+name+'.out 2>/out/'+name+'.err'];binary='/out/solution'
   report['strict_flags']=flags;report['fresh_models']=modelids
  for n,row in enumerate(jobs):script+=['set +e','SPEED_DEMON_THREADS='+str(row['threads'])+' '+binary+' --data '+shlex.quote('/repo/'+row['data_folder'])+' --out /out/valid-'+str(n)+' >/out/stdio/'+str(n)+'.out 2>/out/stdio/'+str(n)+'.err','code=$?','set -e','echo "$code" >/out/stdio/'+str(n)+'.code','test "$code" -eq 0']
  for n,row in enumerate(errors):script+=['set +e','SPEED_DEMON_THREADS='+str(row['threads'])+' '+binary+' --data '+shlex.quote('/repo/'+row['data_folder'])+' --out /out/error-'+str(n)+' >/out/stdio/error-'+str(n)+'.out 2>/out/stdio/error-'+str(n)+'.err','code=$?','set -e','echo "$code" >/out/stdio/error-'+str(n)+'.code','test "$code" -eq 1']
  command([*common,'-i','--entrypoint','/bin/sh','-v',str(r)+':/repo:ro','-v',str(out)+':/out:rw',image,'-s'],'replay','\n'.join(script)+'\n');assert not(out/'replay.stderr').read_bytes(),(out/'replay.stderr').read_text()[-3000:]
  for n,row in enumerate(jobs):
   dest=out/f'valid-{n}';assert[p.name for p in dest.iterdir()]==['aggregates.txt'];assert(out/'stdio'/f'{n}.code').read_text().strip()=='0'and not(out/'stdio'/f'{n}.out').read_bytes()and not(out/'stdio'/f'{n}.err').read_bytes();row['sha256']=sha(dest/'aggregates.txt');assert row['sha256']==row['expected_sha256'],row['case']
  for n,row in enumerate(errors):
   assert(out/'stdio'/f'error-{n}.code').read_text().strip()=='1'and not(out/'stdio'/f'error-{n}.out').read_bytes();err=(out/'stdio'/f'error-{n}.err').read_text();assert err.startswith('track-c:')and not any(t in err for t in ['Sanitizer','runtime error:','DEADLYSIGNAL']);row['stderr']=err
  if mode=='gcc':
   for name in ['fields','numeric','names']:assert(out/(name+'.out')).read_text().startswith('PASS')and not(out/(name+'.err')).read_bytes()
   report['compiled_binary_sha256']=sha(out/'solution');report['model_csv_extracted_tokens_sha256']=pre['csv_model_sha256']
  report.update(runs=jobs,expected_failures=errors)
 for folder,hashes in folders.items():assert{p.name:sha(p)for p in Path(folder).iterdir()if p.is_file()}==hashes
for p,h in pre['source_sha256'].items():assert sha(s/p)==h,p
for p,h in pre['root_selected_bindings'].items():assert sha(r/p)==h,p
report.update(passed=True,completed_at_utc=now());dump(out/'report.json',report);dump(r/f'docs/round362-c-{mode}-proof.json',report);print('PASS362',mode,len(report.get('runs',[])),len(report.get('expected_failures',[])),flush=True)
