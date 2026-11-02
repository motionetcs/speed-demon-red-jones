from pathlib import Path
import collections,datetime,hashlib,importlib.util,json,os,random,shutil,subprocess
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round376';s=w/'source';out=w/'native-proof';assert not out.exists();out.mkdir()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def dump(p,j):p.write_text(json.dumps(j,indent=2)+'\n')
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
pre=read(w/'preflight.json');model=read(w/'partition-model-manifest.json');assert read(w/'fresh-confirmation/report.json')['passed']
for p,h in pre['source_sha256'].items():assert sha(s/p)==h,p
for p,h in pre['root_selected_bindings'].items():assert sha(r/p)==h,p
for p,h in model['model_files'].items():assert sha(w/p)==h,p
report={'started_at_utc':now(),'official_score':False,'selected_in_root':False,'source_sha256':pre['source_sha256'],'scope':'A376 source-specific strict ASAN/UBSAN and TSAN actual partition/claim independent model plus actual main. Saved342 data/reference bytes reused by hash only, no old execution proof or generation/reference repeated. New shuffled multi-job/4096endpoint/full32escape fixture has independent full-sort oracle and one official-reference comparison; fresh3923/3929 samples generated once. Original cache/allocator/writer/decimal headers unchanged, retained only as provenance.','compiles':[],'models':[],'matrices':[],'fresh_suites':[]};env=dict(os.environ,ASAN_OPTIONS='halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1',TSAN_OPTIONS='halt_on_error=1')
def save():dump(out/'partial.json',report)
def compile(mode,source,binary,flags):
 assert not binary.exists();argv=['clang++','-std=c++20','-O1','-g','-Wall','-Wextra','-Wpedantic','-Werror','-pthread','-fno-omit-frame-pointer',*flags,str(source),'-o',str(binary)];q=subprocess.run(argv,capture_output=True,text=True,timeout=240);row={'mode':mode,'source':str(source.relative_to(r)),'command':argv,'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr};report['compiles'].append(row);dump(binary.with_suffix('.compile-attempt.json'),row);save();assert q.returncode==0 and not q.stdout and not q.stderr,(q.returncode,q.stderr);row['binary_sha256']=sha(binary);save()

# New fixture semantics are generated independently of the production parser.
fixture=w/'dynamic-fixtures';fixture.mkdir();valid=fixture/'shuffled-all-ids';valid.mkdir();rng=random.Random(3763911);methods=['GET','POST','PUT','DELETE','PATCH','HEAD','OPTIONS'];statuses=[100,200,499,500,599]
paths=['/'if i==0 else('/'+('x'*(119-len(str(i))))+'/'+str(i)).ljust(125,'z')for i in range(4096)]
assert len(set(paths))==4096 and all(1<=len(x)<=125 for x in paths)
base=datetime.datetime(2026,10,30,18,tzinfo=datetime.timezone.utc);labels={h:(base+datetime.timedelta(hours=h)).strftime('%Y-%m-%dT%H:00:00Z')for h in [0,71]};timestamps={h:(base+datetime.timedelta(hours=h)).strftime('%Y-%m-%dT%H:%M:%S.000000Z')for h in [0,71]}
order=list(range(325000));rng.shuffle(order);values=collections.defaultdict(list);errors=collections.Counter();file=valid/'requests.log'
with file.open('wb')as f:
 for i in order:
  endpoint=paths[i%4096];hour=71 if(i//4096)%2 else 0;latency=[0,524286,524287,524288,4294967295,(i*2654435761)&0xffffffff][i%6];status=statuses[i%5];key=(hour,endpoint);values[key].append(latency);errors[key]+=500<=status<=599
  f.write(f'{timestamps[hour]} {methods[i%7]} {endpoint} {status} {latency}\n'.encode('ascii'))
assert file.stat().st_size>12*(1<<22),'Fixture must activate more than12 production parser jobs'
lines=[]
for key,array in sorted(values.items()):
 array.sort();n=len(array);quantiles=[array[(n*p+99)//100-1]for p in[50,95,99]];e=errors[key];lines.append(f'{labels[key[0]]} {key[1]} {n} {quantiles[0]} {quantiles[1]} {quantiles[2]} {e} {e*1000000//n}\n')
independent=''.join(lines).encode('ascii');(fixture/'independent-summary.txt').write_bytes(independent)
spec=importlib.util.spec_from_file_location('a376_official_reference',r/'tools/official/reference/a_ingest.py');reference=importlib.util.module_from_spec(spec);spec.loader.exec_module(reference);reference.main(str(valid),str(fixture/'official-reference'));assert(fixture/'official-reference/summary.txt').read_bytes()==independent
late=fixture/'late-invalid-latency';late.mkdir();shutil.copyfile(file,late/'requests.log')
with(late/'requests.log').open('ab')as f:f.write((timestamps[0]+' GET /bad 200 4294967296\n').encode())
empty=fixture/'empty';empty.mkdir();(empty/'requests.log').write_bytes(b'')
fixture_report={'passed':True,'official_score':False,'scope':'One new325000-row52MB+ shuffled fixture activates>12 production4MiB jobs,4096 distinct ASCII endpoints, first/last hours, every method/status boundary and complete uint32 latency escapes; separate full-sort quantiles match one official-reference invocation. Empty and appended out-of-range-latency fixtures are separately labeled. No cached runtime answers.','rows':325000,'valid':{'case':'round376-shuffled-all-ids','data_folder':str(valid.relative_to(r)),'inputs_sha256':{'requests.log':sha(file)},'expected_sha256':hashlib.sha256(independent).hexdigest()},'empty':{'case':'round376-empty','data_folder':str(empty.relative_to(r)),'inputs_sha256':{'requests.log':sha(empty/'requests.log')},'expected_sha256':hashlib.sha256(b'').hexdigest()},'invalid':{'case':'round376-late-invalid-latency','data_folder':str(late.relative_to(r)),'inputs_sha256':{'requests.log':sha(late/'requests.log')},'expected_returncode':1,'scope':'Out-of-domain normal-error fixture, no official-reference pass claimed.'},'generator_driver':str(Path(__file__).relative_to(r))};dump(w/'dynamic-fixtures/report.json',fixture_report);dump(r/'docs/round376-a-dynamic-fixtures.json',fixture_report);report['new_fixtures']={'path':'docs/round376-a-dynamic-fixtures.json','sha256':sha(r/'docs/round376-a-dynamic-fixtures.json')};save()

old=read(r/'.build/round342/native-proof/report.json')
def inventory(mode):
 jobs={}
 def add(label,expected,threads,explicit=None,recorded=None,origin='saved input/reference bytes only'):
  candidates=[r/'.data/a'/label,r/'.data/cases'/label]
  data=Path(explicit)if explicit else next(p for p in candidates if p.is_dir());data=data if data.is_absolute()else r/data;data=data.resolve();data.relative_to(r);hashes={p.name:sha(p)for p in data.iterdir()if p.is_file()};assert set(hashes)=={'requests.log'}
  if recorded:assert hashes==recorded
  row={'case':label,'data_folder':str(data.relative_to(r)),'threads':int(threads),'inputs_sha256':hashes,'expected_sha256':expected,'reference_source':origin};key=(tuple(sorted(hashes.items())),int(threads))
  if key in jobs:assert jobs[key]['expected_sha256']==expected
  jobs[key]=row
 for item in old['integrations']:
  if item['mode']!=mode:continue
  path=r/item['report'];x=read(path);assert x['passed']and sha(path)==item['report_sha256']
  for row in x['checks']:
   for trial in row['runs']:add(row['case'],row.get('reference_sha256')or trial['sha256'],trial['requested_threads'],row.get('data_folder'),row.get('inputs_sha256'),item['report'])
 for case in read(w/'confirmation/report.json')['cases']:
  for threads in [1,6,12]:add(case['case'],case['expected_sha256'],threads,case['data_folder'],case['inputs_sha256'],'376screen saved source-independent full refs')
 fresh=read(r/'docs/round376-a-native-fresh-full3911.json')
 if mode=='asan':
  for row in fresh['checks']:
   for trial in row['runs']:add(row['case'],row['reference_sha256'],trial['requested_threads'],origin='376 independent full3911 reference bytes only')
 for name in ['valid','empty']:
  row=fixture_report[name]
  for threads in range(1,13):add(row['case'],row['expected_sha256'],threads,row['data_folder'],row['inputs_sha256'],'new376 independent oracle and official-ref where supported')
 return list(jobs.values())
for mode,flags in [('asan',['-fsanitize=address,undefined','-fno-sanitize-recover=all']),('tsan',['-fsanitize=thread'])]:
 folder=out/mode;folder.mkdir();compile(mode,w/'partitions_model.cpp',folder/'partition-model',flags);q=subprocess.run([str(folder/'partition-model')],capture_output=True,text=True,env=env,timeout=300);row={'mode':mode,'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr,'binary_sha256':sha(folder/'partition-model')};dump(folder/'model-attempt.json',row);assert q.returncode==0 and q.stdout.startswith('PASS376')and not q.stderr,(mode,q.returncode,q.stdout,q.stderr);row['passed']=True;report['models'].append(row);save();print('PASS376',mode,'partition/claim model',q.stdout.strip(),flush=True)
 compile(mode,s/'track-a/main.cpp',folder/'track-a',flags);jobs=inventory(mode);matrix={'mode':mode,'binary_sha256':sha(folder/'track-a'),'runs':[],'expected_failures':[],'scope':'New actual376 source executions; reused inputs/references by exact content and thread, not old342 source proof. New large shuffled and empty fixtures every1..12 workers.'}
 for n,row in enumerate(jobs):
  dest=folder/'outputs'/('valid-'+str(n));dest.mkdir(parents=True);q=subprocess.run([str(folder/'track-a'),'--data',str(r/row['data_folder']),'--out',str(dest)],capture_output=True,text=True,env=dict(env,SPEED_DEMON_THREADS=str(row['threads'])),timeout=180);assert q.returncode==0 and not q.stdout and not q.stderr,(mode,row['case'],row['threads'],q.returncode,q.stderr[-2000:]);assert[p.name for p in dest.iterdir()]==['summary.txt'];row['sha256']=sha(dest/'summary.txt');assert row['sha256']==row['expected_sha256'];matrix['runs'].append(row);dump(folder/'matrix-partial.json',matrix)
 for kind in ['late-invalid','output-open']:
  data=late if kind=='late-invalid'else empty
  for threads in [1,6,12]:
   dest=folder/'outputs'/(kind+'-'+str(threads));dest.mkdir(parents=True)
   if kind=='output-open':(dest/'summary.txt').mkdir()
   q=subprocess.run([str(folder/'track-a'),'--data',str(data),'--out',str(dest)],capture_output=True,text=True,env=dict(env,SPEED_DEMON_THREADS=str(threads)),timeout=180);assert q.returncode==1 and not q.stdout and q.stderr.startswith('track-a:')and not any(x in q.stderr for x in['Sanitizer','runtime error:','DEADLYSIGNAL']),(mode,kind,threads,q.returncode,q.stderr)
   if kind=='late-invalid':assert not(dest/'summary.txt').exists()
   matrix['expected_failures'].append({'case':kind,'data_folder':str(data.relative_to(r)),'threads':threads,'inputs_sha256':{'requests.log':sha(data/'requests.log')},'returncode':q.returncode,'stderr':q.stderr})
 for row in jobs:assert{p.name:sha(p)for p in(r/row['data_folder']).iterdir()if p.is_file()}==row['inputs_sha256']
 matrix['passed']=True;dump(folder/'matrix.json',matrix);dump(r/f'docs/round376-a-native-{mode}-matrix.json',matrix);report['matrices'].append({'mode':mode,'path':str((folder/'matrix.json').relative_to(r)),'sha256':sha(folder/'matrix.json'),'valid_calls':len(jobs),'normal_errors':len(matrix['expected_failures'])});save();print('PASS376',mode,'current main',len(jobs),len(matrix['expected_failures']),flush=True)
 seed=3923 if mode=='asan'else 3929;path=r/f'docs/round376-a-{mode}-fresh-sample{seed}.json';assert not path.exists()and not(r/f'.data/a/sample-seed{seed}').exists();argv=['python3','tools/verify.py','--run-id',f'round376-{mode}-fresh-sample{seed}','--source-root',str(s),'--binary-dir',str(folder),'--tracks','a','--threads','1','6','12','--scale','sample','--seeds',str(seed),'--skip-adversarial','--report',str(path)];q=subprocess.run(argv,cwd=r,capture_output=True,text=True,env=dict(env,PYTHONPATH=str(r/'tools')),timeout=900);(folder/'fresh.stdout').write_text(q.stdout);(folder/'fresh.stderr').write_text(q.stderr);assert q.returncode==0 and read(path)['passed'],(q.returncode,q.stdout[-1500:],q.stderr[-1500:]);report['fresh_suites'].append({'mode':mode,'path':str(path.relative_to(r)),'sha256':sha(path),'command':argv});save()
for p,h in pre['source_sha256'].items():assert sha(s/p)==h,p
for p,h in pre['root_selected_bindings'].items():assert sha(r/p)==h,p
for p,h in model['model_files'].items():assert sha(w/p)==h,p
report.update(passed=True,completed_at_utc=now());dump(out/'report.json',report);dump(r/'docs/round376-a-native-proof.json',report);print('PASS376 exact native partition/claim/currentmain/independent/strict/race/untrained; GNU/image/actual pending',flush=True)
