from pathlib import Path
import datetime,hashlib,json,os,re,statistics,subprocess,time
r=Path.cwd();w=r/'.build/round289';dest=w/'fresh-confirmation';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();read=lambda p:json.loads(Path(p).read_text());pre=read(w/'frozen.json');screen=read(w/'screen/report.json');report=read(dest/'partial.json');assert screen['passed'] and not report['runs'] and not (dest/'outputs').exists();assert [(x['stage'],x['returncode']) for x in report['commands']]==[('generation',0),('oracle',1),('oracle-output-directory-recovery',0)]
# Both generator and recovered independent oracle completed; reuse saved bytes.
# A metadata path still said summary.txt and failed after oracle output was saved.
# Correct only that expected-output path; do not rerun any successful CPU stage.
report['recovery']['saved_oracle_metadata_correction']='Recovered official oracle completed and saved distances.txt, then leftover A summary.txt metadata path failed before any program/timed run. Corrected expected-output path and resume saved inputs/reference without generation/oracle/compile/training repetition.'
case='full-seed3109';data=r/'.data/d'/case;expected_path=dest/'reference/distances.txt';assert expected_path.is_file() and [p.name for p in (dest/'reference').iterdir()]==['distances.txt'];expected=sha(expected_path);inputs={p.name:sha(p) for p in data.iterdir() if p.is_file()};assert inputs==report['recovery']['inputs_before_oracle_retry_sha256'] and set(inputs)=={'graph.txt','queries.txt'}
for rel,h in pre['source_sha256'].items():assert sha(w/rel)==h
for rel,h in pre['root_inputs_sha256'].items():assert sha(r/rel)==h
for rel,h in report['tool_sha256'].items():assert sha(r/rel)==h
bins={'control':Path(pre['control_binary']),'candidate':w/'track-d-bin'}
for label,b in bins.items():assert sha(b)==screen['binary_sha256'][label]
report.update(resumed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),inputs_sha256=inputs,expected_sha256=expected)
def save():(dest/'partial.json').write_text(json.dumps(report,indent=2)+'\n')
save()
def run(label,threads,number):
 out=dest/'outputs'/f'{label}-{threads}-{number}';out.mkdir(parents=True);metrics=out/'time.txt';env=dict(os.environ,SPEED_DEMON_THREADS=str(threads));start=time.perf_counter();q=subprocess.run(['/usr/bin/time','-l','-o',str(metrics),str(bins[label]),'--data',str(data),'--out',str(out)],capture_output=True,text=True,env=env,timeout=180);elapsed=time.perf_counter()-start;assert q.returncode==0 and not q.stdout and not q.stderr,(label,threads,q.returncode,q.stderr);assert sorted(p.name for p in out.iterdir())==['distances.txt','time.txt'];assert sha(out/'distances.txt')==expected;t=metrics.read_text();row={'variant':label,'threads':threads,'round':number,'elapsed_seconds_including_launch_and_time':elapsed,'native_process_rss_bytes':int(re.search(r'(\d+)\s+maximum resident set size',t)[1]),'sha256':expected};report['runs'].append(row);save();return row
for threads in [1,6,12]:
 for label in bins:run(label,threads,-2)
for label in bins:run(label,12,-1)
ratios=[]
for number in range(13):
 order=['control','candidate'] if number%2==0 else ['candidate','control'];pair={label:run(label,12,number) for label in order};ratios.append(pair['candidate']['elapsed_seconds_including_launch_and_time']/pair['control']['elapsed_seconds_including_launch_and_time'])
assert {p.name:sha(p) for p in data.iterdir() if p.is_file()}==inputs and sha(expected_path)==expected
for rel,h in pre['source_sha256'].items():assert sha(w/rel)==h
for rel,h in pre['root_inputs_sha256'].items():assert sha(r/rel)==h
for rel,h in report['tool_sha256'].items():assert sha(r/rel)==h
for label,b in bins.items():assert sha(b)==screen['binary_sha256'][label]
report.update(passed=True,completed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),paired_median_ratio=statistics.median(ratios),paired_wins=sum(v<1 for v in ratios),variants={label:{'median_elapsed_seconds':statistics.median(x['elapsed_seconds_including_launch_and_time'] for x in report['runs'] if x['variant']==label and x['round']>=0),'median_native_rss_bytes':statistics.median(x['native_process_rss_bytes'] for x in report['runs'] if x['variant']==label and x['round']>=0)} for label in bins});(dest/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS289 fresh full3109 confirmation',json.dumps({k:report[k] for k in ['paired_median_ratio','paired_wins','variants']}),flush=True)
