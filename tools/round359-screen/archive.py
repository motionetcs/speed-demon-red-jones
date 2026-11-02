from pathlib import Path
import datetime,hashlib,json,shutil,subprocess,tempfile
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round359';a=r/'tools/round359-screen';a.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
pre=read(w/'preflight.json');decision=read(w/'decision.json');assert decision['decision']=='REJECT_NATIVE_ONLY'
for n in ['prepare.py','diagnose.py','screen.py','compile.json','prepared.json','preflight.json','diagnostic-transforms.json','decision.json']:
 shutil.copy2(w/n,a/n)
for folder in ['diagnostic','confirmation']:
 for p in (w/folder).iterdir():
  if p.is_file()and (p.name in ['report.json','compile.json']or p.suffix in ['.stdout','.stderr']):
   dest=a/folder/p.name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
for name in ['main.cpp','endpoint_table.hpp']:
 p=w/'diagnostic-source/track-a'/name;dest=a/'diagnostic-source'/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,dest)
shutil.copy2(w/'source/track-a/PERF.md',a/'base-a-PERF.md');patch=r/'docs/prototype-patches/round359-a-two-choice-endpoint_table.hpp.patch';shutil.copy2(w/'endpoint_table.hpp.patch',patch)
with tempfile.TemporaryDirectory(prefix='round359-reconstruct-')as temp:
 base=Path(temp)
 for path,h in pre['source_sha256'].items():
  dest=base/path;dest.parent.mkdir(parents=True,exist_ok=True)
  if dest.name=='PERF.md':shutil.copy2(a/'base-a-PERF.md',dest)
  else:dest.write_bytes(subprocess.check_output(['git','show',pre['source_parent']+':'+path],cwd=r))
 q=subprocess.run(['git','apply',str(patch)],cwd=base,capture_output=True,text=True);assert q.returncode==0,q.stderr
 for path,h in pre['source_sha256'].items():assert sha(base/path)==sha(w/'source'/path)==h,path
for path,h in pre['diagnostic_source_sha256'].items():assert sha(w/'diagnostic-source'/path)==h,path
(a/'README.md').write_text('# A359 two-choice cache, native rejection\n\nTwo separately compiled binaries: one unshipped same-key-stream direct-versus-two-choice diagnostic with thread-private counts/equal-ID assertions, then one pure single-table production candidate. Existing exact input/reference bytes reused; no generator/oracle/profile repeated. Diagnostic observer storage/output never enters candidate. The raw diagnostic backslash-n framing is preserved and explicitly parsed by the executed driver.\n\nAround89–91% fewer authoritative-interner cache fallbacks did not establish a time gain.13 paired full cases show public1.010452/full1951 .976985/full2221 1.006815;5/8/6 wins, native RSS slightly lower. Reject before independent hash/relocation/eviction/long-key/ID/race/strict/untrained/GNU/image/default/board proof. Counts and Apple measurements are not Intel/cgroup/totalK/causal evidence. Complete key equality and authoritative fallback were designed, not broadly certified.\n\nExact executed preparation/diagnostic/screen, raw counts and source hashes retained. Recorded353 parent plus one disclosed header patch and frozen PERF reconstruct all12 files; exact diagnostic main/header separately archived. No selected runtime/Git/board changes from the coordinated chat.\n')
report={'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'official_score':False,'selected_in_root':False,'source_parent':pre['source_parent'],'decision':decision,'patch':{'path':str(patch.relative_to(r)),'sha256':sha(patch)},'reconstruction':{'passed':True,'all12_frozen_files_match':True},'archive_files_sha256':{str(p.relative_to(r)):sha(p)for p in a.rglob('*')if p.is_file()}}
(r/'docs/round359-a-cache-rejection.json').write_text(json.dumps(report,indent=2)+'\n');p=r/'track-a/PERF.md';p.write_text(p.read_text()+'\n\n359 two-choice bounded cache: same-stream diagnostic full authoritative fallback calls fall256892→22750/219733→23504/205265→23110 across public/1951/2221, but separately compiled pure production13-pair time ratios1.010452/.976985/1.006815 (5/8/6wins), RSSdelta-311296/-540672/-81920B are flat/mixed. REJECT_NATIVE_ONLY before new collision/relocation/long-key/full-ID/strict/race/untrained/GNU/image/default/board proof. Native counts/timing do not establish Intel/official/causal gain. Exact prepare/observer/production sources/drivers/rawcounts/report/reconstruction: docs/round359-a-cache-rejection.json.\n')
p=r/'track-d/PERF.md';p.write_text(p.read_text()+'\n\nRead-only duplicate audit during357/358: cumulative actual scanned-edge direction policy exactly matches rejected298; eight-lane AVX2 same-bucket lookup matches actual-losing124. Both stopped before any new runtime code/compiler/benchmark/model/training/board run. Primary conceptual sources rechecked: https://arxiv.org/html/2410.14638v3 and https://arxiv.org/html/2608.26952v1 (later paper questions earlier instance-optimality analysis; neither theorem certifies this zero-weight/banded implementation); Intel intrinsic guide https://www.intel.com/content/www/us/en/docs/intrinsics-guide/index.html . No imported implementations, played-video claim, target or new correctness proof. Current D334 remains exact.\n')
shutil.copyfile(Path(__file__),a/'archive.py');print('PASS359 archive/reconstruction; native-only rejection, no runtime change')
