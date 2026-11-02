from pathlib import Path
import datetime,hashlib,json,shutil,subprocess,tempfile
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip()=='72b55e083ab3251e4687f1e03df32625bccfd6c1'
a=r/'tools/round364-review';a.mkdir()
for p in(r/'.build/round364').iterdir():
 if p.is_file():shutil.copy2(p,a/p.name)
(a/'README.md').write_text('# A364 read-only eligibility and algebra\n\nSame16B/4..12 exact-key encoding was rejected before implementation: only3.462/1.267/1.626% of actual calls qualify. Counts come from already-validated359 summary group multiplicities, not unique-key lengths, a rawinput pass, or a new program/profile. Hit-by-length joint counts unavailable; bounds only. Expanded32B/4..28 proposal covers44.712/40.409/53.359% but doubles cache bytes; array size is not processRSS/chargedM. Read-only algebra/union/bounds review is not a model/compiler/runtime/general-correctness certificate. No candidate, test/model/benchmark/compiler/generator/oracle/training/board run occurred in364.\n')
w=r/'.build/round365';a=r/'tools/round365-screen';a.mkdir()
for name in ['prepare.py','screen.py','preflight.json','compile.json']:shutil.copy2(w/name,a/name)
shutil.copy2(w/'confirmation/report.json',a/'report.json');shutil.copy2(w/'source/track-a/PERF.md',a/'base-a-PERF.md')
review=r/'.build/round365-review'
for p in review.iterdir():
 if p.is_file():shutil.copy2(p,a/('review-'+p.name))
patch=r/'docs/prototype-patches/round365-a-exact28-endpoint_table.hpp.patch';shutil.copy2(w/'endpoint_table.hpp.patch',patch);pre=read(w/'preflight.json');screen=read(w/'confirmation/report.json');assert screen['passed']
with tempfile.TemporaryDirectory(prefix='round365-reconstruct-')as tmp:
 base=Path(tmp)
 for path,h in pre['source_sha256'].items():
  dest=base/path;dest.parent.mkdir(parents=True,exist_ok=True)
  if dest.name=='PERF.md':shutil.copy2(a/'base-a-PERF.md',dest)
  else:dest.write_bytes(subprocess.check_output(['git','show',pre['source_parent']+':'+path],cwd=r))
 q=subprocess.run(['git','apply',str(patch)],cwd=base,capture_output=True,text=True);assert q.returncode==0,q.stderr
 for path,h in pre['source_sha256'].items():assert sha(base/path)==sha(w/'source'/path)==h,path
summary={k:{'paired_median_ratio':v['paired_median_ratio'],'paired_wins':v['paired_wins'],'native_rss_delta_bytes':v['variants']['candidate']['median_native_rss_bytes']-v['variants']['control']['median_native_rss_bytes']}for k,v in screen['summary'].items()}
(a/'README.md').write_text('# A365 exact4..28-byte cache encoding, native rejection\n\nComplete-key representation uses three8-byte payloadwords, the unchangedfull32 sampledhash and full length/ID in align32 slots. Input-key-derived caching only, no precomputedanswers or catalogue recognition.4..7/8..24 samplecoverage and25..28 conditionalbijection reasoning reviewed; encoded() internalprecondition4..28 only. Exact sharedglobalprefix/hashfunction and all other A files unchanged.\n\nOne optimizedcompile/90calls fullpublic1/6/12 plus13 rotatingpairs public/full1951/full2221 pass all source/input/output/control/candidatehashes. Ratios.998224/1.005213/1.011549 and7/5/5wins are flat/losing with mixed nativeRSS. REJECT_NATIVE_ONLY before new exact-key/forcedcollision/unionlifetime/guard/unaligned/endian/long/full-ID/strict/race/untrained/GNU/image/default/board proof. Read-only mathematical/source review found no concrete guarded counterexample but is not a correctness certificate. Header/source growth/cache bytes would be charged normally. Apple timing/RSS is not Intel/chargedM/officialgain. Recordedparent +onepatch +frozen excludedPERF reconstruct all12files exactly.\n')
record={'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'official_score':False,'selected_in_root':False,'decision':'REJECT_NATIVE_ONLY','source_parent':pre['source_parent'],'scope':pre['scope'],'screen_summary':summary,'screen_calls':len(screen['runs']),'reconstruction':{'passed':True,'all12_frozen_files_match':True},'patch':{'path':str(patch.relative_to(r)),'sha256':sha(patch)},'archive_files_sha256':{str(p.relative_to(r)):sha(p)for p in a.iterdir()if p.is_file()},'readonly364':{str(p.relative_to(r)):sha(p)for p in(r/'tools/round364-review').iterdir()if p.is_file()},'limits':'Only full legal-data screen and read-only reasoning; no broad strict/model/race/untrained/GNU/image/actual proof. No root runtime or board change.'};(r/'docs/round364-365-a-cache-rejection.json').write_text(json.dumps(record,indent=2)+'\n')
p=r/'track-a/PERF.md';p.write_text(p.read_text()+'\n\n364 read-only same16B4..12 exactencoding rejected beforeimplementation: actualcallcoverage3.462/1.267/1.626%, weightedfromalreadyvalidated359summary multiplicities, hit-lengthjointcounts absent. Wider32B4..28 coverage44.712/40.409/53.359% motivated isolated365. Onecompile/90legaldata fullpublic1/6/12/threefull13-pair input/output/source/binaryhashesPASS;365 ratios.998224/1.005213/1.011549 (7/5/5wins), nativeRSS-114688/-81920/+245760B flat/mixed. REJECT before broad exactkey/union/guard/collision/endian/ID/strict/race/untrained/GNU/image/default/board proof. Readonlybijection/bounds/source argument is not correctness or Intelgain. No selectedruntime change. Exact sources/drivers/patch/reconstruction/traffic/review: docs/round364-365-a-cache-rejection.json.\n');shutil.copyfile(Path(__file__),a/'archive364-365.py');print('ARCHIVED364readonly/365native-only rejection; exactreconstructionPASS')
