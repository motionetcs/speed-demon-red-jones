from pathlib import Path
import datetime,hashlib,json,shutil,subprocess,tempfile
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
parent='781f2ea889c110b470720000729c7eedfadc67af';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip()==parent
index=[]
for n in [354,355,356,357]:
 w=r/f'.build/round{n}';a=r/f'tools/round{n}-proof';a.mkdir();pre=read(w/'preflight.json');assert pre['source_parent']==parent
 def copy(src,dest):
  out=a/dest;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,out)
 for p in w.iterdir():
  if p.is_file()and p.suffix in ['.py','.json','.cpp','.inc','.md'] and p.name not in ['integration-partial.json']:
   copy(p,p.name)
 copy(w/'confirmation/report.json','screen-report.json')
 for t in sorted({p[6]for p in pre['source_sha256']}):copy(w/f'source/track-{t}/PERF.md',f'base-{t}-PERF.md')
 patches=[]
 for p in sorted(w.glob('*.patch')):
  dest=r/f'docs/prototype-patches/round{n}-{p.name}';shutil.copy2(p,dest);patches.append({'path':str(dest.relative_to(r)),'sha256':sha(dest)})
 if n==354:
  f=r/'.build/round354-initial-prepare-failed'
  for p in f.rglob('*'):
   if p.is_file()and p.name in ['executed-prepare.py','failure.json']:copy(p,'initial-prepare-failed/'+str(p.relative_to(f)))
 if n==356:
  copy(w/'fresh-confirmation/report.json','fresh-confirmation.json');copy(w/'native-proof/report.json','native-proof.json')
  for p in (w/'native-proof').rglob('*'):
   if p.is_file()and p.suffix in ['.stdout','.stderr']:copy(p,'native-raw/'+str(p.relative_to(w/'native-proof')))
 if n==357:
  copy(w/'native-proof/report.json','native-proof.json')
  for base,dest in [(w/'native-proof','native-raw'),(w/'proof/model','gnu-model-raw'),(w/'failed-GNU-allocator','failed-GNU-allocator')]:
   for p in base.rglob('*'):
    if p.is_file()and p.suffix in ['.stdout','.stderr','.json','.py','.cpp'] and p.name not in ['partial.json']:copy(p,dest+'/'+str(p.relative_to(base)))
  for mode in ['model','gcc','build','image','defaults']:
   report=r/f'docs/round357-c-{mode}-proof.json';assert read(report)['passed'];assert report.read_bytes()==(w/f'proof/{mode}/report.json').read_bytes()
  assert read(r/'docs/round357-candidate-source-match.json')['passed']
 # Reconstruct every frozen source file from353 plus only these patches and frozen excluded PERF.
 with tempfile.TemporaryDirectory(prefix=f'round{n}-reconstruct-')as temp:
  base=Path(temp)
  for p,h in pre['source_sha256'].items():
   dest=base/p;dest.parent.mkdir(parents=True,exist_ok=True)
   if dest.name=='PERF.md':shutil.copy2(a/f'base-{p[6]}-PERF.md',dest)
   else:dest.write_bytes(subprocess.check_output(['git','show',parent+':'+p],cwd=r))
  for row in patches:
   q=subprocess.run(['git','apply',str(r/row['path'])],cwd=base,capture_output=True,text=True);assert q.returncode==0,q.stderr
  for p,h in pre['source_sha256'].items():assert sha(base/p)==sha(w/'source'/p)==h,p
 screen=read(w/'confirmation/report.json');assert screen['passed'];summary={k:{'paired_median_ratio':v['paired_median_ratio'],'paired_wins':v['paired_wins'],'native_rss_delta_bytes':v['variants']['candidate']['median_native_rss_bytes']-v['variants']['control']['median_native_rss_bytes']}for k,v in screen['summary'].items()}
 decision={354:'SUPERSEDED_BEFORE_STRICT_GNU_IMAGE_OR_BOARD: initial64epoch prototype had preexisting startup-join gap; revised356 before model compilation.',355:'REJECT_NATIVE_ONLY: weak/mixed A whole-hour radix time plus3.1–3.5MB nativeRSS; no new broad/rank/escape/strict/race/GNU/image/board proof.',356:'SUPERSEDED_BEFORE_GNU_IMAGE_OR_BOARD: native strict/race/full/untrained proofs complete, fresh3623 weaker variable timing; revised357 to direct uint32 GNU wait word with independent bounded-ABA review.',357:'LOCAL_PASS_ONE_REAL_TRIAL_PENDING: native/source-specific strict/race and actual pinnedGNU15.3/model/fault/main/image/default/rootMake passed. No official improvement claimed.'}[n]
 limitations='Native Apple timings/RSS and emulated Linux correctness are not Intel timing, charged memory, organizer ELF, causal improvement, eligibility or final holdout guarantees. Saved data/reference bytes reused only by hash; no cached production answers. No host/harness/counter/identity manipulation.'
 (a/'README.md').write_text(f'# Round{n} exact evidence\n\n{pre["scope"]}\n\n{decision}\n\nReconstruction: recorded353 parent plus disclosed source patches and separately frozen PERF snapshots reconstruct all frozen files exactly. Drivers are archived as actually executed;355 preparation is an exact recovered command-execution record, no invented prepare.py.354 failed preliminary assertion preceded any compiler/benchmark; its unexecuted model is not proof.356/357 models and raw labels retain historical print strings; actual source types/version and recovery are documented in reports.357 GNU allocator mismatch diagnosis was test-only; separate model-only TUs retained all strict flags, reused completed queue proof, and resumed failed/unexecuted startup work only. No vendor atomic_wait header is copied into tracked source; actual pinned header hash/path and compiler15.3 report are retained.\n\n'+limitations+'\n')
 row={'round':n,'source_parent':parent,'official_score':False,'selected_in_root_for_trial_only':n==357,'decision':decision,'scope':pre['scope'],'screen_summary':summary,'screen_call_count':len(screen['runs']),'patches':patches,'reconstruction':{'passed':True,'all_frozen_files_match':True,'file_count':len(pre['source_sha256'])},'archive_files_sha256':{str(p.relative_to(r)):sha(p)for p in a.rglob('*')if p.is_file()},'limitations':limitations}
 dump(r/f'docs/round{n}-proof-archive.json',row);index.append({k:row[k]for k in ['round','decision','screen_summary','screen_call_count','reconstruction']})
