from pathlib import Path
import datetime,hashlib,json,os,re,statistics,subprocess,sys,time
r=Path.cwd();w=r/'.build/round289';dest=w/'fresh-confirmation';assert dest.is_dir();read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();pre=read(w/'frozen.json');screen=read(w/'screen/report.json');assert screen['passed'];binaries={'control':Path(pre['control_binary']),'candidate':w/'track-d-bin'}
for label,p in binaries.items():assert sha(p)==screen['binary_sha256'][label]
for rel,h in pre['source_sha256'].items():assert sha(w/rel)==h
case='full-seed3109';data=r/'.data/d'/case;assert data.is_dir();generator=r/'tools/official/generators/d_traverse.py';oracle=r/'tools/official/reference/d_traverse.py';tool_hashes={str(p.relative_to(r)):sha(p) for p in [generator,oracle]};report={'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'official_score':False,'selected_in_root':False,'scope':'Fresh independent untrained full3109 confirmation of existing D289/retained263 binaries after3full screening; no recompile/training. Byte-identical official generator then independent official Python single-source binary-heap Dijkstra CLI completes before program checks, hashes recorded before/after. New bounded cross-node gather/prefetch has not yet received partial-buffer/stale/growth/Floyd/full64/strict/race/GCC/image/default/actual proof; no target gain claimed.','case':case,'tool_sha256':tool_hashes,'source_sha256':pre['source_sha256'],'binary_sha256':screen['binary_sha256'],'commands':[],'runs':[]}
def save():(dest/'partial.json').write_text(json.dumps(report,indent=2)+'\n')
# Generation completed. The naive D reference calculated answers but its CLI does not create its output directory; attempt1 failed only when opening the missing output path. No result bytes survived, so only that oracle stage must repeat. Never repeat generation, compile or training.
failed=read(dest/'attempt1.json');assert failed['commands'][0]['returncode']==0 and failed['commands'][1]['returncode']==1 and not failed['runs']
assert failed['tool_sha256']==tool_hashes
assert not (dest/'outputs').exists() and not (dest/'reference').exists()
before_inputs={p.name:sha(p) for p in data.iterdir() if p.is_file()}
(dest/'reference').mkdir()
report['commands']=failed['commands']
report['recovery']={'scope':'Only missing oracle output directory corrected in test wrapper. Generator completed and is reused; official reference had computed answers but saved none, so only oracle calculation must repeat. Production source/binaries/tools unchanged. No program/timed run occurred before recovery.','resume_precondition_correction':'First recovery launch retained the generation-only data-must-not-exist assertion and stopped before directory/oracle/program work; corrected to data-is-directory. No generator/oracle/compiler/model/benchmark duplicated by that early assertion.', 'failed_attempt_sha256':sha(dest/'attempt1.json'),'inputs_before_oracle_retry_sha256':before_inputs}
save()
cmd=[sys.executable,str(oracle),'--data',str(data),'--out',str(dest/'reference')]
q=subprocess.run(cmd,capture_output=True,text=True,timeout=300);report['commands'].append({'stage':'oracle-output-directory-recovery','command':cmd,'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr});save();assert q.returncode==0,(q.returncode,q.stderr)
assert {p.name:sha(p) for p in data.iterdir() if p.is_file()}==before_inputs
assert sorted(p.name for p in (dest/'reference').iterdir())==['distances.txt'];expected=sha(dest/'reference/summary.txt');inputs={p.name:sha(p) for p in data.iterdir() if p.is_file()};assert set(inputs)=={'graph.txt','queries.txt'};report.update(inputs_sha256=inputs,expected_sha256=expected);save()
def run(label,threads,number):
 out=dest/'outputs'/f'{label}-{threads}-{number}';out.mkdir(parents=True);metrics=out/'time.txt';env=dict(os.environ,SPEED_DEMON_THREADS=str(threads));start=time.perf_counter();q=subprocess.run(['/usr/bin/time','-l','-o',str(metrics),str(binaries[label]),'--data',str(data),'--out',str(out)],capture_output=True,text=True,env=env,timeout=180);elapsed=time.perf_counter()-start;assert q.returncode==0 and not q.stdout and not q.stderr,(q.returncode,q.stdout,q.stderr);assert sorted(p.name for p in out.iterdir())==['distances.txt','time.txt'];assert sha(out/'distances.txt')==expected;t=metrics.read_text();row={'variant':label,'threads':threads,'round':number,'elapsed_seconds_including_launch_and_time':elapsed,'native_process_rss_bytes':int(re.search(r'(\d+)\s+maximum resident set size',t)[1]),'sha256':expected};report['runs'].append(row);save();return row
for threads in [1,6,12]:
 for label in binaries:run(label,threads,-2)
for label in binaries:run(label,12,-1)
ratios=[]
for number in range(13):
 order=['control','candidate'] if number%2==0 else ['candidate','control'];pair={label:run(label,12,number) for label in order};ratios.append(pair['candidate']['elapsed_seconds_including_launch_and_time']/pair['control']['elapsed_seconds_including_launch_and_time'])
assert {p.name:sha(p) for p in data.iterdir() if p.is_file()}==inputs
for rel,h in tool_hashes.items():assert sha(r/rel)==h
for rel,h in pre['source_sha256'].items():assert sha(w/rel)==h
for label,p in binaries.items():assert sha(p)==screen['binary_sha256'][label]

for rel,h in pre['root_inputs_sha256'].items():assert sha(r/rel)==h
report.update(passed=True,completed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),paired_median_ratio=statistics.median(ratios),paired_wins=sum(v<1 for v in ratios),variants={label:{'median_elapsed_seconds':statistics.median(x['elapsed_seconds_including_launch_and_time'] for x in report['runs'] if x['variant']==label and x['round']>=0),'median_native_rss_bytes':statistics.median(x['native_process_rss_bytes'] for x in report['runs'] if x['variant']==label and x['round']>=0)} for label in binaries});(dest/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS289 fresh full3109 confirmation',json.dumps({k:report[k] for k in ['paired_median_ratio','paired_wins','variants']}),flush=True)
