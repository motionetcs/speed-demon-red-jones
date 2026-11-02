from pathlib import Path
import datetime,difflib,hashlib,json,os,shutil,subprocess,tempfile
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round384';s=w/'source';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();read=lambda p:json.loads(Path(p).read_text());dump=lambda p,x:Path(p).write_text(json.dumps(x,indent=2)+'\n');pre=read(w/'final-source.json');prior=read(r/'docs/round377-final-source-match.json');head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip();assert head==pre['source_parent']==prior['source_commit']=='77904f6fba5375cb0d3e7e8d738ba681b61d7971';assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,11,2,14,tzinfo=datetime.timezone.utc);assert not(r/'docs/round384-candidate-source-match.json').exists()
proofs={mode:read(w/'proof'/mode/'report.json')for mode in ['gcc','build','image','defaults']};native=read(w/'native-proof/report.json');assert all(x['passed']for x in[*proofs.values(),native]);assert len(native['matrices'])==2 and len(native['models'])==2
for p,h in pre['source_sha256'].items():assert sha(s/p)==h
for p,h in pre['root_selected_bindings'].items():assert sha(r/p)==h
original=w/'original-retained';original.mkdir();shutil.copytree(r/'track-c',original/'track-c');shutil.copy2(r/'Makefile',original/'Makefile')
for name in ['main.cpp','names.hpp','README.md']:shutil.copyfile(s/'track-c'/name,r/'track-c'/name)
a=r/'tools/round384-proof';a.mkdir();shutil.copy2(Path(__file__),w/'integrate.py')
for p in w.iterdir():
 if p.is_file()and(p.suffix in['.py','.cpp']or p.name in['preflight.json','final-source.json','compile.json','native-inventory-attempt1-failure.json']):shutil.copy2(p,a/p.name)
shutil.copy2(s/'track-c/PERF.md',a/'base-c-PERF.md')
patches=[]
for name in ['main.cpp','names.hpp','README.md']:
 old=subprocess.check_output(['git','show',head+':track-c/'+name],cwd=r).decode();new=(s/'track-c'/name).read_text();dest=r/f'docs/prototype-patches/round384-c-fixed4-{name}.patch';dest.write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile=f'a/track-c/{name}',tofile=f'b/track-c/{name}')));patches.append({'path':str(dest.relative_to(r)),'sha256':sha(dest)})
# Initial timing source remains separately reconstructible; final proof uses final exact main.
shutil.copy2(w/'main.cpp.patch',a/'initial-native-main.cpp.patch')
with tempfile.TemporaryDirectory(prefix='round384-reconstruct-')as tmp:
 base=Path(tmp)
 for p,h in pre['source_sha256'].items():
  dest=base/p;dest.parent.mkdir(parents=True,exist_ok=True)
  if dest.name=='PERF.md':shutil.copy2(a/'base-c-PERF.md',dest)
  else:dest.write_bytes(subprocess.check_output(['git','show',head+':'+p],cwd=r))
 for row in patches:
  q=subprocess.run(['git','apply',str(r/row['path'])],cwd=base,capture_output=True,text=True);assert q.returncode==0,q.stderr
 for p,h in pre['source_sha256'].items():assert sha(base/p)==h
