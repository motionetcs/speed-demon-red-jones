from pathlib import Path
import datetime,hashlib,json,os,subprocess
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round384';s=w/'source';out=w/'native-proof';out.mkdir(exist_ok=True);sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();read=lambda p:json.loads(Path(p).read_text());dump=lambda p,x:Path(p).write_text(json.dumps(x,indent=2)+'\n');pre=read(w/'final-source.json');assert not(out/'report.json').exists()
for p,h in pre['source_sha256'].items():assert sha(s/p)==h
for p,h in pre['root_selected_bindings'].items():assert sha(r/p)==h
report={'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_sha256':pre['source_sha256'],'final_manifest_sha256':sha(w/'final-source.json'),'scope':'Fresh exact-final384 main ASAN/UBSAN(no recovery) and TSAN, fresh actual changed-header fixed4/generic0/dispatch/stdset/arena/private-owner model in both modes. Source-independent370 saved data/reference bytes reused ONLY as fixtures, no old source proof or generator/oracle/PGO repetition. New country fixtures each1..12 plus untrained3863/full public and source-bound unchanged headers. Native timing/heap not target score.','official_score':False,'selected_in_root':False,'compiles':[],'models':[],'matrices':[]};env=dict(os.environ,ASAN_OPTIONS='halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1',TSAN_OPTIONS='halt_on_error=1')
def save():dump(out/'partial.json',report)
def compile(label,unit,binary,flags):
 marker=binary.with_suffix('.compile.json')
 if marker.exists():row=read(marker);assert row['returncode']==0 and sha(binary)==row['binary_sha256'];report['compiles'].append(row);return
 assert not binary.exists();argv=['clang++','-std=c++20','-O1','-g','-Wall','-Wextra','-Wpedantic','-Werror','-pthread','-fno-omit-frame-pointer',*flags,str(unit),'-o',str(binary)];q=subprocess.run(argv,capture_output=True,text=True,timeout=240);row={'label':label,'argv':argv,'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr};dump(binary.with_suffix('.compile-attempt.json'),row);assert q.returncode==0 and not q.stdout and not q.stderr,(label,q.stderr[-2500:]);row['binary_sha256']=sha(binary);dump(marker,row);report['compiles'].append(row);save()
def inventory(mode):
 bank=read(r/f'docs/round370-c-native-{mode}-matrix.json');assert bank['passed'];jobs={};errors={};folders={};expected_by_content={}
 def add(row,error=False):
  row=dict(row);data=(r/row['data_folder']).resolve();data.relative_to(r);hashes={p.name:sha(p)for p in data.iterdir()if p.is_file()};assert hashes==row['inputs_sha256'];content=tuple(sorted(hashes.items()));folders[str(data)]=hashes;row['data_folder']=str(data.relative_to(r));row['reference_source']=row.get('reference_source','370 saved input/expected bytes ONLY; not old source proof');expected=row.get('expected_sha256',row.get('reference_sha256',row.get('sha256')));row.pop('sha256',None)
  if error:errors[(content,row['threads'])]=row
  else:
   assert expected
   if content in expected_by_content:assert expected_by_content[content]==expected
   expected_by_content[content]=expected;row['expected_sha256']=expected;jobs[(content,row['threads'])]=row
 for row in bank['runs']:add(row)
 for row in bank['expected_failures']:add(row,True)
 heads=read(r/'docs/round370-c-header-integration.json');assert heads['passed']
 for error,rows in [(False,heads['checks']),(True,heads['expected_failures'])]:
  for row in rows:
   for threads in [1,6,12]:add(dict(row,threads=threads,reference_source='370 saved header compatibility byte oracle; BOM+quoted-first extension uses official hand-computed payload, not unsupported official-reference pass'),error)
 for row in pre['fixtures']:
  for threads in row['threads']:add(dict(row,threads=threads,reference_source=row['reference']))
 for path in ['docs/round370-c-asan-fresh-sample3851.json','docs/round370-c-tsan-fresh-sample3853.json','docs/round370-c-asan-fresh-full3863.json']:
  doc=read(r/path);assert doc['passed']
  for row in doc['checks']:
   if row.get('track','c')!='c':continue
   if 'data_folder'not in row:
    candidates=[r/'.data/c'/row['case'],r/'.data/cases'/row['case']];data=next(p for p in candidates if p.is_dir());row=dict(row,data_folder=str(data.relative_to(r)),inputs_sha256={p.name:sha(p)for p in data.iterdir()if p.is_file()})
   for threads in [1,6,12]:add(dict(row,threads=threads,reference_source=path+' input/reference ONLY'))
 return list(jobs.values()),list(errors.values()),folders
for mode,flags in [('asan',['-fsanitize=address,undefined','-fno-sanitize-recover=all']),('tsan',['-fsanitize=thread'])]:
 folder=out/mode;folder.mkdir(exist_ok=True);model=folder/'names-model';compile(mode+'-names-model',w/'fixed_words_model.cpp',model,flags);marker=folder/'model.json'
 if marker.exists():row=read(marker);assert row['passed']and row['binary_sha256']==sha(model)
 else:
  q=subprocess.run([str(model)],capture_output=True,text=True,env=env,timeout=600);row={'mode':mode,'argv':[str(model)],'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr,'binary_sha256':sha(model)};dump(folder/'model-attempt.json',row);assert q.returncode==0 and 'PASS384'in q.stdout and not q.stderr,(q.returncode,q.stdout,q.stderr[-2500:]);row['passed']=True;dump(marker,row)
 report['models'].append(row);save();print('PASS384',mode,'fresh fixed4/generic0 actual-header model',flush=True)
 binary=folder/'track-c';compile(mode+'-main',s/'track-c/main.cpp',binary,flags);jobs,errors,folders=inventory(mode);matrix={'mode':mode,'binary_sha256':sha(binary),'runs':[],'expected_failures':[],'scope':'New exact-final384 main runs. Saved370 independent data/reference bytes only; new384 country boundary fixtures and every1..12; untrained full3863 and samples; full-public hashes. No old source certificate reused.'}
 for error,rows in [(False,jobs),(True,errors)]:
  for number,row in enumerate(rows):
   label=('error-'if error else'valid-')+str(number);dest=folder/'outputs'/label;marker=folder/'markers'/(label+'.json');marker.parent.mkdir(exist_ok=True)
   if marker.exists():trial=read(marker);assert trial['case']==row['case']and trial['threads']==row['threads']and trial['inputs_sha256']==row['inputs_sha256'];assert error or sha(dest/'aggregates.txt')==row['expected_sha256']==trial['sha256']
   else:
    dest.mkdir(parents=True);q=subprocess.run([str(binary),'--data',str(r/row['data_folder']),'--out',str(dest)],capture_output=True,text=True,env=dict(env,SPEED_DEMON_THREADS=str(row['threads'])),timeout=180);assert q.returncode==(1 if error else 0)and not q.stdout,(mode,row['case'],q.returncode,q.stderr[-2000:]);trial=dict(row)
    if error:assert q.stderr.startswith('track-c:')and not any(x in q.stderr for x in ['Sanitizer','runtime error:','DEADLYSIGNAL']);trial['stderr']=q.stderr
    else:assert not q.stderr and[p.name for p in dest.iterdir()]==['aggregates.txt'];trial['sha256']=sha(dest/'aggregates.txt');assert trial['sha256']==row['expected_sha256']
    dump(marker,trial)
   matrix['expected_failures'if error else'runs'].append(trial)
   if number%20==0:dump(folder/'matrix-partial.json',matrix)
 for data,hashes in folders.items():assert{p.name:sha(p)for p in Path(data).iterdir()if p.is_file()}==hashes
 matrix['passed']=True;dump(folder/'matrix.json',matrix);dump(r/f'docs/round384-c-native-{mode}-matrix.json',matrix);report['matrices'].append({'mode':mode,'path':str((folder/'matrix.json').relative_to(r)),'sha256':sha(folder/'matrix.json'),'valid_calls':len(matrix['runs']),'normal_errors':len(matrix['expected_failures'])});save();print('PASS384',mode,'current main',len(matrix['runs']),len(matrix['expected_failures']),flush=True)
for p,h in pre['source_sha256'].items():assert sha(s/p)==h
for p,h in pre['root_selected_bindings'].items():assert sha(r/p)==h
report.update(passed=True,completed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());dump(out/'report.json',report);dump(r/'docs/round384-c-native-proof.json',report);print('PASS384 all native strict/race proof; GNU/image/default/real still required',flush=True)
