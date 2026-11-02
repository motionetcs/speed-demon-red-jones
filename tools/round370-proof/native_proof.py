from pathlib import Path
import datetime,hashlib,json,os,subprocess
r=Path.cwd();w=r/'.build/round370';s=w/'source';out=w/'native-proof';out.mkdir(exist_ok=True)
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
pre=read(w/'preflight.json');screen=read(w/'confirmation/report.json');old=read(r/'.build/round356/native-proof/report.json');assert screen['passed']and old['passed'];assert not(out/'report.json').exists()
files={name:sha(w/name)for name in ['raw_fields_model.cpp','csv_model.hpp']};manifest={'created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'preflight_sha256':sha(w/'preflight.json'),'source_sha256':pre['source_sha256'],'model_files_sha256':files,'scope':'Fresh370 constructed-field/header-equivalence/boundary/long/all-byte rawlexer model under failfastASAN/UBSAN; NEWcurrentmain ASAN+TSAN replay356saved input/referencebytes, no regenerated/oracled oldfixtures. Originalheader-only Names/queue/numeric/source protocols retainedONLYby exactbytes, no356/357newqueue/startupcallback proof transferred to original370 protocol. Newfresh3851/3853samples/3863full generated once and officialreference-compared. GNU/image/default/actual stillrequired.'};dump(w/'proof-manifest.json',manifest)
for p,h in pre['source_sha256'].items():assert sha(s/p)==h,p
for p,h in pre['root_selected_bindings'].items():assert sha(r/p)==h,p
report={'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'official_score':False,'selected_in_root':False,'scope':manifest['scope'],'source_sha256':pre['source_sha256'],'model_files_sha256':files,'unchanged_headers_sha256':pre['unchanged_C_headers_sha256'],'compiles':[],'models':[],'matrices':[]};env=dict(os.environ,ASAN_OPTIONS='halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1',TSAN_OPTIONS='halt_on_error=1')
def save():dump(out/'partial.json',report)
def compile(label,unit,binary,flags):
 assert not binary.exists();argv=['clang++','-std=c++20','-O1','-g','-Wall','-Wextra','-Wpedantic','-Werror','-pthread','-fno-omit-frame-pointer',*flags,str(unit),'-o',str(binary)];q=subprocess.run(argv,capture_output=True,text=True,timeout=240);row={'label':label,'command':argv,'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr};dump(binary.with_suffix('.compile-attempt.json'),row);assert q.returncode==0 and not q.stdout and not q.stderr,(label,q.returncode,q.stderr[-2500:]);row['binary_sha256']=sha(binary);dump(binary.with_suffix('.compile.json'),row);report['compiles'].append(row);save()
def inventory(mode):
 jobs={};errors={};folders={};expected_by_content={}
 def add(label,expected,threads,origin,explicit=None,recorded=None,error=False):
  data=Path(explicit)if explicit else next(p for p in[r/'.data/cases'/label,r/'.data/c'/label]if p.is_dir());data=data if data.is_absolute()else r/data;data=data.resolve();data.relative_to(r);hashes={p.name:sha(p)for p in data.iterdir()if p.is_file()};assert set(hashes)=={'records.csv','regions.csv'}
  if recorded:assert hashes==recorded,(label,'inputchanged')
  folders[str(data)]=hashes;content=tuple(sorted(hashes.items()));row={'case':label,'data_folder':str(data.relative_to(r)),'threads':int(threads),'inputs_sha256':hashes,'reference_source':origin}
  if error:row['returncode']=1;errors[(content,int(threads))]=row
  else:
   assert expected
   if content in expected_by_content:assert expected_by_content[content]==expected
   expected_by_content[content]=expected;row['expected_sha256']=expected;jobs[(content,int(threads))]=row
 for item in old['runs']:
  if not(item['suite'].startswith(mode+'-')):continue
  x=read(r/item['report']);assert x['passed'];argv=item['command'];prefix=argv[argv.index('--run-id')+1]if '--run-id'in argv else None
  for row in x.get('checks',[]):
   assert row.get('track','c')=='c'
   for trial in row['runs']:add(row['case'],row.get('reference_sha256')or trial['sha256'],trial.get('requested_threads',trial.get('threads')),item['report']+' input/referenceONLY',row.get('data_folder'),row.get('inputs_sha256'))
  for row in x.get('expected_failures',[]):
   label=row.get('data_case')or(prefix+'-'+row['case']if prefix else row['case']);add(label,None,row['threads'],item['report']+' inputONLY',row.get('data_folder'),row.get('inputs_sha256'),error=True)
 if mode=='asan':
  for row in old['full_public_untrained_runs']:add(row['case'],row['expected_sha256'],row['threads'],'356savedfullreferencebytesONLY',row['data_folder'],row['inputs_sha256'])
 return list(jobs.values()),list(errors.values()),folders
for mode,flags in [('asan',['-fsanitize=address,undefined','-fno-sanitize-recover=all']),('tsan',['-fsanitize=thread'])]:
 folder=out/mode;folder.mkdir(exist_ok=True)
 if mode=='asan':
  binary=folder/'field-model';compile(mode+'-field-model',w/'raw_fields_model.cpp',binary,flags);q=subprocess.run([str(binary)],capture_output=True,text=True,env=env,timeout=300);row={'mode':mode,'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr,'binary_sha256':sha(binary)};dump(folder/'model-attempt.json',row);assert q.returncode==0 and q.stdout.startswith('PASS370')and not q.stderr,(q.returncode,q.stdout,q.stderr[-2500:]);row['passed']=True;dump(folder/'model.json',row);report['models'].append(row);save();print('PASS370 constructed field/header model',flush=True)
 binary=folder/'track-c';compile(mode+'-main',s/'track-c/main.cpp',binary,flags);jobs,errors,folders=inventory(mode);matrix={'mode':mode,'binary_sha256':sha(binary),'runs':[],'expected_failures':[],'scope':'NEW370exactsource executions on356saved independentreference/data bytes only, deduplicatedcontent+thread. No generator/oracle repeat or356sourceproofsubstitution.'}
 for n,row in enumerate(jobs):
  dest=folder/'outputs'/('valid-'+str(n));dest.mkdir(parents=True);q=subprocess.run([str(binary),'--data',str(r/row['data_folder']),'--out',str(dest)],capture_output=True,text=True,env=dict(env,SPEED_DEMON_THREADS=str(row['threads'])),timeout=180);assert q.returncode==0 and not q.stdout and not q.stderr,(mode,row['case'],row['threads'],q.returncode,q.stderr[-2000:]);assert[p.name for p in dest.iterdir()]==['aggregates.txt'];row['sha256']=sha(dest/'aggregates.txt');assert row['sha256']==row['expected_sha256'];matrix['runs'].append(row);dump(folder/'matrix-partial.json',matrix)
 for n,row in enumerate(errors):
  dest=folder/'outputs'/('error-'+str(n));dest.mkdir(parents=True);q=subprocess.run([str(binary),'--data',str(r/row['data_folder']),'--out',str(dest)],capture_output=True,text=True,env=dict(env,SPEED_DEMON_THREADS=str(row['threads'])),timeout=30);assert q.returncode==1 and not q.stdout and q.stderr.startswith('track-c:')and not any(t in q.stderr for t in['Sanitizer','runtime error:','DEADLYSIGNAL']),(mode,row['case'],q.returncode,q.stderr[-2000:]);row['stderr']=q.stderr;matrix['expected_failures'].append(row);dump(folder/'matrix-partial.json',matrix)
 for data,hashes in folders.items():assert{p.name:sha(p)for p in Path(data).iterdir()if p.is_file()}==hashes
 matrix.update(passed=True);dump(folder/'matrix.json',matrix);dump(r/f'docs/round370-c-native-{mode}-matrix.json',matrix);report['matrices'].append({'mode':mode,'path':str((folder/'matrix.json').relative_to(r)),'sha256':sha(folder/'matrix.json'),'valid_calls':len(matrix['runs']),'normal_errors':len(matrix['expected_failures'])});save();print('PASS370',mode,'main',len(matrix['runs']),len(matrix['expected_failures']),flush=True)
report['fresh_suites']=[]
for mode,scale,seed in [('asan','sample',3851),('tsan','sample',3853),('asan','full',3863)]:
 path=r/f'docs/round370-c-{mode}-fresh-{scale}{seed}.json';assert not path.exists()and not(r/f'.data/c/{scale}-seed{seed}').exists(),'Do not duplicate generator/reference work';argv=['python3','tools/verify.py','--run-id',f'round370-{mode}-fresh-{scale}{seed}','--source-root',str(s),'--binary-dir',str(out/mode),'--tracks','c','--threads','1','6','12','--scale',scale,'--seeds',str(seed),'--report',str(path)]
 if scale=='full':argv.append('--skip-adversarial')
 print('RUN370 fresh',mode,scale,seed,flush=True);q=subprocess.run(argv,cwd=r,capture_output=True,text=True,env=dict(env,PYTHONPATH=str(r/'tools')),timeout=1200);(out/f'fresh-{mode}-{seed}.stdout').write_text(q.stdout);(out/f'fresh-{mode}-{seed}.stderr').write_text(q.stderr);row={'mode':mode,'scale':scale,'seed':seed,'command':argv,'returncode':q.returncode,'path':str(path.relative_to(r))};report['fresh_suites'].append(row);save();assert q.returncode==0 and read(path)['passed'],(q.returncode,q.stdout[-1200:],q.stderr[-2500:]);row['sha256']=sha(path);save()
for p,h in pre['source_sha256'].items():assert sha(s/p)==h,p
for p,h in files.items():assert sha(w/p)==h,p
for p,h in pre['root_selected_bindings'].items():assert sha(r/p)==h,p
report.update(passed=True,completed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());dump(out/'report.json',report);dump(r/'docs/round370-c-native-proof.json',report);print('PASS370 rawfield/header-equivalence exactmodel/main strict proof; GNU/image/actual pending',flush=True)
