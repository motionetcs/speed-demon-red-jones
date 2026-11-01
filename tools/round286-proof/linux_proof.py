from pathlib import Path
import argparse,datetime,hashlib,importlib.util,json,os,shlex,subprocess
r=Path.cwd();w=r/'.build/round286';source=w/'source';read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();pre=read(w/'preflight.json');native=read(w/'native-proof/report.json');assert native['passed'];mode=argparse.ArgumentParser();mode.add_argument('mode',choices=['gcc','build','image','defaults']);mode=mode.parse_args().mode;work=w/'linux-proof';out=work/mode;out.mkdir(parents=True,exist_ok=True);out.chmod(0o777);assert not (out/'report.json').exists(),'Do not repeat completed mode'
for rel,h in pre['source_sha256'].items():assert sha(source/rel)==h
GCC='gcc:15@sha256:eb5e64286ad47187b32bda75c6b6916166ecb41da56559b8b09e0001748d2cce';tag='speed-demon-fresh/track-d:round286-query6';common=['docker','run','--rm','--pull=never','--platform','linux/amd64','--network=none','--read-only','--memory=8g','--memory-swap=8g','--pids-limit=512','--cap-drop=ALL','--security-opt=no-new-privileges','--user','65534:65534','--tmpfs','/tmp:rw,exec,size=1g','-e','MALLOC_ARENA_MAX=2'];flags='g++ -std=c++20 -O1 -g -march=native -Wall -Wextra -Wpedantic -Werror -pthread -fsanitize=address,undefined -fno-sanitize-recover=all -fno-omit-frame-pointer '
report={'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'official_score':False,'mode':mode,'track':'d','source_sha256':pre['source_sha256'],'manifest_sha256':sha(w/'preflight.json'),'native_report_sha256':sha(w/'native-proof/report.json'),'scope':'Fresh exact querycap6 D286 source under pinned offline restricted Linux/amd64 GCC strict ASAN/UBSAN or one unchanged-permitted-training native-GCC PGO image. All original header primitive proofs retained only by exact bytes. Original996 and later262 reference fixtures/expected hashes are data only; no old source-specific algorithm/main proof substituted. Native/VM time or memory is not organizer K/ELF evidence.'}
def save():(out/'partial.json').write_text(json.dumps(report,indent=2)+'\n')
def run(cmd,label,stdin=None,timeout=1200):
 print('RUN286',mode,label,flush=True);report.setdefault('commands',[]).append({'label':label,'argv':list(map(str,cmd))});save()
 with (out/(label+'.stdout')).open('w') as stdout,(out/(label+'.stderr')).open('w') as stderr:q=subprocess.run(list(map(str,cmd)),input=stdin,text=True,stdout=stdout,stderr=stderr,timeout=timeout)
 assert q.returncode==0,(label,q.returncode,(out/(label+'.stderr')).read_text()[-1800:],(out/(label+'.stdout')).read_text()[-1000:]);return (out/(label+'.stdout')).read_text()
def inventory():
 folders={};jobs={};errors={};expected_by_content={};fresh=set()
 def add(case,expected,threads,origin,explicit=None,recorded=None,error=False,isfresh=False):
  threads=int(threads);assert 1<=threads<=12
  data=Path(explicit) if explicit else next(p for p in [r/'.data/cases'/case,r/'.data/d'/case] if p.is_dir());data=data if data.is_absolute() else r/data;data=data.resolve();data.relative_to(r)
  if str(data) not in folders:
   assert {p.name for p in data.iterdir() if p.is_file()}=={'graph.txt','queries.txt'};folders[str(data)]={p.name:sha(p) for p in data.iterdir() if p.is_file()}
  hashes=folders[str(data)]
  if recorded:assert hashes==recorded,(case,'input changed')
  content=tuple(sorted(hashes.items()));row={'case':case,'data_folder':str(data.relative_to(r)),'threads':threads,'inputs_sha256':hashes,'reference_source':origin}
  if error:errors[(content,threads)]=row
  else:
   assert expected
   if content in expected_by_content:assert expected_by_content[content]==expected,(case,'conflicting references')
   expected_by_content[content]=expected;row['expected_sha256']=expected;jobs[(content,threads)]=row
   if isfresh:fresh.add(content)
 base=read(r/'docs/round262-d-linux-image.json');assert base['passed'] and len(base['runs'])==1556
 for row in base['runs']:add(row['case'],row.get('expected_sha256') or row['sha256'],row['threads'],'docs/round262-d-linux-image.json recorded input/reference only',row['data_folder'],row['inputs_sha256'])
 for row in base['expected_failures']:add(row['case'],None,row['threads'],'docs/round262-d-linux-image.json error input only',row['data_folder'],row['inputs_sha256'],error=True)
 for item in native['runs']:
  data=read(r/item['report']);assert data['passed'];cmd=item['command'];prefix=cmd[cmd.index('--run-id')+1] if '--run-id' in cmd else None
  for row in data.get('checks',[]):
   if not row or row.get('track')!='d':continue
   for sample in row['runs']:add(row['case'],row.get('reference_sha256') or sample['sha256'],sample['requested_threads'],item['report'],row.get('data_folder'),row.get('inputs_sha256'),isfresh=True)
  for row in data.get('malformed',[])+data.get('expected_failures',[]):
   label=row.get('data_case') or (prefix+'-d-pipeline-error-'+row['case'] if prefix else row['case']);add(label,None,row['threads'],item['report'],row.get('data_folder'),row.get('inputs_sha256'),error=True)
 for row in native['direct_runs']:add(row['case'],row['expected_sha256'],row['threads'],'Fresh286 independent Python Floyd/query-count bank',row['data_folder'],row['inputs_sha256'],isfresh=True)
 for row in native['full_public_untrained_runs']:add(row['case'],row['expected_sha256'],row['threads'],'Native286 full-input independent references',row['data_folder'],row['inputs_sha256'],isfresh=True)
 public=read(r/'docs/public-sha256.json')['tracks']['d']
 for threads in [1,6,12]:add('public-full-seed1',public['expected_output_sha256'][0],threads,'Published official full-public hashes',r/'.data/d/public-full-seed1',public['inputs_sha256'])
 return list(jobs.values()),list(errors.values()),folders,fresh
if mode=='build':
 spec=importlib.util.spec_from_file_location('policy286',r/'tools/official/harness/dockerfile_check.py');policy=importlib.util.module_from_spec(spec);spec.loader.exec_module(policy);assert not policy.check((source/'track-d/Dockerfile').read_text(),read(r/'docs/allowlist.json')['images']);run(['docker','build','--platform','linux/amd64','--network=none','-t',tag,str(source/'track-d')],'build',timeout=600);info=json.loads(run(['docker','image','inspect',tag],'inspect'))[0];original=json.loads(run(['docker','image','inspect','sha256:c4d3c407647521f82a295be8f0ebaa3de8d755d121a0439f7ddc5ea51968bb04'],'original-config'))[0];assert info['Architecture']=='amd64' and info['Size']<=2*1024**3
 for key in ['User','Env','Entrypoint','Cmd','WorkingDir']:assert info['Config'].get(key)==original['Config'].get(key),key
 assert info['Config']['User']=='65534:65534' and info['Config']['Entrypoint']==['/app/solution'] and 'MALLOC_ARENA_MAX=2' in info['Config']['Env'] and not any(v.startswith('SPEED_DEMON_THREADS=') for v in info['Config']['Env']);elf=run([*common,'--entrypoint','sha256sum',info['Id'],'/app/solution'],'elf').split()[0];report.update(image_id=info['Id'],image_tag=tag,image_bytes=info['Size'],elf_sha256=elf,image_config=info['Config'],training='Unchanged pinned native GCC/full1000003 then sample130363/default thread budget12, actual query cap6. Only executable enters final image; no publicseed1 training.')
else:
 jobs,errors,folders,fresh=inventory();report.update(original_bank_rows=1556,deduplication='Complete input-content hashes plus requested thread budget; references must agree. Later262 data is reused only as independently expected input/output fixtures, never its bypass-source proof.');image=GCC if mode=='gcc' else read(work/'build/report.json')['image_id'];report['image_id']=image
 if mode=='defaults':
  assert read(work/'image/report.json')['passed'];base=read(r/'docs/round262-d-linux-defaults.json');allowed={tuple(sorted(x['inputs_sha256'].items())) for x in base['runs']}|fresh;allowed_errors={tuple(sorted(x['inputs_sha256'].items())) for x in base['expected_failures']};unique={tuple(sorted(x['inputs_sha256'].items())):dict(x) for x in jobs if tuple(sorted(x['inputs_sha256'].items())) in allowed};errunique={tuple(sorted(x['inputs_sha256'].items())):dict(x) for x in errors if tuple(sorted(x['inputs_sha256'].items())) in allowed_errors};runs=[];failed=[]
  for number,row in enumerate(unique.values()):
   dest=out/f'valid-{number}';marker=out/f'default-{number}.pass.json'
   if marker.exists():old=read(marker);assert old['sha256']==row['expected_sha256']==sha(dest/'distances.txt');runs.append(old);continue
   dest.mkdir(exist_ok=True);dest.chmod(0o777);run([*common,'-v',str(r/row['data_folder'])+':/data:ro','-v',str(dest)+':/out:rw',image],f'default-{number}',timeout=180);assert not (out/f'default-{number}.stdout').read_bytes() and not (out/f'default-{number}.stderr').read_bytes();assert [p.name for p in dest.iterdir()]==['distances.txt'];row['sha256']=sha(dest/'distances.txt');assert row['sha256']==row['expected_sha256'];qcount=len((r/row['data_folder']/'queries.txt').read_text().split())//2;row.update(configured_default_thread_budget=12,graph_loader_cap=12,effective_query_workers=min(12,qcount,6),query_count=qcount,source_fixture_threads=row.pop('threads'));marker.write_text(json.dumps(row,indent=2)+'\n');runs.append(row);report['runs']=runs;save()
  for number,row in enumerate(errunique.values()):
   dest=out/f'error-{number}';dest.mkdir(exist_ok=True);dest.chmod(0o777);q=subprocess.run([*common,'-v',str(r/row['data_folder'])+':/data:ro','-v',str(dest)+':/out:rw',image],capture_output=True,text=True,timeout=180);assert q.returncode==1 and not q.stdout and q.stderr.startswith('track-d:') and not any(x in q.stderr for x in ['Sanitizer','runtime error:','DEADLYSIGNAL']);row.update(returncode=q.returncode,stderr=q.stderr,source_fixture_threads=row.pop('threads'),configured_default_thread_budget=12,query_worker_cap=6);failed.append(row)
  report.update(runs=runs,expected_failures=failed,arguments=[],thread_override=False,default_selection='Unique recorded262 default inputs plus all fresh286 Floyd/query-count/sample/adversarial/full reference inputs; true entrypoint/no arguments/no SPEED_DEMON_THREADS override. Default budget12/graph12, effective query workers=min(12,Q,6). Full production reference bank separately image-replayed.')
 else:
  if mode=='gcc':jobs=[x for x in jobs if x['threads'] in [1,6,12]];errors=[x for x in errors if x['threads'] in [1,6,12]]
  script=['set -eu','export ASAN_OPTIONS=halt_on_error=1','export UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1','mkdir -p /out/stdio'];binary='/app/solution'
  if mode=='gcc':
   marker=out/'solution.sha256';binary='/out/solution'
   if marker.exists():assert sha(out/'solution')==marker.read_text().split()[0]
   else:script +=[flags+shlex.quote('/repo/'+str((source/'track-d/main.cpp').relative_to(r)))+' -o /out/solution','sha256sum /out/solution >/out/solution.sha256.tmp','mv /out/solution.sha256.tmp /out/solution.sha256']
  for number,row in enumerate(jobs):
   marker=out/'stdio'/f'{number}.code';dest=out/f'valid-{number}'
   if marker.exists():assert marker.read_text().strip()=='0' and sha(dest/'distances.txt')==row['expected_sha256'] and not (out/'stdio'/f'{number}.out').read_bytes() and not (out/'stdio'/f'{number}.err').read_bytes();continue
   script+=['set +e','SPEED_DEMON_THREADS='+str(row['threads'])+' '+binary+' --data '+shlex.quote('/repo/'+row['data_folder'])+' --out /out/'+dest.name+' >/out/stdio/'+str(number)+'.out 2>/out/stdio/'+str(number)+'.err','code=$?','set -e','echo "$code" >/out/stdio/'+str(number)+'.code','test "$code" -eq 0']
  for number,row in enumerate(errors):
   marker=out/'stdio'/f'error-{number}.code'
   if marker.exists():assert marker.read_text().strip()=='1';continue
   script+=['set +e','SPEED_DEMON_THREADS='+str(row['threads'])+' '+binary+' --data '+shlex.quote('/repo/'+row['data_folder'])+' --out /out/error-'+str(number)+' >/out/stdio/error-'+str(number)+'.out 2>/out/stdio/error-'+str(number)+'.err','code=$?','set -e','echo "$code" >/out/stdio/error-'+str(number)+'.code','test "$code" -eq 1']
  run([*common,'-i','--entrypoint','/bin/sh','-v',str(r)+':/repo:ro','-v',str(out)+':/out:rw',image,'-s'],'replay','\n'.join(script)+'\n',timeout=1200);assert not (out/'replay.stderr').read_bytes(),(out/'replay.stderr').read_text()[-1800:]
  for number,row in enumerate(jobs):
   dest=out/f'valid-{number}';assert [p.name for p in dest.iterdir()]==['distances.txt'];assert (out/'stdio'/f'{number}.code').read_text().strip()=='0' and not (out/'stdio'/f'{number}.out').read_bytes() and not (out/'stdio'/f'{number}.err').read_bytes();row['sha256']=sha(dest/'distances.txt');assert row['sha256']==row['expected_sha256']
  for number,row in enumerate(errors):
   assert (out/'stdio'/f'error-{number}.code').read_text().strip()=='1' and not (out/'stdio'/f'error-{number}.out').read_bytes();err=(out/'stdio'/f'error-{number}.err').read_text();assert err.startswith('track-d:') and not any(x in err for x in ['Sanitizer','runtime error:','DEADLYSIGNAL']);row['stderr']=err
  report.update(runs=jobs,expected_failures=errors)
  if mode=='gcc':report['compiled_binary_sha256']=sha(out/'solution')
 for folder,hashes in folders.items():assert {p.name:sha(p) for p in Path(folder).iterdir() if p.is_file()}==hashes
for rel,h in pre['source_sha256'].items():assert sha(source/rel)==h
report.update(passed=True,completed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(r/f'docs/round286-d-linux-{mode}.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS286 Linux',mode,len(report.get('runs',[])),len(report.get('expected_failures',[])),flush=True)
