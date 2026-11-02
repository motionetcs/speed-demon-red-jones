from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,shlex,subprocess
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round343';s=w/'source';pre=json.loads((w/'frozen.json').read_text());root=w/'linux-proof';root.mkdir(exist_ok=True)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
p=argparse.ArgumentParser();p.add_argument('mode',choices=['gcc','build','image','defaults']);mode=p.parse_args().mode;out=root/mode;out.mkdir(exist_ok=True);out.chmod(0o777);assert not (out/'report.json').exists(),'Do not repeat completed mode'
for name,h in pre['source_sha256'].items():assert sha(s/name)==h,name
for name,h in pre['root_selected_bindings'].items():assert sha(r/name)==h,name
for name,h in pre['unchanged_A_cpp_sha256'].items():assert sha(s/name)==sha(r/name)==h,name
compiler='gcc:15@sha256:eb5e64286ad47187b32bda75c6b6916166ecb41da56559b8b09e0001748d2cce';tag='speed-demon-fresh/track-a:round343-raptorlake-tune';report={'started_at_utc':now(),'official_score':False,'mode':mode,'scope':'A343 explicit scheduling tune only, original A C++/headers/defaultISA/full1000003+sample130363 PGO. Restricted pinned offline unprivileged read-only linuxamd64 fresh current compiler/image/default tests. All reused reports supply reference bytes/input identities ONLY, including rejected342 changed-header data, never source-specific execution proof. No ARM/emulated speed, native routing override or organizer binary identity claim.','frozen_manifest_sha256':sha(w/'frozen.json'),'source_sha256':pre['source_sha256'],'commands':[]}
common=['docker','run','--rm','--pull=never','--platform','linux/amd64','--network=none','--read-only','--memory=8g','--memory-swap=8g','--pids-limit=512','--cap-drop=ALL','--security-opt=no-new-privileges','--user','65534:65534','--tmpfs','/tmp:rw,exec,size=1g']
def run(command,label,stdin=None,timeout=1200):
 assert not (out/(label+'.code')).exists(),'Never repeat completed command '+label
 record={'label':label,'argv':list(map(str,command)),'stdin':stdin};report['commands'].append(record);dump(out/'partial.json',report);print('RUN343',mode,label,flush=True)
 with (out/(label+'.stdout')).open('w') as a,(out/(label+'.stderr')).open('w') as b:q=subprocess.run(list(map(str,command)),input=stdin,text=True,stdout=a,stderr=b,timeout=timeout)
 (out/(label+'.code')).write_text(str(q.returncode)+'\n');record['returncode']=q.returncode;dump(out/'partial.json',report);assert q.returncode==0,(label,q.returncode,(out/(label+'.stderr')).read_text()[-3000:]);return (out/(label+'.stdout')).read_text()
def inventory():
 jobs={};folders={}
 def add(label,expected,threads,origin,recorded=None,explicit=None):
  data=Path(explicit) if explicit else next(p for p in [r/'.data/cases'/label,r/'.data/a'/label] if p.is_dir());data=data if data.is_absolute() else r/data;data=data.resolve();data.relative_to(r);assert {p.name for p in data.iterdir()}=={'requests.log'}
  if str(data) not in folders:folders[str(data)]={'requests.log':sha(data/'requests.log')}
  hashes=folders[str(data)]
  if recorded:assert hashes==recorded,(label,'input changed')
  key=(hashes['requests.log'],int(threads));assert 1<=int(threads)<=12 and expected
  if key in jobs:assert jobs[key]['expected_sha256']==expected
  jobs[key]={'case':label,'data_folder':str(data.relative_to(r)),'threads':int(threads),'expected_sha256':expected,'inputs_sha256':hashes,'reference_source':origin}
 oldpath=r/'docs/round197-restored-a-image-cases.json';old=read(oldpath);assert old['passed']
 for row in old['runs']:add(row['case'],row.get('expected_sha256') or row['sha256'],row['threads'],str(oldpath.relative_to(r)),row.get('inputs_sha256'),row.get('data_folder'))
 native=read(r/'docs/round342-a-native-proof.json');assert native['passed']
 for item in native['integrations']:
  path=r/item['report'];x=read(path);assert x['passed'] and sha(path)==item['report_sha256']
  for row in x['checks']:
   if row.get('track')!='a':continue
   for sample in row['runs']:add(row['case'],row.get('reference_sha256') or sample['sha256'],sample['requested_threads'],item['report']+' expected/input bytes only, rejected342 source execution not reused',row.get('inputs_sha256'),row.get('data_folder'))
 pub=read(r/'docs/public-sha256.json')['tracks']['a']
 for threads in [1,6,12]:add('public-full-seed1',pub['expected_output_sha256'][0],threads,'Published full-public hashes',pub['inputs_sha256'])
 return list(jobs.values()),folders
