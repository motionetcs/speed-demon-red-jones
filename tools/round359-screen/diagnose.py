from pathlib import Path
import datetime,hashlib,json,os,subprocess
r=Path.cwd();w=r/'.build/round359';s=w/'diagnostic-source';out=w/'diagnostic';out.mkdir(exist_ok=True)
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
pre=read(w/'preflight.json');frozen=read(w/'prepared.json');assert not(out/'report.json').exists()
for rel,h in frozen['artifacts_sha256'].items():assert sha(w/rel)==h,rel
for rel,h in pre['diagnostic_source_sha256'].items():assert sha(s/rel)==h,rel
for rel,h in pre['source_sha256'].items():assert sha(w/'source'/rel)==h,rel
for rel,h in pre['root_selected_bindings'].items():assert sha(r/rel)==h,rel
assert sha(pre['control_binary'])==pre['control_binary_sha256']
binary=w/'diagnostic-bin';assert not binary.exists();cmd=['clang++','-std=c++20','-O3','-DNDEBUG','-Wall','-Wextra','-Wpedantic','-pthread',str(s/'track-a/main.cpp'),'-o',str(binary)]
q=subprocess.run(cmd,capture_output=True,text=True,timeout=180);dump(out/'compile.json',{'command':cmd,'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr});assert q.returncode==0 and not q.stdout and not q.stderr,q.stderr
public=read(r/'docs/public-sha256.json')['tracks']['a'];prior=read(r/'docs/round268-a-suffix-screen.json');assert prior['passed'];report={'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'official_score':False,'selected_in_root':False,'scope':pre['diagnostic_scope'],'source_sha256':pre['diagnostic_source_sha256'],'candidate_source_sha256':pre['source_sha256'],'binary_sha256':sha(binary),'prepared_manifest_sha256':sha(w/'prepared.json'),'runs':[]}
fields=['calls','first_hits','second_hits','short_misses','long_fallbacks','empty_misses','conflict_misses','relocation_steps','dropped_entries']
for name in ['public-full-seed1','full-seed1951','full-seed2221']:
 case=next(c for c in prior['cases'] if c['case']==name);data=r/'.data/a'/name;inputs={p.name:sha(p) for p in data.iterdir() if p.is_file()};assert inputs=={'requests.log':case['input_sha256']};expected=case['reference_sha256']
 if name=='public-full-seed1':assert inputs==public['inputs_sha256'] and expected in public['expected_output_sha256']
 dest=out/'outputs'/name;dest.mkdir(parents=True);env=dict(os.environ,SPEED_DEMON_THREADS='12');command=[str(binary),'--data',str(data),'--out',str(dest)];q=subprocess.run(command,capture_output=True,text=True,env=env,timeout=180)
 (out/(name+'.stdout')).write_text(q.stdout);(out/(name+'.stderr')).write_text(q.stderr)
 row={'case':name,'command':command,'requested_threads':12,'returncode':q.returncode,'inputs_sha256':inputs,'expected_output_sha256':expected,'stdout_sha256':sha(out/(name+'.stdout')),'stderr_sha256':sha(out/(name+'.stderr'))};report['runs'].append(row);dump(out/'partial.json',report)
 assert q.returncode==0 and not q.stdout,(name,q.returncode,q.stderr)
 assert sorted(p.name for p in dest.iterdir())==['summary.txt'];actual=sha(dest/'summary.txt');assert actual==expected
 # The preserved generated diagnostic emits literal backslash-n record separators.
 # Parse that explicit framing; the exact raw stderr above remains immutable.
 lines=q.stderr.replace(chr(92)+'n','\n').splitlines();assert len(lines)==24 and all(line.startswith('CACHE359 ') for line in lines)
 counters=[json.loads(line[len('CACHE359 '):]) for line in lines];assert {(c['worker'],c['variant']) for c in counters}=={(worker,label) for worker in range(12) for label in ['direct','cuckoo']}
 for c in counters:
  assert all(isinstance(c[f],int) and c[f]>=0 for f in fields)
  assert c['calls']==c['first_hits']+c['second_hits']+c['short_misses']+c['long_fallbacks']
  assert c['short_misses']==c['empty_misses']+c['conflict_misses']
  assert c['dropped_entries']<=c['conflict_misses']
  if c['variant']=='direct':assert c['second_hits']==c['relocation_steps']==c['dropped_entries']==0
 for worker in range(12):assert len({c['calls'] for c in counters if c['worker']==worker})==1
 totals={label:{field:sum(c[field] for c in counters if c['variant']==label) for field in fields} for label in ['direct','cuckoo']}
 output_records=sum(int(line.split()[2]) for line in (dest/'summary.txt').read_text().splitlines());assert totals['direct']['calls']==totals['cuckoo']['calls']==output_records
 row.update(passed=True,output_sha256=actual,output_records=output_records,counters=counters,totals=totals,source_of_expected_hash=case['reference_source'],interpretation='Input-derived event counts only; no native timing, charged-memory or official-score inference. Both diagnostics execute on the same per-worker key stream and assert equal IDs.')
 assert {p.name:sha(p) for p in data.iterdir() if p.is_file()}==inputs;dump(out/'partial.json',report)
for rel,h in pre['diagnostic_source_sha256'].items():assert sha(s/rel)==h,rel
for rel,h in pre['source_sha256'].items():assert sha(w/'source'/rel)==h,rel
for rel,h in pre['root_selected_bindings'].items():assert sha(r/rel)==h,rel
for rel,h in frozen['artifacts_sha256'].items():assert sha(w/rel)==h,rel
assert sha(binary)==report['binary_sha256'] and sha(pre['control_binary'])==pre['control_binary_sha256']
report.update(passed=True,completed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());dump(out/'report.json',report);print('PASS359 paired private-cache event counts',json.dumps({row['case']:row['totals'] for row in report['runs']}),flush=True)
