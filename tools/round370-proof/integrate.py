from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess,tempfile
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round370';s=w/'source'
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,j):p.write_text(json.dumps(j,indent=2)+'\n')
pre=read(w/'preflight.json');prior=read(r/'docs/round363-final-source-match.json');head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip()
assert head==pre['source_parent']==prior['source_commit']=='72b55e083ab3251e4687f1e03df32625bccfd6c1'
assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,11,2,14,tzinfo=datetime.timezone.utc)
assert not(r/'docs/round370-candidate-source-match.json').exists()
proofs={m:read(w/f'proof/{m}/report.json')for m in ['fresh','build','image','defaults']};native=read(w/'native-proof/report.json');gnu=read(r/'.build/round370-other-gnu/result/report.json');headers=read(w/'header-proof/report.json')
assert all(p['passed']for p in [*proofs.values(),native,gnu,headers])
for p,h in pre['source_sha256'].items():assert sha(s/p)==h,p
for p,h in pre['root_selected_bindings'].items():assert sha(r/p)==h,p
for p,h in pre['unchanged_C_headers_sha256'].items():assert sha(s/p)==sha(r/p)==h,p
for name in ['main.cpp','README.md']:assert(r/'track-c'/name).read_bytes()==(w/'original-retained/track-c'/name).read_bytes();shutil.copyfile(s/'track-c'/name,r/'track-c'/name)
archive=r/'tools/round370-proof';archive.mkdir();shutil.copy2(Path(__file__),w/'integrate.py')
for p in w.iterdir():
 if p.is_file()and(p.suffix in ['.py','.hpp','.cpp']or p.name in ['preflight.json','proof-manifest.json','compile.json','header-attempt1-failure.json','production-inventory-attempt1-failure.json']):shutil.copy2(p,archive/p.name)
shutil.copy2(s/'track-c/PERF.md',archive/'base-c-PERF.md')
for folder in ['native-proof','header-proof','proof/build','proof/image','proof/defaults']:
 dest=archive/'raw'/folder;dest.mkdir(parents=True)
 for p in(w/folder).iterdir():
  if p.is_file()and p.name in ['report.json','model.json','field-model.compile.json','track-c.compile.json','gcc.txt','model-attempt.json','fresh-asan-3851.stdout','fresh-asan-3851.stderr','fresh-tsan-3853.stdout','fresh-tsan-3853.stderr','fresh-asan-3863.stdout','fresh-asan-3863.stderr','build.stdout','build.stderr','inspect.stdout','inspect.stderr','original-config.stdout','original-config.stderr','elf.stdout','elf.stderr','replay.stdout','replay.stderr']:shutil.copy2(p,dest/p.name)
for mode in ['asan','tsan']:
 dest=archive/'raw/native-proof'/mode;dest.mkdir(parents=True)
 for p in(w/'native-proof'/mode).iterdir():
  if p.is_file()and p.suffix=='.json':shutil.copy2(p,dest/p.name)
other=r/'.build/round370-other-gnu';dest=archive/'other-gnu';dest.mkdir()
manifest=read(other/'manifest.json');assert manifest['proof_passed']and manifest['terminal_exit_code']==0
for p in other.iterdir():
 if p.is_file():shutil.copy2(p,dest/p.name)
(dest/'result').mkdir()
for p in(other/'result').iterdir():
 if p.is_file()and p.suffix not in ['']and p.name not in ['solution','raw-fields','numeric']:
  shutil.copy2(p,dest/'result'/p.name)
patches=[]
for name in ['main.cpp','README.md']:
 p=r/f'docs/prototype-patches/round370-c-raw-fields-{name}.patch';shutil.copy2(w/(name+'.patch'),p);patches.append({'path':str(p.relative_to(r)),'sha256':sha(p)})
shutil.copy2(w/'preflight.json',r/'docs/round370-preflight.json');shutil.copy2(other/'result/report.json',r/'docs/round370-c-gnu-proof.json')
with tempfile.TemporaryDirectory(prefix='round370-reconstruct-')as tmp:
 base=Path(tmp)
 for p,h in pre['source_sha256'].items():
  d=base/p;d.parent.mkdir(parents=True,exist_ok=True)
  if d.name=='PERF.md':shutil.copyfile(archive/'base-c-PERF.md',d)
  else:d.write_bytes(subprocess.check_output(['git','show',head+':'+p],cwd=r))
 for row in patches:q=subprocess.run(['git','apply',str(r/row['path'])],cwd=base,capture_output=True,text=True);assert q.returncode==0,q.stderr
 for p,h in pre['source_sha256'].items():assert sha(base/p)==h,p