if mode=='build':
 assert read(root/'gcc/report.json')['passed'];spec=importlib.util.spec_from_file_location('policy',r/'tools/official/harness/dockerfile_check.py');policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy);assert not policy.check((s/'track-a/Dockerfile').read_text(),read(r/'docs/allowlist.json')['images'])
 run(['docker','build','--pull=false','--platform','linux/amd64','--network=none','-t',tag,s/'track-a'],'build',timeout=600)
 info=json.loads(run(['docker','image','inspect',tag],'inspect'))[0];original=json.loads(run(['docker','image','inspect',pre['original_A_image']],'original-config'))[0];assert info['Architecture']=='amd64' and info['Size']<=2*1024**3
 for key in ['User','Entrypoint','Cmd','Env','WorkingDir']:assert info['Config'].get(key)==original['Config'].get(key),key
 assert info['Config']['User']=='65534:65534' and info['Config']['Entrypoint']==['/app/solution'] and not any(x.startswith('SPEED_DEMON_THREADS=') for x in info['Config']['Env'])
 elf=run([*common,'--entrypoint','sha256sum',info['Id'],'/app/solution'],'elf').split()[0];report.update(image_id=info['Id'],image_tag=tag,image_bytes=info['Size'],elf_sha256=elf,image_config=info['Config'],training='Unchanged official1000003/full then130363/sample/default12; only final executable enters image. Both GCC passes explicitmtune=raptorlake with original default generic ISA, no publicseed1 or stored runtime answers.')
