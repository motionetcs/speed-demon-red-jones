from pathlib import Path
import datetime,hashlib,json,shutil,subprocess,tempfile
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');parent='83630432c7acd216b9813027a2e863fe0fd8aaee'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip()==parent;rows=[]
for number,track in [(372,'c'),(373,'d'),(374,'a'),(375,'a')]:
 w=r/f'.build/round{number}';pre_path=w/('frozen.json'if number==373 else'preflight.json');pre=read(pre_path);report_path=w/('screen/report.json'if number==373 else'confirmation/report.json');report=read(report_path);assert report['passed'];bindings=pre.get('root_selected_bindings',pre.get('root_inputs_sha256'))
 for p,h in bindings.items():assert sha(r/p)==h,p
 archive=r/f'tools/round{number}-screen';assert not archive.exists();archive.mkdir();shutil.copy2(w/'prepare.py',archive/'prepare.py');shutil.copy2(w/'screen.py',archive/'screen.py');shutil.copy2(pre_path,archive/pre_path.name);shutil.copy2(report_path,archive/'report.json')
 if(w/'compile.json').exists():shutil.copy2(w/'compile.json',archive/'compile.json')
 shutil.copy2(w/f'source/track-{track}/PERF.md',archive/f'base-{track}-PERF.md');patches=[]
 for p in sorted(w.glob('*.patch')):
  dest=r/f'docs/prototype-patches/round{number}-{track}-{p.name}';shutil.copy2(p,dest);patches.append({'path':str(dest.relative_to(r)),'sha256':sha(dest)})
 frozen={p.removeprefix('source/'):h for p,h in pre['source_sha256'].items()}
 for p,h in frozen.items():assert sha(w/'source'/p)==h,p
 with tempfile.TemporaryDirectory(prefix=f'round{number}-reconstruct-')as tmp:
  base=Path(tmp)
  for p,h in frozen.items():
   dest=base/p;dest.parent.mkdir(parents=True,exist_ok=True)
   if dest.name=='PERF.md':shutil.copy2(archive/f'base-{track}-PERF.md',dest)
   else:dest.write_bytes(subprocess.check_output(['git','show',parent+':'+p],cwd=r))
  for row in patches:
   q=subprocess.run(['git','apply',str(r/row['path'])],cwd=base,capture_output=True,text=True);assert q.returncode==0,q.stderr
  for p,h in frozen.items():assert sha(base/p)==h,p
 summary={name:{'paired_median_ratio':x['paired_median_ratio'],'paired_wins':x['paired_wins'],'native_rss_delta_bytes':x['variants']['candidate']['median_native_rss_bytes']-x['variants']['control']['median_native_rss_bytes']}for name,x in report['summary'].items()}
 limitations={'372':'New owner-private hint front-end is slower on all4 full cases and adds memory. No independent hint/eviction/collision/zero1/growth/stableindex/binary/guard/country/strict/race/untrained/GNU/image/default/actual proof. Original queue/parser source identity is provenance, not a cache correctness certificate.','373':'Retaining physical backing while resetting logical packed bits is slower on all3 full cases, RSS mixed. Distinct from83 fresh smaller allocations, still unsupported. No new active-prefix/grow/reset/fullbucket/wide/guard/stdmap/Floyd/strict/race/untrained/GNU/image/default/actual proof. No standalone-header portability or SIMD-path cross-platform proof.','374':'Initial mapped reserve512 is weak/mixed and slightly higher native RSS. No demonstrated charged-memory peak saving; unused virtual reserve is not resident memory. No new OOM/growth/lifetime/strict/race/untrained/GNU/image/default/actual proof. Old35 standard-allocator reserve512 and214 grow factors remain different historical trials.','375':'Dynamic1MiB newline parser jobs have weak/mixed time and1.9–2.5MB higher native RSS. No demonstrated Intel imbalance/P-E cause or charged-memory gain. No new exact-once partition/empty/equal-boundary/guard/overflow/privateownership/errorjoin/strict/race/untrained/GNU/image/default/actual proof; working atomic coverage reasoning is not a certificate.'}[str(number)]
 item={'number':number,'track':track,'decision':'REJECT_NATIVE_ONLY','source_parent':parent,'source_selected':False,'official_score':False,'scope':pre['scope'],'summary':summary,'native_valid_calls':len(report['runs']),'patches':patches,'frozen_source_sha256':frozen,'reconstruction':{'passed':True,'all_files':len(frozen),'scope':'Exact parent plus disclosed patches and separately frozen excluded PERF snapshot reconstruct every prototype context file.'},'limitations':limitations,'files':{str(p.relative_to(r)):sha(p)for p in archive.iterdir()if p.is_file()}}
 (archive/'README.md').write_text(f'# {track.upper()}{number}: rejected after native screening\n\n'+pre['scope']+'\n\n'+limitations+'\n\nOne successful optimized compile; immutable selected control reused. All full-public1/6/12 calls and thirteen rotating pairs on saved full references match before/after input, output, source and binary hashes. No new data generation, reference execution, training, production image or board request. Native Apple process timing and RSS are not target timing, cgroup memory or total K. Source remains selected original371.\n')
 item['files']={str(p.relative_to(r)):sha(p)for p in archive.iterdir()if p.is_file()};(w/'ACTIVE.json').write_text(json.dumps({'status':'rejected_native_only','no_active_work':True,'summary':summary,'limitations':limitations},indent=2)+'\n');rows.append(item)
 p=r/f'track-{track}/PERF.md';p.write_text(p.read_text()+f'\n\n{track.upper()}{number} REJECT_NATIVE_ONLY. '+limitations+' Paired full-reference ratios '+json.dumps(summary,sort_keys=True)+f'. One native compile/{len(report["runs"])} legal-data calls, full input/output/source/ELF hashesPASS; no selected runtime or board change. Exact source/driver/patch reconstruction docs/round372-375-screen-index.json and tools/round{number}-screen.\n')
out=r/'docs/round372-375-screen-index.json';assert not out.exists();out.write_text(json.dumps({'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'selected_commit':parent,'official_score':False,'all_rejected':True,'cases':rows,'scope':'Independent sequential isolated native screens. Each compiled once with unchanged flags under shared exclusive lane. Original cached A/C263 and current D334 controls reused. All current root30/Make bindings match selected371. No new generator/oracle/model/training/GNU/production image/default or board work. No meaningful retained gain or user action.'},indent=2)+'\n')
shutil.copy2(Path(__file__),r/'tools/round375-screen/archive372-375.py');print('ARCHIVED372–375 all rejected; all frozen context reconstructionsPASS; root source unchanged',flush=True)
