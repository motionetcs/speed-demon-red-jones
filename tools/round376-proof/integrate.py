from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess,tempfile
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round376';s=w/'source'
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,j):p.write_text(json.dumps(j,indent=2)+'\n')
pre=read(w/'preflight.json');prior=read(r/'docs/round371-final-source-match.json');head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip();assert head==pre['source_parent']==prior['source_commit']=='83630432c7acd216b9813027a2e863fe0fd8aaee';assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,11,2,14,tzinfo=datetime.timezone.utc);assert not(r/'docs/round376-candidate-source-match.json').exists()
proofs={m:read(w/f'proof/{m}/report.json')for m in ['gnu','build','image','defaults']};native=read(w/'native-proof/report.json');fresh=read(w/'fresh-confirmation/report.json');assert all(x['passed']for x in [*proofs.values(),native,fresh]);review=r/'.build/round376-review';assert(review/'binding.json').exists()
for p,h in pre['source_sha256'].items():assert sha(s/p)==h,p
for p,h in pre['root_selected_bindings'].items():assert sha(r/p)==h,p
for name in ['main.cpp','README.md']:shutil.copyfile(s/'track-a'/name,r/'track-a'/name)
archive=r/'tools/round376-proof';archive.mkdir();shutil.copy2(Path(__file__),w/'integrate.py')
for p in w.iterdir():
 if p.is_file()and(p.suffix in ['.py','.hpp','.cpp']or p.name in ['preflight.json','compile.json','partition-model-manifest.json','native-proof-attempt1-failure.json']):shutil.copy2(p,archive/p.name)
shutil.copy2(s/'track-a/PERF.md',archive/'base-a-PERF.md');(archive/'semantic-review').mkdir()
for p in review.iterdir():
 if p.is_file():shutil.copy2(p,archive/'semantic-review'/p.name)
for folder in ['native-proof','proof/gnu','proof/build','proof/image','proof/defaults']:
 dest=archive/'raw'/folder;dest.mkdir(parents=True)
 for p in(w/folder).iterdir():
  if p.is_file()and p.name in ['report.json','gcc.txt','model.stdout','model.stderr','executed.sh','replay.stdout','replay.stderr','build.stdout','build.stderr','inspect.stdout','inspect.stderr','original-config.stdout','original-config.stderr','elf.stdout','elf.stderr','solution.sha256']:shutil.copy2(p,dest/p.name)
for mode in ['asan','tsan']:
 dest=archive/'raw/native-proof'/mode;dest.mkdir(parents=True)
 for p in(w/'native-proof'/mode).iterdir():
  if p.is_file()and(p.suffix=='.json'or p.name in ['fresh.stdout','fresh.stderr']):shutil.copy2(p,dest/p.name)
patches=[]
for name in ['main.cpp','README.md']:
 dest=r/f'docs/prototype-patches/round376-a-dynamic4m-{name}.patch';shutil.copy2(w/(name+'.patch'),dest);patches.append({'path':str(dest.relative_to(r)),'sha256':sha(dest)})
shutil.copy2(w/'preflight.json',r/'docs/round376-preflight.json')
with tempfile.TemporaryDirectory(prefix='round376-reconstruct-')as tmp:
 base=Path(tmp)
 for p,h in pre['source_sha256'].items():
  dest=base/p;dest.parent.mkdir(parents=True,exist_ok=True)
  if dest.name=='PERF.md':shutil.copyfile(archive/'base-a-PERF.md',dest)
  else:dest.write_bytes(subprocess.check_output(['git','show',head+':'+p],cwd=r))
 for row in patches:q=subprocess.run(['git','apply',str(r/row['path'])],cwd=base,capture_output=True,text=True);assert q.returncode==0,q.stderr
 for p,h in pre['source_sha256'].items():assert sha(base/p)==h,p
