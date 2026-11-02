from pathlib import Path
import datetime,hashlib,json,os,re,statistics,subprocess,time
r=Path.cwd();w=r/'.build/round386';m=json.loads((w/'frozen.json').read_text());dest=w/'screen';dest.mkdir();read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();report={'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'official_score':False,'selected_in_root':False,'scope':m['scope'],'frozen_manifest_sha256':sha(w/'frozen.json'),'source_sha256':m['source_sha256'],'runs':[]}
def checkpoint():(dest/'partial.json').write_text(json.dumps(report,indent=2)+'\n')
for p,h in m['source_sha256'].items():assert sha(w/p)==h
for p,h in m['root_inputs_sha256'].items():assert sha(r/p)==h
candidate=w/'track-d-bin';assert not candidate.exists();control=Path(m['control_binary']);assert sha(control)==m['control_binary_sha256'];cmd=['clang++','-std=c++20','-O3','-DNDEBUG','-Wall','-Wextra','-Wpedantic','-pthread',str(w/'source/track-d/main.cpp'),'-o',str(candidate)];q=subprocess.run(cmd,capture_output=True,text=True,timeout=180);report['compile']={'command':cmd,'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr};checkpoint();assert q.returncode==0 and not q.stderr and not q.stdout,q.stderr
bins={'control':control,'candidate':candidate};report['binary_sha256']={k:sha(p) for k,p in bins.items()};public=read(r/'docs/public-sha256.json')['tracks']['d'];prior=read(r/'docs/round262-degree2-native-confirmation.json');assert prior['passed'];cases=[]
for name in ['public-full-seed1','full-seed1823','full-seed2633']:
 hashes={x.get('output_sha256',x.get('sha256')) for x in prior['runs'] if x['case']==name};assert len(hashes)==1;expected=hashes.pop();inputs=prior['inputs_sha256'][name];data=r/'.data/d'/name;assert {p.name:sha(p) for p in data.iterdir() if p.is_file()}==inputs
 if name=='public-full-seed1':assert inputs==public['inputs_sha256'] and expected in public['expected_output_sha256']
 cases.append({'case':name,'reference_sha256':expected,'inputs_sha256':inputs,'data_folder':str(data),'reference_source':'docs/round262-degree2-native-confirmation.json input/expected bytes only; changed-main proof is not reused'})
report['cases']=cases;checkpoint()
def run(label,case,threads,number):
 out=dest/'outputs'/f"{case['case']}-{label}-{threads}-{number}";out.mkdir(parents=True);metrics=out/'time.txt';env=dict(os.environ,SPEED_DEMON_THREADS=str(threads));started=time.perf_counter();q=subprocess.run(['/usr/bin/time','-l','-o',str(metrics),str(bins[label]),'--data',case['data_folder'],'--out',str(out)],capture_output=True,text=True,env=env,timeout=180);elapsed=time.perf_counter()-started;assert q.returncode==0 and not q.stdout and not q.stderr,(label,case['case'],threads,q.returncode,q.stderr);assert sorted(p.name for p in out.iterdir())==['distances.txt','time.txt'];assert sha(out/'distances.txt')==case['reference_sha256'];t=metrics.read_text();row={'case':case['case'],'variant':label,'threads':threads,'round':number,'elapsed_seconds_including_launch_and_time':elapsed,'native_process_rss_bytes':int(re.search(r'(\d+)\s+maximum resident set size',t)[1]),'sha256':case['reference_sha256']};report['runs'].append(row);checkpoint();return row
for threads in [1,6,12]:
 for label in bins:run(label,cases[0],threads,-2)
for case in cases:
 for label in bins:run(label,case,12,-1)
ratios={case['case']:[] for case in cases}
for number in range(13):
 for offset in range(len(cases)):
  case=cases[(number+offset)%len(cases)];order=['control','candidate'] if (number+offset)%2==0 else ['candidate','control'];pair={label:run(label,case,12,number) for label in order};ratios[case['case']].append(pair['candidate']['elapsed_seconds_including_launch_and_time']/pair['control']['elapsed_seconds_including_launch_and_time'])
for case in cases:assert {p.name:sha(p) for p in Path(case['data_folder']).iterdir() if p.is_file()}==case['inputs_sha256']
for p,h in m['source_sha256'].items():assert sha(w/p)==h
for p,h in m['root_inputs_sha256'].items():assert sha(r/p)==h
for label,b in bins.items():assert sha(b)==report['binary_sha256'][label]
summary={}
for case in cases:
 name=case['case'];summary[name]={'paired_median_ratio':statistics.median(ratios[name]),'paired_wins':sum(x<1 for x in ratios[name]),'variants':{label:{'median_elapsed_seconds':statistics.median(x['elapsed_seconds_including_launch_and_time'] for x in report['runs'] if x['case']==name and x['variant']==label and x['round']>=0),'median_native_rss_bytes':statistics.median(x['native_process_rss_bytes'] for x in report['runs'] if x['case']==name and x['variant']==label and x['round']>=0)} for label in bins}}
report.update(passed=True,completed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),summary=summary);(dest/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS D386 word-blocked opposite negative filter screen',json.dumps(summary),flush=True)
