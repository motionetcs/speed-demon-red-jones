from pathlib import Path
import datetime,hashlib,json,os,re,statistics,subprocess,time
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round323';s=w/'source';outroot=w/'confirmation';outroot.mkdir(exist_ok=True)
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
pre=read(w/'preflight.json');assert not (outroot/'report.json').exists()
for name,digest in pre['source_sha256'].items():assert sha(s/name)==digest
candidate=w/'track-c-bin';control=Path(pre['control_binary']);assert not candidate.exists();cmd=['clang++','-std=c++20','-O3','-DNDEBUG','-Wall','-Wextra','-Wpedantic','-pthread',str(s/'track-c/main.cpp'),'-o',str(candidate)];q=subprocess.run(cmd,capture_output=True,text=True,timeout=180);(w/'compile.json').write_text(json.dumps({'command':cmd,'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr},indent=2)+'\n');assert q.returncode==0 and not q.stderr and not q.stdout,q.stderr;pre['candidate_binary_sha256']=sha(candidate);assert sha(control)==pre['control_binary_sha256']
banks=[r/'docs/round193-image-matrix.json',r/'docs/round234-c-image-matrix.json'];refs={}
for path in banks:
 x=read(path);assert x['passed']
 for row in x['runs']:
  if row['case'] not in ['full-seed2203','full-seed2309','full-seed2371']:continue
  expected=row.get('expected_sha256') or row['sha256'];data=r/row.get('data_folder','.data/c/'+row['case']);inputs={p.name:sha(p) for p in data.iterdir() if p.is_file()}
  if row.get('inputs_sha256'):assert inputs==row['inputs_sha256']
  if row['case'] in refs:assert refs[row['case']]['expected_sha256']==expected
  refs[row['case']]={'case':row['case'],'data_folder':str(data),'expected_sha256':expected,'inputs_sha256':inputs,'reference_source':str(path.relative_to(r))}
assert set(refs)=={'full-seed2203','full-seed2309','full-seed2371'}
public=read(r/'docs/public-sha256.json')['tracks']['c'];data=r/'.data/c/public-full-seed1';inputs={p.name:sha(p) for p in data.iterdir() if p.is_file()};assert inputs==public['inputs_sha256'];cases=[{'case':'public-full-seed1','data_folder':str(data),'expected_sha256':public['expected_output_sha256'][0],'inputs_sha256':inputs,'reference_source':'Published official full-public hashes'},*[refs[name] for name in ['full-seed2203','full-seed2309','full-seed2371']]]
report={'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'official_score':False,'selected_in_root':False,'scope':pre['scope'],'source_sha256':pre['source_sha256'],'binary_sha256':{'control':sha(control),'candidate':sha(candidate)},'cases':cases,'runs':[]}
def run(label,binary,case,threads,number):
 dest=outroot/'outputs'/(case['case']+'-'+label+'-'+str(threads)+'-'+str(number));dest.mkdir(parents=True,exist_ok=True);metrics=dest/'time.txt';env=dict(os.environ);env['SPEED_DEMON_THREADS']=str(threads)
 start=time.perf_counter();q=subprocess.run(['/usr/bin/time','-l','-o',str(metrics),str(binary),'--data',case['data_folder'],'--out',str(dest)],capture_output=True,text=True,env=env,timeout=180);elapsed=time.perf_counter()-start
 assert q.returncode==0 and not q.stdout and not q.stderr,(label,case['case'],q.returncode,q.stderr)
 assert sorted(p.name for p in dest.iterdir())==['aggregates.txt','time.txt'];actual=sha(dest/'aggregates.txt');assert actual==case['expected_sha256'],(case['case'],actual)
 text=metrics.read_text();rss=int(re.search(r'(\d+)\s+maximum resident set size',text)[1]);real=float(re.search(r'([0-9.]+)\s+real',text)[1]);row={'case':case['case'],'variant':label,'threads':threads,'round':number,'elapsed_seconds_including_launch_and_time':elapsed,'rounded_time_real_seconds':real,'native_process_rss_bytes':rss,'sha256':actual};report['runs'].append(row);(outroot/'partial.json').write_text(json.dumps(report,indent=2)+'\n');return row
for threads in [1,6,12]:
 for label,binary in [('control',control),('candidate',candidate)]:run(label,binary,cases[0],threads,-2)
for case in cases:
 for label,binary in [('control',control),('candidate',candidate)]:run(label,binary,case,12,-1)
ratios={case['case']:[] for case in cases}
for number in range(13):
 for offset in range(len(cases)):
  case=cases[(number+offset)%len(cases)];order=[('control',control),('candidate',candidate)]
  if (number+offset)%2:order.reverse()
  pair={label:run(label,binary,case,12,number) for label,binary in order};ratios[case['case']].append(pair['candidate']['elapsed_seconds_including_launch_and_time']/pair['control']['elapsed_seconds_including_launch_and_time'])
for case in cases:assert {p.name:sha(p) for p in Path(case['data_folder']).iterdir() if p.is_file()}==case['inputs_sha256']
for name,digest in pre['source_sha256'].items():assert sha(s/name)==digest
assert sha(candidate)==pre['candidate_binary_sha256'] and sha(control)==pre['control_binary_sha256'];assert sha(r/'track-c/main.cpp')==pre['root_main_sha256'] and sha(r/'track-c/names.hpp')==pre['root_names_sha256']
summary={}
for case in cases:
 name=case['case'];summary[name]={'paired_median_ratio':statistics.median(ratios[name]),'paired_wins':sum(x<1 for x in ratios[name]),'variants':{label:{'median_elapsed_seconds':statistics.median(x['elapsed_seconds_including_launch_and_time'] for x in report['runs'] if x['case']==name and x['variant']==label and x['round']>=0),'median_native_rss_bytes':statistics.median(x['native_process_rss_bytes'] for x in report['runs'] if x['case']==name and x['variant']==label and x['round']>=0)} for label in ['control','candidate']}}
report.update(passed=True,completed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),summary=summary);(outroot/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS C323 compact8 event/owner hashing screen',json.dumps(summary),flush=True)