reconstruction={'passed':True,'source_parent':head,'frozen_files':len(pre['source_sha256']),'scope':'All12 frozen A files reconstruct from371 plus2 disclosed patches and exact excluded PERF snapshot. Original preparation was a logged inline command; no fabricated saved preparation-driver execution.'};dump(r/'docs/round376-archive-reconstruction.json',reconstruction)
folder=w/'final-make';folder.mkdir();controls={'a':w/'track-a-bin','c':r/'.build/round263/final-make/track-c','d':r/'.build/round334/final-make/track-d'};compile=read(w/'compile.json');assert compile['returncode']==0 and not compile['stderr']and compile['command'][1:9]==['-std=c++20','-O3','-DNDEBUG','-Wall','-Wextra','-Wpedantic','-pthread',str(s/'track-a/main.cpp')];assert sha(r/'Makefile')==pre['root_selected_bindings']['Makefile'];assert sha(controls['a'])==read(w/'confirmation/report.json')['binary_sha256']['candidate']
for t,p in controls.items():shutil.copyfile(p,folder/f'track-{t}');(folder/f'track-{t}').chmod(0o755);assert sha(folder/f'track-{t}')==sha(p)
cmd=['make','BUILD_DIR=.build/round376/final-make','all'];q=subprocess.run(cmd,cwd=r,capture_output=True,text=True,timeout=180);dump(w/'Make.json',{'command':cmd,'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr,'scope':'Actual root Make uses exact-source376 initial optimized native ELF and unchanged C263/current D334 cached controls. Same Make flags, no repeated compiler.'});assert q.returncode==0 and not q.stderr and 'clang++'not in q.stdout and 'g++'not in q.stdout,(q.stdout,q.stderr)
pub=read(r/'docs/public-sha256.json')['tracks'];runs=[]
def replay(t,data,inputs,expected,threads,label):
 assert{p.name:sha(p)for p in data.iterdir()if p.is_file()}==inputs;dest=w/'combined-native'/t/label;dest.mkdir(parents=True);env=dict(os.environ);env.pop('SPEED_DEMON_THREADS',None)
 if threads is not None:env['SPEED_DEMON_THREADS']=str(threads)
 q=subprocess.run([str(folder/f'track-{t}'),'--data',str(data),'--out',str(dest)],capture_output=True,text=True,env=env,timeout=180);assert q.returncode==0 and not q.stdout and not q.stderr,(t,threads,q.returncode,q.stderr);assert[p.name for p in dest.iterdir()]==[pub[t]['output']];actual=sha(dest/pub[t]['output']);assert actual==expected;assert{p.name:sha(p)for p in data.iterdir()if p.is_file()}==inputs;runs.append({'track':t,'case':label,'requested_threads':threads,'native_default12':threads is None,'binary_sha256':sha(folder/f'track-{t}'),'inputs_sha256':inputs,'sha256':actual})
for t in 'acd':
 for threads in [1,6,12,None]:replay(t,r/f'.data/{t}/public-full-seed1',pub[t]['inputs_sha256'],pub[t]['expected_output_sha256'][0],threads,'public-'+('default'if threads is None else str(threads)))
data=r/'.data/a/full-seed3911';inputs={p.name:sha(p)for p in data.iterdir()if p.is_file()};expected=fresh['expected_sha256']
for threads in [1,6,12,None]:replay('a',data,inputs,expected,threads,'full3911-'+('default'if threads is None else str(threads)))
inputs=[]
for old in prior['inputs']:
 p=old['path'];h=sha(r/p)
 if p.startswith('track-a/'):assert h==pre['source_sha256'][p];image=proofs['build']['image_id']
 else:assert h==old['sha256'];image=prior['images'][p[6]]
 inputs.append({'path':p,'sha256':h,'image_id':image,'scope':'A376 dynamic4MiB parser jobs; other runtime/build inputs remain original371. Local image identity, not organizer ELF.'})
assert len(inputs)==30;sets={};readmes={};submitted=w/'submitted-source';submitted.mkdir()
for t in 'acd':
 names=sorted(str(p.relative_to(r))for p in(r/f'track-{t}').iterdir()if p.is_file()and p.name!='PERF.md');assert names==prior['complete_file_sets_excluding_PERF'][t];sets[t]=names;readmes[t]=sha(r/f'track-{t}/README.md')
 for p in names:dest=submitted/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(r/p,dest)
shutil.copyfile(r/'Makefile',submitted/'Makefile');images=dict(prior['images'],a=proofs['build']['image_id'])
(archive/'README.md').write_text('# A376 dynamic parser trial\n\nSame requested workers claim immutable newline-aligned4MiB ranges from one atomic counter, keeping their original private cache/hour/wide-escape state. Original body and downstream aggregation/output are exact. The initial reserve remains the original average per-worker byte estimate, not rejected374reserve512.\n\nOne initial optimized compile and saved controls were reused. Fresh full3911 paired.932848/11of13 wins and earlier.967164/.972460/.954856 are native hypotheses, not Intel/cgroup/K. New source-extracted range/claim model passes10750042 checks in each ASAN/UBSAN andTSAN, and again on pinned GNU; new55.6MB shuffled325000-row4096-endpoint fixture activates more than12 real jobs and matches an independent full-sort oracle plus one official reference. Native actualmain114+6/105+6 and fresh3923/3929 samples pass. Pinned genericGNU78+6, one unchanged allowed full1000003/sample130363 PGO image123+6,26 actual defaults+2 and cached rootMake/native16 pass. Source-byte-bound unchanged headers are provenance; no C357 fault/cancellation proof is transferred.\n\nOne initial Python SyntaxError occurred before any execution and is preserved; no completed generation/reference/compiler/model/PGO repeated. Original prototype preparation was a logged inline Python invocation, not a saved pre-execution file. Parent371+two patches+frozen PERF reconstruct all12 context files; no historical preparation script is fabricated. Real A totalK must exceed32.070167/75.305061 to retain, otherwise full main/README/original image rollback.\n')
pa={'passed':True,'official_score':False,'source_parent':head,'scope':pre['scope'],'preflight_sha256':sha(r/'docs/round376-preflight.json'),'patches':patches,'archive_reconstruction':reconstruction,'proof_reports':{str(p.relative_to(r)):sha(p)for p in(r/'docs').glob('round376-a-*.json')},'executed_proof_drivers':{str(p.relative_to(r)):sha(p)for p in archive.rglob('*')if p.is_file()},'image_id':images['a'],'elf_sha256':proofs['build']['elf_sha256'],'preparation_provenance':'Logged original inline Python command; no saved pre-execution prepare.py. Reconstruction is exact byte proof, not evidence of an invented driver execution.','limitations':'Native process timing/RSS not Intel/cgroup/K; exact canonical S and totalK pending real board. New independent scheduler/current-main proofs cover changed behavior; original source-byte-bound allocator/cache/decimal/writer provenance is distinguished from new execution.'};dump(r/'docs/round376-proof-archive.json',pa)
proof={'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'official_score':False,'actual_board_confirmation_pending':True,'source_parent':head,'inputs':inputs,'Makefile_sha256':sha(r/'Makefile'),'images':images,'complete_file_sets_excluding_PERF':sets,'README_sha256':readmes,'native_public_default_runs':runs,'a_image':{'id':images['a'],'elf_sha256':proofs['build']['elf_sha256'],'bytes':proofs['build']['image_bytes']},'proof_archive':'docs/round376-proof-archive.json','scope':'A376 dynamic exact newline parser job assignment only, same requested workers/private state/unchanged data rules and original downstream code. All30/root/submitted/Make/fullsets/README/local images match. C175/D334 unchanged. Keep only supported actual A K>32.070167/75.305061, else full main/README/original A image rollback.'};dump(r/'docs/round376-candidate-source-match.json',proof)
note=f"A376 locally validated for ONE real dynamic-parser trial. Same requestedworkers claim4MiB newline jobs, exact original parser/private state/downstream output; no host scheduling/seed/domain/answer shortcuts. Native3full paired.967164/.972460/.954856; fresh independent3911.932848/11wins,RSS+262144B are hypotheses. Source-extracted partition/claim model10750042 checks EACH nativeASAN/UBSAN,TSAN and genericGNU; new55.6MB325000-row shuffled4096endpoint fixture independent full-sort/oneofficialref; actualmainASAN114+6/TSAN105+6 plus fresh3923/3929 pass. PinnedGNU78+6, ONE original allowedPGO image123+6,26 true noargument/nooverride defaults+2, cached actualMake/native16 PASS. Local image{images['a']}/ELF{proofs['build']['elf_sha256']} are not organizer identities. Actual S/K unmeasured until board. Keep only A K>32.070167/75.305061; otherwise full main/README/image rollback. Exact all30/source/Make/fullsets/archive/snapshot proof docs/round376-candidate-source-match.json. C/D unchanged; PRIVATE/MIT, stop risky14:00/runtime+Git15:00/publication ONLY approved15:00–16:00UTC."
for name in ['track-a/PERF.md','docs/RESULTS.md','docs/SUBMISSION.md']:
 p=r/name;p.write_text(p.read_text()+'\n\n'+note+'\n')
p=r/'docs/STATE.md';p.write_text('# A376 locally validated; ONE private real trial pending\n\n'+note+'\n\nHEADstilloriginal371; A376 main/README integrated only after all proof. Source snapshot .build/round376/submitted-source; complete rollback original371 snapshot retained. No new candidate before actual result. All proof sessions terminal; root sole source/Git/board writer, peer review sealed/CPUHOLD.\n\n'+p.read_text());dump(w/'ACTIVE.json',{'status':'local_candidate_proof_passed','selected_in_root':True,'actual_board_pending':True,'note':note});print('PASS376 localcandidate/all30/native16/archive/exactimage/default; ONE real trial pending',flush=True)