else:
 jobs,folders=inventory();report['deduplication']='Actual inputSHA plus worker count, independent reference identity checked; no old source-specific execution pass transferred.';report['inventory_rows']=len(jobs);image=compiler if mode=='gcc' else read(root/'build/report.json')['image_id'];report['image_id']=image
 if mode=='defaults':
  assert read(root/'image/report.json')['passed'];unique={row['inputs_sha256']['requests.log']:dict(row) for row in jobs};runs=[]
  for n,row in enumerate(unique.values()):
   dest=out/f'valid-{n}';dest.mkdir();dest.chmod(0o777);run([*common,'-v',str(r/row['data_folder'])+':/data:ro','-v',str(dest)+':/out:rw',image],'default-'+str(n),timeout=180);assert not (out/f'default-{n}.stdout').read_bytes() and not (out/f'default-{n}.stderr').read_bytes();assert [p.name for p in dest.iterdir()]==['summary.txt'];row['sha256']=sha(dest/'summary.txt');assert row['sha256']==row['expected_sha256'];row['source_fixture_threads']=row.pop('threads');row['configured_default_threads']=12;runs.append(row);report['runs']=runs;dump(out/'partial.json',report)
  report.update(command_arguments=[],thread_override=False)
 else:
  if mode=='gcc':jobs=[row for row in jobs if row['threads'] in [1,6,12]]
  script=['set -eu','export ASAN_OPTIONS=halt_on_error=1','export UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1','mkdir -p /out/stdio'];binary='/app/solution';models=[]
  if mode=='gcc':
   flags='g++ -std=c++20 -O1 -g -mtune=raptorlake -Wall -Wextra -Wpedantic -Werror -pthread -fsanitize=address,undefined -fno-sanitize-recover=all -fno-omit-frame-pointer '
   script+=['g++ --version','g++ -dM -E -x c++ /dev/null >/out/default-macros.txt','g++ -mtune=raptorlake -dM -E -x c++ /dev/null >/out/tuned-macros.txt']
   units=[('main',s/'track-a/main.cpp','solution',None),('prefix',r/'tools/test_decimal_prefix.cpp','prefix-model','DECIMAL_HEADER'),('ordered',r/'tools/test_ordered_output.cpp','ordered-model','ORDERED_OUTPUT_HEADER')]
   for label,source,name,macro in units:
    extra=''
    if macro:
     header=s/'track-a'/('decimal.hpp' if label=='prefix' else 'ordered_output.hpp');extra=shlex.quote('-D'+macro+'="/repo/'+str(header.relative_to(r))+'"')+' ';models.append({'unit':label,'model':str(source.relative_to(r)),'model_sha256':sha(source),'actual_header':str(header.relative_to(r)),'header_sha256':sha(header)})
    script+=[flags+extra+'-I '+shlex.quote('/repo/'+str((s/'track-a').relative_to(r)))+' '+shlex.quote('/repo/'+str(source.relative_to(r)))+' -o /out/'+name,'sha256sum /out/'+name+' >/out/'+name+'.sha256']
   script+=['/out/prefix-model >/out/prefix-model.out 2>/out/prefix-model.err','/out/ordered-model /out/ordered-cases >/out/ordered-model.out 2>/out/ordered-model.err'];binary='/out/solution';report['strict_flags']=flags;report['fresh_model_identity']=models
  for n,row in enumerate(jobs):
   dest=f'valid-{n}';row['output_folder']=dest;script+=['set +e','SPEED_DEMON_THREADS='+str(row['threads'])+' '+binary+' --data '+shlex.quote('/repo/'+row['data_folder'])+' --out /out/'+dest+' >/out/stdio/'+str(n)+'.out 2>/out/stdio/'+str(n)+'.err','code=$?','set -e','echo "$code" >/out/stdio/'+str(n)+'.code','test "$code" -eq 0']
  sinkcase=next(row['data_folder'] for row in jobs if 'first-hour-lag' in row['case'])
  for threads in [1,6,12]:
   target='/out/sink-'+str(threads);script+=['mkdir -p '+target,'ln -sf /dev/full '+target+'/summary.txt','set +e','SPEED_DEMON_THREADS='+str(threads)+' '+binary+' --data '+shlex.quote('/repo/'+sinkcase)+' --out '+target+' >/out/stdio/sink-'+str(threads)+'.out 2>/out/stdio/sink-'+str(threads)+'.err','code=$?','set -e','echo "$code" >/out/stdio/sink-'+str(threads)+'.code','test "$code" -eq 1']
  run([*common,'-i','--entrypoint','/bin/sh','-v',str(r)+':/repo:ro','-v',str(out)+':/out:rw',image,'-s'],'replay','\n'.join(script)+'\n',timeout=1200);assert not (out/'replay.stderr').read_bytes(),(out/'replay.stderr').read_text()
  for n,row in enumerate(jobs):
   dest=out/row.pop('output_folder');assert [p.name for p in dest.iterdir()]==['summary.txt'];assert (out/'stdio'/f'{n}.code').read_text().strip()=='0';assert not (out/'stdio'/f'{n}.out').read_bytes() and not (out/'stdio'/f'{n}.err').read_bytes();row['sha256']=sha(dest/'summary.txt');assert row['sha256']==row['expected_sha256']
  failures=[]
  for threads in [1,6,12]:
   assert (out/'stdio'/f'sink-{threads}.code').read_text().strip()=='1' and not (out/'stdio'/f'sink-{threads}.out').read_bytes();err=(out/'stdio'/f'sink-{threads}.err').read_text();assert err=='track-a: cannot write summary.txt\n';failures.append({'threads':threads,'returncode':1,'stderr':err,'kind':'Normal deferred /dev/full sink failure after joined workers'})
  report.update(runs=jobs,expected_sink_failures=failures)
  if mode=='gcc':
   assert (out/'prefix-model.out').read_text()=='PASS leading decimal byte/reference/guard-page model\n' and not (out/'prefix-model.err').read_bytes();assert (out/'ordered-model.out').read_text().startswith('PASS mapped char') and not (out/'ordered-model.err').read_bytes();report['compiled_binary_sha256']={name:sha(out/name) for name in ['solution','prefix-model','ordered-model']}
   isa=['__SSE__','__SSE2__','__SSE3__','__SSSE3__','__SSE4_1__','__SSE4_2__','__AVX__','__AVX2__','__AVX512F__','__BMI__','__BMI2__','__LZCNT__','__POPCNT__'];macro=lambda text:{p[1]:p[2] if len(p)>2 else '' for l in text.splitlines() if len(p:=l.split())>=2 and p[0]=='#define'};a=macro((out/'default-macros.txt').read_text());b=macro((out/'tuned-macros.txt').read_text());assert {k:a.get(k) for k in isa}=={k:b.get(k) for k in isa};report['default_ISA_macro_comparison']={'passed':True,'scope':'These compiler ISA feature macros unchanged under explicit tune; no claimed organizer binary/microarchitecture measurement.','macros':{k:b.get(k) for k in isa}}
 for folder,hashes in folders.items():assert {'requests.log':sha(Path(folder)/'requests.log')}==hashes
for name,h in pre['source_sha256'].items():assert sha(s/name)==h,name
for name,h in pre['root_selected_bindings'].items():assert sha(r/name)==h,name
report.update(passed=True,completed_at_utc=now());dump(out/'report.json',report);dump(r/f'docs/round343-a-linux-{mode}.json',report);print('PASS343',mode,len(report.get('runs',[])),flush=True)
