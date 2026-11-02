from pathlib import Path
import datetime,hashlib,json,shutil
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
index=[]
for n in [360,361]:
 w=r/f'.build/round{n}';a=r/f'tools/round{n}-review';a.mkdir()
 if n==360:
  names=['inspect.py','report.json','findings.md','manifest.json']
  for name in names:
   if(w/name).exists():shutil.copy2(w/name,a/name)
  assert(a/'inspect.py').exists()and(a/'report.json').exists()and(a/'findings.md').exists()
  scope='Read-only original C263 production ELF/disassembly source binding and IFUNCPLT inspection; no compiler/program/profile/training/benchmark/image/board fetch. Four static equality PLT callsites in defaultnarrowworker, not dynamicfrequency/cost. Exact existing ELF/disassembly hashes retained, binaries not tracked. No A/D emittedpath evidence inferred.'
 else:
  for name in ['probe.py','probe.cpp','report.json','stdout','stderr']:shutil.copy2(w/name,a/name)
  for p in(w/'out').iterdir():
   if p.suffix=='.txt':shutil.copy2(p,a/p.name)
  scope='One unshipped minimal staticIFUNC equality-call probe, two explicit pinnedGNU15.3 compiler/link modes baseline/fno-plt and smokeinvocations. Expected direct PLT call vs FF15 GOT call confirmed. No PGO, timing, source-production correctness, wholeproduction emission or official gain claim. No selected source changes, no source-dependent models repeated.'
 (a/'README.md').write_text(f'# Round{n} compiler feasibility evidence\n\n'+scope+'\n\nPrimary GCC documentation: https://gcc.gnu.org/onlinedocs/gcc/Code-Gen-Options.html . The option avoids a PLT stub via GOT calls where supported. Actual current-production callshape and target performance must be separately checked; static linking can retain IFUNC stubs for unchanged prebuilt libraries. No vendor or competitor implementation copied.\n')
 index.append({'round':n,'official_score':False,'selected_in_root':False,'scope':scope,'artifacts_sha256':{str(p.relative_to(r)):sha(p)for p in a.iterdir()if p.is_file()}})
(r/'docs/round360-361-compiler-feasibility.json').write_text(json.dumps({'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'official_score':False,'evidence':index,'candidate362_status':'Isolated Linux proof complete, actual emitted hotcall review and rootMake/source30 proof required before real trial.'},indent=2)+'\n');print('Archived360 read-only and361 minimal probe; no runtime/timing gain')