reconstruction={'passed':True,'source_parent':head,'frozen_files':len(pre['source_sha256']),'scope':'All10 frozen C context files reconstructed from parent plus2 disclosed patches and exact excluded PERF snapshot.'};dump(r/'docs/round370-archive-reconstruction.json',reconstruction)
folder=w/'final-make';folder.mkdir();controls={'a':r/'.build/round263/final-make/track-a','c':w/'track-c-bin','d':r/'.build/round334/final-make/track-d'}
compile=read(w/'compile.json');assert compile['returncode']==0 and not compile['stderr']and compile['command'][1:9]==['-std=c++20','-O3','-DNDEBUG','-Wall','-Wextra','-Wpedantic','-pthread',str(s/'track-c/main.cpp')]
assert sha(r/'Makefile')==pre['root_selected_bindings']['Makefile']
for t,p in controls.items():shutil.copyfile(p,folder/f'track-{t}');(folder/f'track-{t}').chmod(0o755);assert sha(folder/f'track-{t}')==sha(p)
cmd=['make','BUILD_DIR=.build/round370/final-make','all'];q=subprocess.run(cmd,cwd=r,capture_output=True,text=True,timeout=180);dump(w/'Make.json',{'command':cmd,'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr,'scope':'Actual rootMake uses exact-source native binaries: A263,currentD334, and370 one initial native compile with exact Make flags/current compiled headers. No repeat compiler.'});assert q.returncode==0 and not q.stderr and 'clang++'not in q.stdout and 'g++'not in q.stdout,(q.stdout,q.stderr)
pub=read(r/'docs/public-sha256.json')['tracks'];runs=[]
def replay(t,data,inputs,expected,threads,label):
 assert{p.name:sha(p)for p in data.iterdir()if p.is_file()}==inputs;dest=w/'combined-native'/t/label;dest.mkdir(parents=True);env=dict(os.environ);env.pop('SPEED_DEMON_THREADS',None)
 if threads is not None:env['SPEED_DEMON_THREADS']=str(threads)
 q=subprocess.run([str(folder/f'track-{t}'),'--data',str(data),'--out',str(dest)],capture_output=True,text=True,env=env,timeout=180);assert q.returncode==0 and not q.stdout and not q.stderr,(t,threads,q.returncode,q.stderr)
 assert[p.name for p in dest.iterdir()]==[pub[t]['output']];actual=sha(dest/pub[t]['output']);assert actual==expected
 assert{p.name:sha(p)for p in data.iterdir()if p.is_file()}==inputs;runs.append({'track':t,'case':label,'requested_threads':threads,'native_default12':threads is None,'binary_sha256':sha(folder/f'track-{t}'),'inputs_sha256':inputs,'sha256':actual})
for t in 'acd':
 for threads in [1,6,12,None]:replay(t,r/f'.data/{t}/public-full-seed1',pub[t]['inputs_sha256'],pub[t]['expected_output_sha256'][0],threads,'public-'+('default'if threads is None else str(threads)))
fresh=read(r/'docs/round370-c-asan-fresh-full3863.json');row=next(x for x in fresh['checks']if x['case']=='full-seed3863');data=r/'.data/c/full-seed3863';hashes={p.name:sha(p)for p in data.iterdir()if p.is_file()}
for threads in [1,6,12,None]:replay('c',data,hashes,row['reference_sha256'],threads,'full3863-'+('default'if threads is None else str(threads)))
inputs=[]
for old in prior['inputs']:
 p=old['path'];h=sha(r/p)
 if p.startswith('track-c/'):assert h==pre['source_sha256'][p];image=proofs['build']['image_id']
 else:assert h==old['sha256'];image=prior['images'][p[6]]
 inputs.append({'path':p,'sha256':h,'image_id':image,'scope':'370 rawcanonical/count field simplification; other runtime/build inputs remain original source. Local image identity, not organizer ELF.'})
assert len(inputs)==30;sets={};readmes={};submitted=w/'submitted-source';submitted.mkdir()
for t in 'acd':
 names=sorted(str(p.relative_to(r))for p in(r/f'track-{t}').iterdir()if p.is_file()and p.name!='PERF.md');assert names==prior['complete_file_sets_excluding_PERF'][t];sets[t]=names;readmes[t]=sha(r/f'track-{t}/README.md')
 for p in names:d=submitted/p;d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(r/p,d)
shutil.copyfile(r/'Makefile',submitted/'Makefile');images=dict(prior['images'],c=proofs['build']['image_id'])
pa={'passed':True,'official_score':False,'source_parent':head,'scope':pre['scope'],'preflight_sha256':sha(r/'docs/round370-preflight.json'),'patches':patches,'archive_reconstruction':reconstruction,'proof_reports':{str(p.relative_to(r)):sha(p)for p in(r/'docs').glob('round370-c-*.json')},'executed_proof_drivers':{str(p.relative_to(r)):sha(p)for p in archive.rglob('*')if p.is_file()},'source_review':{'path':'.build/round370-review/review.md','sha256':sha(r/'.build/round370-review/review.md')},'image_id':images['c'],'elf_sha256':proofs['build']['elf_sha256'],'limitations':'Native timings mixed; fresh3863 +2.059% time,4/13 wins; native RSS is not charged memory. Canonical S and totalK unmeasured until one real board trial. Fresh exact parser/header/native ASAN/TSAN+GNU strict+one production image/default checks are evidence for correctness, not eligibility or victory. Original parallel header remains original363; no357 cancellation/startup-failure model proof transferred. Two fixture/inventory adapter failures preserved; no completed compiler/model/generator/oracle/PGO repeated.'}
review=archive/'semantic-review';review.mkdir()
for p in(r/'.build/round370-review').iterdir():
 if p.is_file():shutil.copy2(p,review/p.name)
pa['executed_proof_drivers']={str(p.relative_to(r)):sha(p)for p in archive.rglob('*')if p.is_file()};dump(r/'docs/round370-proof-archive.json',pa)
proof={'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'official_score':False,'actual_board_confirmation_pending':True,'source_parent':head,'inputs':inputs,'Makefile_sha256':sha(r/'Makefile'),'images':images,'complete_file_sets_excluding_PERF':sets,'README_sha256':readmes,'native_public_default_runs':runs,'c_image':{'id':images['c'],'elf_sha256':proofs['build']['elf_sha256'],'bytes':proofs['build']['image_bytes']},'proof_archive':'docs/round370-proof-archive.json','scope':'New rawcanonical/count-only Csv removes unused decode/scratch/escaped result. Same quote-free expected header acceptance, full byte counts, records and original worker/name protocol; A178/D334 unchanged. All30/root/submitted/Make/fullsets/README/local image bound. Retain only real C K>23.033578/68.118071; otherwise full main/README/image rollback.'};dump(r/'docs/round370-candidate-source-match.json',proof)
note=f"C370 locally validated for ONE official source-simplification trial. Current555050 raw/count/header/bounds model; ASAN411+30 and TSAN396+30 main plus fresh3851/3853/3863; new actual-header integration441valid+90error calls; pinnedGNU15.3 raw555050/numeric402810 and159+10 actualmain PASS. ONE original allowed full1000003/sample130363 PGO image {images['c']}, ELF {proofs['build']['elf_sha256']}, image{len(proofs['image']['runs'])}+{len(proofs['image']['expected_failures'])}, actual noarg/nooverride defaults{len(proofs['defaults']['runs'])}+{len(proofs['defaults']['expected_failures'])}, cached actualMake/native16 PASS. Local identities are not organizer identities. Native timing weak/mixed, fresh3863 paired1.0205925954/4wins, RSS not chargedM; exact canonicalS/totalK only realboard. No GNU/image/PGO proof repetitions, source-specific cancellation fault proof not transferred. Only main/README changed, original headers/default12/ISA/PGO untouched; preserve passing363 snapshot. Keep only C K>23.033578/points68.118071, else full main/README/image rollback and one cooled confirmation. Exact archive docs/round370-proof-archive.json. PRIVATE/MIT, publication only approved15:00–16:00UTC; stop risky14:00/runtime+Git15:00."
for name in ['track-c/PERF.md','docs/RESULTS.md','docs/SUBMISSION.md']:
 p=r/name;p.write_text(p.read_text()+'\n\n'+note+'\n')
p=r/'docs/STATE.md';p.write_text('# C370 validated; ONE private official trial pending\n\n'+note+'\n\nHEADstilloriginal363; current candidate main/README integrated only after full proof. Source30 and rollback snapshot protected; no new A/D work until real decision.\n\n'+p.read_text())
dump(w/'ACTIVE.json',{'status':'local_candidate_proof_passed','selected_in_root':True,'actual_board_pending':True,'note':note});print('PASS370 localcandidate/all30/native16/archive/exactimage/default; official trial pending',flush=True)