reconstruction={'passed':True,'source_parent':head,'files':len(pre['source_sha256']),'scope':'All10 final C context files reconstructed from parent plus3 exact disclosed patches and frozen excluded PERF; initial timing main separately bound in final-source.json.'};dump(r/'docs/round384-archive-reconstruction.json',reconstruction)
folder=w/'final-make';folder.mkdir();controls={'a':r/'.build/round263/final-make/track-a','c':w/'track-c-bin','d':r/'.build/round334/final-make/track-d'};initial=read(w/'compile.json');assert initial['returncode']==0 and not initial['stderr'];assert sha(w/'main.native-optimized.cpp')==read(w/'preflight.json')['source_sha256']['track-c/main.cpp'];assert ''.join((w/'main.native-optimized.cpp').read_text().split())==''.join((s/'track-c/main.cpp').read_text().split())
for t,p in controls.items():shutil.copyfile(p,folder/f'track-{t}');(folder/f'track-{t}').chmod(0o755);assert sha(folder/f'track-{t}')==sha(p)
argv=['make','BUILD_DIR=.build/round384/final-make','all'];q=subprocess.run(argv,cwd=r,capture_output=True,text=True,timeout=180);dump(w/'Make.json',{'argv':argv,'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr,'scope':'Actual rootMake uses cached original A263/currentD334 and exact optimized384 native source before TWO whitespace-only queue linebreaks. Final exact bytes newly compiled under ASAN/TSAN/pinnedGNU/production image; initial optimized main+all headers bound separately, no duplicate optimized compilation.'});assert q.returncode==0 and not q.stderr and 'clang++'not in q.stdout and 'g++'not in q.stdout,(q.stdout,q.stderr)
pub=read(r/'docs/public-sha256.json')['tracks'];runs=[]
def replay(t,data,inputs,expected,threads,label):
 assert{p.name:sha(p)for p in data.iterdir()if p.is_file()}==inputs;dest=w/'combined-native'/t/label;dest.mkdir(parents=True);env=dict(os.environ);env.pop('SPEED_DEMON_THREADS',None)
 if threads is not None:env['SPEED_DEMON_THREADS']=str(threads)
 q=subprocess.run([str(folder/f'track-{t}'),'--data',str(data),'--out',str(dest)],capture_output=True,text=True,env=env,timeout=180);assert q.returncode==0 and not q.stdout and not q.stderr,(t,threads,q.returncode,q.stderr);assert[p.name for p in dest.iterdir()]==[pub[t]['output']];actual=sha(dest/pub[t]['output']);assert actual==expected;assert{p.name:sha(p)for p in data.iterdir()if p.is_file()}==inputs;runs.append({'track':t,'case':label,'requested_threads':threads,'native_default12':threads is None,'binary_sha256':sha(folder/f'track-{t}'),'inputs_sha256':inputs,'sha256':actual})
for t in'acd':
 for threads in[1,6,12,None]:replay(t,r/f'.data/{t}/public-full-seed1',pub[t]['inputs_sha256'],pub[t]['expected_output_sha256'][0],threads,'public-'+('default'if threads is None else str(threads)))
fresh=read(w/'fresh-confirmation/report.json');data=r/fresh['data_folder']
for threads in[1,6,12,None]:replay('c',data,fresh['inputs_sha256'],fresh['expected_sha256'],threads,'full3863-'+('default'if threads is None else str(threads)))
images=dict(prior['images']);images['c']=proofs['build']['image_id'];inputs=[]
for row in prior['inputs']:
 p=row['path'];h=sha(r/p)
 if p.startswith('track-c/'):assert h==pre['source_sha256'][p]
 else:assert h==row['sha256']
 inputs.append({'path':p,'sha256':h,'image_id':images[p[6]],'scope':'384 exact four-word name arena stride; A/D original. Local replay image, not organizer ELF.'})
assert len(inputs)==30;sets={};readmes={};submitted=w/'submitted-source';submitted.mkdir()
for t in'acd':
 names=sorted(str(p.relative_to(r))for p in(r/f'track-{t}').iterdir()if p.is_file()and p.name!='PERF.md');assert names==prior['complete_file_sets_excluding_PERF'][t];sets[t]=names;readmes[t]=sha(r/f'track-{t}/README.md')
 for p in names:dest=submitted/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(r/p,dest)
shutil.copy2(r/'Makefile',submitted/'Makefile');assert sha(r/'Makefile')==prior['Makefile_sha256'];scope='C384 exact FOUR-word arena/key offsets chosen only at actual country words==4, generic exact all others; original representation/queue/CSV/hash/native/full1000003+sample130363/default12 retained. New actual-header model native ASAN/TSAN/GNU, exact current main strict/race, independent country seam fixtures and saved adversarial/untrained/full refs, one exact PGO image and true defaults PASS. Native screen/confirmation are hypotheses only. One real all-track board trial required. Retain C ONLY if supported totalK>23.033578/68.118071, otherwise restore all3 C main/names/README and originalCimage and make one cooled confirmation. No #1/holdout/judging/eligibility/prize guarantee.'
proof={'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'official_score':False,'actual_board_confirmation_pending':True,'source_parent':head,'inputs':inputs,'images':images,'Makefile_sha256':sha(r/'Makefile'),'complete_file_sets_excluding_PERF':sets,'README_sha256':readmes,'native_public_default_runs':runs,'native_strict_proof':'docs/round384-c-native-proof.json','linux_proofs':{m:f'docs/round384-c-{m}-proof.json'for m in proofs},'scope':scope};dump(r/'docs/round384-candidate-source-match.json',proof)
(a/'README.md').write_text('# C384: exact four-word specialization, actual trial pending\n\n'+scope+'\n\nAll final source context is reconstructible from parent plus3 patches/frozen PERF. Initial optimized native main differs by exactly two whitespace-only linebreaks, disclosed in final-source.json; exact final main compiled and executed under native sanitizers/race, GNU strict and production image. Native384 inventory first lacked per-run expected-hash extraction; successful model/main compiles and model were reused, never repeated.\n')
docs=['docs/round384-c-native-proof.json','docs/round384-c-native-asan-matrix.json','docs/round384-c-native-tsan-matrix.json','docs/round384-c-saved-untrained-confirmation.json','docs/round384-archive-reconstruction.json',*[f'docs/round384-c-{m}-proof.json'for m in proofs]];dump(r/'docs/round384-proof-archive.json',{'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'official_score':False,'patches':patches,'reconstruction':reconstruction,'executed_drivers':{str(p.relative_to(r)):sha(p)for p in a.iterdir()if p.is_file()},'reports':{p:sha(r/p)for p in docs},'scope':scope})
for name in['track-c/PERF.md','docs/RESULTS.md','docs/SUBMISSION.md']:
 p=r/name;p.write_text(p.read_text()+'\n\n'+scope+' Native4full .982206/1.008344/.951742/.979952; saved independent untrained3863 .958487/10wins. Exact docs/round384-proof-archive.json and round384-candidate-source-match.json.\n')
p=r/'docs/STATE.md';state=p.read_text();i=state.index('# Current: original377');p.write_text('# C384 all local proof passed; real trial next\n\n'+scope+' Root now has ONLY C384 main/names/README changed; candidate30/Make/README/fullsets/submitted binding docs/round384-candidate-source-match.json. Original377 whole C rollback saved .build/round384/original-retained and immutable originalC263image. Commit/push/ordinary all-track watcher next; do not start another candidate before real decision/restoration. No official gain yet.\n\n'+state[i:]);dump(w/'ACTIVE.json',{'status':'all_local_proof_passed_real_pending','scope':scope});print('INTEGRATED384 after all local proof; source30/Make/native16/reconstructionPASS; one real trial next',flush=True)
