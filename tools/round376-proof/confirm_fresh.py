from pathlib import Path
import datetime,hashlib,json,os,re,shutil,statistics,subprocess,time
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round376';pre=json.loads((w/'preflight.json').read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def dump(p,j):p.write_text(json.dumps(j,indent=2)+'\n')
assert read(w/'confirmation/report.json')['passed'];assert not(w/'fresh-confirmation').exists();out=w/'fresh-confirmation';out.mkdir();source=w/'source'
for p,h in pre['source_sha256'].items():assert sha(source/p)==h
for p,h in pre['root_selected_bindings'].items():assert sha(r/p)==h
candidate=w/'track-a-bin';control=Path(pre['control_binary']);screen=read(w/'confirmation/report.json');assert sha(candidate)==screen['binary_sha256']['candidate']and sha(control)==screen['binary_sha256']['control']
report={'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'official_score':False,'selected_in_root':False,'scope':'One newly generated independent full3911 official-reference suite at1/6/12, then13 rotating paired original/candidate native calls. No compiler or training repeat; original exact cached controls and existing376 optimized ELF reused. Native process time/RSS not Intel/cgroup/K.','source_sha256':pre['source_sha256'],'runs':[]}
path=r/'docs/round376-a-native-fresh-full3911.json';assert not path.exists()and not(r/'.data/a/full-seed3911').exists();native=w/'native';native.mkdir();shutil.copyfile(candidate,native/'track-a');(native/'track-a').chmod(0o755);assert sha(native/'track-a')==sha(candidate)
argv=['python3','tools/verify.py','--run-id','round376-native-fresh-full3911','--source-root',str(source),'--binary-dir',str(native),'--tracks','a','--threads','1','6','12','--scale','full','--seeds','3911','--skip-adversarial','--report',str(path)];q=subprocess.run(argv,cwd=r,capture_output=True,text=True,env=dict(os.environ,PYTHONPATH=str(r/'tools')),timeout=1200);(out/'fresh.stdout').write_text(q.stdout);(out/'fresh.stderr').write_text(q.stderr);dump(out/'fresh-attempt.json',{'command':argv,'returncode':q.returncode});assert q.returncode==0 and read(path)['passed'],(q.returncode,q.stdout[-1800:],q.stderr[-1800:])
x=next(x for x in read(path)['checks']if x['case']=='full-seed3911');data=r/'.data/a/full-seed3911';inputs={p.name:sha(p)for p in data.iterdir()if p.is_file()};expected=x['reference_sha256'];report.update(reference_report={'path':str(path.relative_to(r)),'sha256':sha(path)},inputs_sha256=inputs,expected_sha256=expected,binary_sha256=screen['binary_sha256'])
def run(label,binary,number):
 dest=out/'outputs'/(label+'-'+str(number));dest.mkdir(parents=True);metrics=dest/'time.txt';started=time.perf_counter();q=subprocess.run(['/usr/bin/time','-l','-o',str(metrics),str(binary),'--data',str(data),'--out',str(dest)],capture_output=True,text=True,env=dict(os.environ,SPEED_DEMON_THREADS='12'),timeout=180);elapsed=time.perf_counter()-started;assert q.returncode==0 and not q.stdout and not q.stderr,(q.returncode,q.stderr);assert sorted(p.name for p in dest.iterdir())==['summary.txt','time.txt'];assert sha(dest/'summary.txt')==expected;row={'variant':label,'round':number,'threads':12,'elapsed_seconds_including_launch_and_time':elapsed,'native_process_rss_bytes':int(re.search(r'(\d+)\s+maximum resident set size',metrics.read_text())[1]),'sha256':expected};report['runs'].append(row);dump(out/'partial.json',report);return row
bins={'control':control,'candidate':candidate}
for k,v in bins.items():run(k,v,-1)
ratios=[]
for n in range(13):
 order=['control','candidate']if n%2==0 else['candidate','control'];pair={k:run(k,bins[k],n)for k in order};ratios.append(pair['candidate']['elapsed_seconds_including_launch_and_time']/pair['control']['elapsed_seconds_including_launch_and_time'])
summary={'paired_median_ratio':statistics.median(ratios),'paired_wins':sum(x<1 for x in ratios),'variants':{label:{'median_elapsed_seconds':statistics.median(x['elapsed_seconds_including_launch_and_time']for x in report['runs']if x['variant']==label and x['round']>=0),'median_native_rss_bytes':statistics.median(x['native_process_rss_bytes']for x in report['runs']if x['variant']==label and x['round']>=0)}for label in bins}}
for p,h in pre['source_sha256'].items():assert sha(source/p)==h
for p,h in pre['root_selected_bindings'].items():assert sha(r/p)==h
assert{p.name:sha(p)for p in data.iterdir()if p.is_file()}==inputs
for label,b in bins.items():assert sha(b)==screen['binary_sha256'][label]
report.update(passed=True,completed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),summary=summary);dump(out/'report.json',report);dump(r/'docs/round376-a-fresh-confirmation.json',report);print('PASS376 fresh full3911 native confirmation',json.dumps(summary),flush=True)
