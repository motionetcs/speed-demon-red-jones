from pathlib import Path
import datetime,hashlib,json,os,re,statistics,subprocess,time
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round342';s=w/'source';out=w/'fresh-confirmation';assert not out.exists();out.mkdir()
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
pre=read(w/'preflight.json');old=read(w/'confirmation/report.json');strict=read(w/'native-proof/report.json');refs=read(r/'docs/round342-a-asan-full.json');assert old['passed'] and strict['passed'] and refs['passed'];ref=next(x for x in refs['checks'] if x['case']=='full-seed3557');data=r/'.data/a/full-seed3557';inputs={'requests.log':sha(data/'requests.log')};expected=ref['reference_sha256'];assert all(x['sha256']==expected for x in ref['runs']);assert sha(r/'.out/a/full-seed3557/reference/summary.txt')==expected
for p,h in pre['source_sha256'].items():assert sha(s/p)==h,p
for p,h in pre['root_selected_bindings'].items():assert sha(r/p)==h,p
bins={'control':Path(pre['control_binary']),'candidate':w/'track-a-bin'};assert {k:sha(p) for k,p in bins.items()}==old['binary_sha256']
report={'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'official_score':False,'selected_in_root':False,'scope':'One newly generated/official-reference untrained full3557 confirmation using already-built exact optimized342 and immutable263 controls, no compiler/generator/oracle/training repetition. Full1/6/12 plus13alternating pairs. Native wall/RSS only; source cost one line and prior tiny result do not establish Intel/score gain.','data_folder':str(data.relative_to(r)),'case':'full-seed3557','inputs_sha256':inputs,'reference_sha256':expected,'reference_provenance':'Fresh official generator/reference executed ONCE by342 ASANfull proof; exact completed input/reference reused, no source-specific proof relabeled.','source_sha256':pre['source_sha256'],'binary_sha256':old['binary_sha256'],'runs':[]}
def run(label,threads,number):
 dest=out/f'{label}-{threads}-{number}';dest.mkdir();metrics=dest/'time.txt';env=dict(os.environ,SPEED_DEMON_THREADS=str(threads));start=time.perf_counter();q=subprocess.run(['/usr/bin/time','-l','-o',str(metrics),str(bins[label]),'--data',str(data),'--out',str(dest)],capture_output=True,text=True,env=env,timeout=180);elapsed=time.perf_counter()-start;assert q.returncode==0 and not q.stdout and not q.stderr,(label,q.returncode,q.stderr);assert sorted(p.name for p in dest.iterdir())==['summary.txt','time.txt'];actual=sha(dest/'summary.txt');assert actual==expected;rss=int(re.search(r'(\d+)\s+maximum resident set size',metrics.read_text())[1]);row={'variant':label,'threads':threads,'round':number,'elapsed_seconds_including_launch_and_time':elapsed,'native_process_rss_bytes':rss,'sha256':actual};report['runs'].append(row);dump(out/'partial.json',report);return row
for threads in [1,6,12]:
 for label in bins:run(label,threads,-2)
for label in bins:run(label,12,-1)
ratios=[]
for n in range(13):
 order=['control','candidate'] if n%2==0 else ['candidate','control'];pair={label:run(label,12,n) for label in order};ratios.append(pair['candidate']['elapsed_seconds_including_launch_and_time']/pair['control']['elapsed_seconds_including_launch_and_time'])
for p,h in pre['source_sha256'].items():assert sha(s/p)==h,p
for p,h in pre['root_selected_bindings'].items():assert sha(r/p)==h,p
assert inputs=={'requests.log':sha(data/'requests.log')} and {k:sha(p) for k,p in bins.items()}==old['binary_sha256']
summary={'paired_median_ratio':statistics.median(ratios),'paired_wins':sum(x<1 for x in ratios),'variants':{label:{'median_elapsed_seconds':statistics.median(x['elapsed_seconds_including_launch_and_time'] for x in report['runs'] if x['variant']==label and x['round']>=0),'median_native_rss_bytes':statistics.median(x['native_process_rss_bytes'] for x in report['runs'] if x['variant']==label and x['round']>=0)} for label in bins}};report.update(passed=True,completed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),summary=summary);dump(out/'report.json',report);dump(r/'docs/round342-a-fresh-confirmation.json',report);print('PASS A342 exact fresh-full confirmation',json.dumps(summary),flush=True)
