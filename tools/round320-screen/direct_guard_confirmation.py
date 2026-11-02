from pathlib import Path
import datetime,hashlib,json,os,re,statistics,subprocess,time
r=Path.cwd();w=r/'.build/round320';o=w/'direct-confirmation';assert not o.exists();o.mkdir();read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();pre=read(w/'preflight.json');old=read(w/'confirmation/report.json');assert old['passed'];bins={'original':r/'.build/round263/final-make/track-c','shared315':r/'.build/round315/final-make/track-c','guard320':w/'track-c-bin'};cases=old['cases'];bank=read(r/'docs/round305-c-linux-image.json');extra=next(x for x in bank['runs'] if x['case']=='full-seed3313');cases.append({'case':'full-seed3313','data_folder':str(r/extra['data_folder']),'expected_sha256':extra['expected_sha256'],'inputs_sha256':extra['inputs_sha256'],'reference_source':'Saved independent305 untrained full3313 reference, first C320 execution; input/expected data only, no old-source proof inherited'})
for rel,h in pre['source_sha256'].items():assert sha(w/'source'/rel)==h
for row in read(r/'docs/round317-final-source-match.json')['inputs']:assert sha(r/row['path'])==row['sha256']
report={'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'official_score':False,'selected_in_root':False,'scope':'Direct guarded320 versus rejected unguarded315 versus passing original263 in rotating13triples over6full input/reference packs. Native320 initial15-25% versus original is not a guard-specific causal gain; previous315 screen had different baseline launch timings. This uses existing exact optimized binaries, no compiler/model/training/generator/oracle duplicates, and adds held-out-relative-to320 full3313 saved independent reference. Native/runtimeRss only, not IntelK.','binary_sha256':{label:sha(p) for label,p in bins.items()},'source315_manifest_sha256':sha(r/'.build/round315/preflight.json'),'source320_manifest_sha256':sha(w/'preflight.json'),'cases':cases,'runs':[]}
def save():(o/'partial.json').write_text(json.dumps(report,indent=2)+'\n')
def run(label,case,n):
 dest=o/'out'/case['case']/f'{label}-{n}';dest.mkdir(parents=True);metric=dest/'time.txt';start=time.perf_counter();q=subprocess.run(['/usr/bin/time','-l','-o',str(metric),str(bins[label]),'--data',case['data_folder'],'--out',str(dest)],capture_output=True,text=True,env=dict(os.environ,SPEED_DEMON_THREADS='12'),timeout=180);elapsed=time.perf_counter()-start;assert q.returncode==0 and not q.stdout and not q.stderr,(label,case['case'],q.returncode,q.stderr);assert sorted(p.name for p in dest.iterdir())==['aggregates.txt','time.txt'] and sha(dest/'aggregates.txt')==case['expected_sha256'];rss=int(re.search(r'(\d+)\s+maximum resident set size',metric.read_text())[1]);row={'case':case['case'],'variant':label,'round':n,'elapsed_seconds_including_launch_and_time':elapsed,'native_process_rss_bytes':rss,'sha256':case['expected_sha256']};report['runs'].append(row);save();return row
for case in cases:
 assert {p.name:sha(p) for p in Path(case['data_folder']).iterdir() if p.is_file()}==case['inputs_sha256']
 for label in bins:run(label,case,-1)
ratios={c['case']:{'guard_to_shared315':[],'guard_to_original':[]} for c in cases};labels=list(bins)
for n in range(13):
 for offset in range(len(cases)):
  case=cases[(n+offset)%len(cases)];order=labels[(n+offset)%3:]+labels[:(n+offset)%3]
  if (n+offset)%2:order=list(reversed(order))
  pair={label:run(label,case,n) for label in order}
  for key,base in [('guard_to_shared315','shared315'),('guard_to_original','original')]:ratios[case['case']][key].append(pair['guard320']['elapsed_seconds_including_launch_and_time']/pair[base]['elapsed_seconds_including_launch_and_time'])
summary={}
for case in cases:
 name=case['case'];summary[name]={key:{'paired_median_ratio':statistics.median(values),'wins':sum(x<1 for x in values)} for key,values in ratios[name].items()};summary[name]['variants']={label:{'median_elapsed_seconds':statistics.median(x['elapsed_seconds_including_launch_and_time'] for x in report['runs'] if x['case']==name and x['variant']==label and x['round']>=0),'median_rss_bytes':statistics.median(x['native_process_rss_bytes'] for x in report['runs'] if x['case']==name and x['variant']==label and x['round']>=0)} for label in bins};assert {p.name:sha(p) for p in Path(case['data_folder']).iterdir() if p.is_file()}==case['inputs_sha256']
for rel,h in pre['source_sha256'].items():assert sha(w/'source'/rel)==h
for label,p in bins.items():assert sha(p)==report['binary_sha256'][label]
report.update(passed=True,summary=summary,completed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());(o/'report.json').write_text(json.dumps(report,indent=2)+'\n');(r/'docs/round320-c-direct-guard-confirmation.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS320 direct guard-specific native comparison',json.dumps(summary),flush=True)