dump(r/'docs/round354-357-index.json',{'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'official_score':False,'rounds':index,'root_candidate':'C357 trial only; A178/D334 unchanged','original353_preserved':True})
for n in [354,356,357]:
 p=r/'track-c/PERF.md';row=read(r/f'docs/round{n}-proof-archive.json');p.write_text(p.read_text()+f'\n\nRound{n}: '+row['decision']+' Nativepaired time ratios '+json.dumps(row['screen_summary'],sort_keys=True)+'. Exact source/patches/drivers and limitations: docs/round'+str(n)+'-proof-archive.json. '+row['limitations']+'\n')
p=r/'track-a/PERF.md';row=read(r/'docs/round355-proof-archive.json');p.write_text(p.read_text()+'\n\nRound355: '+row['decision']+' Paired screen '+json.dumps(row['screen_summary'],sort_keys=True)+'. Exact recovered execution record, frozen source reconstruction and driver: docs/round355-proof-archive.json. No production change/official gain.\n')
note='C357 locally PASSED for one real trial: source-specific native ASAN411+30/TSAN396+30 and actual queue/owner/cancel/wrap/role/startup-failure tests, pinned GNU15.3 strict main231+25 and actual queue/launch allocation-thread fault models, one original-generator-PGO image645+50,77 true noargument/nooverride defaults+9, actual rootMake one C compile+16 public/fresh3623/default composite calls. Local image0a0d2ee777936764db34c2d375d9a615dcb0eb47debe89e77ff1d568ee84e83a/ELF54e7159230c2dd304d8d21e12f294cd6459e42396e692df1fb410de9dd109c6c are replay identities, not organizerELF. Full30/Make/README/file sets proof in docs/round357-candidate-source-match.json. Real C K>23.033578 required; otherwise fullthreefile/originalimage rollback358 and one cooled confirmation.354/356 superseded;355 rejected; exact archives354–357 and honest limits preserved. Original353 snapshot/control remains. PRIVATE/MIT, publication onlyapproved15:00–16:00UTC; runtime+Gitfreeze15:00, risky startsstop14:00.'
for name in ['track-c/PERF.md','docs/RESULTS.md','docs/SUBMISSION.md']:
 p=r/name;p.write_text(p.read_text()+'\n\n'+note+'\n')
p=r/'docs/STATE.md';p.write_text('# C357 fully locally verified; one private real trial pending\n\n'+note+'\n\n43506GNUchain and11428rootMake terminalPASS. No active root compiler/training/model/benchmark/watcher. Other user-authorized chat has359 diagnostic-only GO under exclusive lock; root sole selected runtime/Git/board writer. Its preparation and diagnostic are isolated A/Make guarded, not selected. No new sourcecandidate until real357decision. Do not duplicate completed models/GNUtraining/references; failedtest-only allocator recovery and raw historical label clarification preserved.\n\n'+p.read_text())
shutil.copyfile(Path(__file__),r/'tools/round357-proof/archive354-357.py');print('PASS354–357 exact archive/reconstruction; realtrialpending',flush=True)
