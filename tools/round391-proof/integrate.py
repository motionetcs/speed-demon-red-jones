from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess,tempfile
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round391';s=w/'source';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();read=lambda p:json.loads(Path(p).read_text());dump=lambda p,x:Path(p).write_text(json.dumps(x,indent=2)+'\n');pre=read(w/'preflight.json');prior=read(r/'docs/round385-final-source-match.json');head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip();assert head==pre['source_parent']==prior['source_commit']=='108506457565e394919de18e995eb1bb7179ecd3';assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,11,2,14,tzinfo=datetime.timezone.utc);assert not(r/'docs/round391-candidate-source-match.json').exists();proofs={m:read(w/'proof'/m/'report.json')for m in['native','gcc','build','image','defaults']};assert all(x['passed']for x in proofs.values());assert proofs['build']['elf_equals_original'];assert proofs['build']['elf_sha256']==proofs['build']['original_elf_sha256']=='8dd0a2e5698b99e3d470e3b960035403e734dc3dbf3fafab31d0e075b9351fe9'
for p,h in pre['source_sha256'].items():assert sha(s/p)==h
for p,h in pre['root_selected_bindings'].items():assert sha(r/p)==h
for p,h in pre['unchanged_A_cpp_sha256'].items():assert sha(s/p)==sha(r/p)==h
# Require all three compiler/training RUN steps to have actually reused cache, not a duplicate job.
logs=(w/'proof/build/build.stderr').read_text()+(w/'proof/build/build.stdout').read_text();import re
runsteps=re.findall(r'(?m)^(#\d+) \[build \d+/\d+\] RUN (g\+\+[^\n]+|python3 training_generator[^\n]+)',logs);assert len(runsteps)==3 and all(step+' CACHED'in logs for step,_ in runsteps),runsteps
original=w/'original-retained';original.mkdir();shutil.copytree(r/'track-a',original/'track-a');shutil.copy2(r/'Makefile',original/'Makefile')
for name in['Dockerfile','README.md']:shutil.copyfile(s/'track-a'/name,r/'track-a'/name)
a=r/'tools/round391-proof';a.mkdir();shutil.copy2(Path(__file__),w/'integrate.py')
for p in w.iterdir():
 if p.is_file()and(p.suffix=='.py'or p.name in['preflight.json','frozen.json','report.json','proof-attempt1-setup-failure.json']):shutil.copy2(p,a/p.name)
shutil.copy2(s/'track-a/PERF.md',a/'base-a-PERF.md');patches=[]
for name in['Dockerfile','README.md']:
 dest=r/f'docs/prototype-patches/round391-a-runtime8-{name}.patch';shutil.copy2(w/(name+'.patch'),dest);patches.append({'path':str(dest.relative_to(r)),'sha256':sha(dest)})
with tempfile.TemporaryDirectory(prefix='round391-reconstruct-')as tmp:
 base=Path(tmp)
 for p,h in pre['source_sha256'].items():
  dest=base/p;dest.parent.mkdir(parents=True,exist_ok=True)
  if dest.name=='PERF.md':shutil.copy2(a/'base-a-PERF.md',dest)
  else:dest.write_bytes(subprocess.check_output(['git','show',head+':'+p],cwd=r))
 for row in patches:
  q=subprocess.run(['git','apply',str(r/row['path'])],cwd=base,capture_output=True,text=True);assert q.returncode==0,q.stderr
 for p,h in pre['source_sha256'].items():assert sha(base/p)==h
reconstruction={'passed':True,'source_parent':head,'files':len(pre['source_sha256']),'scope':'Exact parent plus2 disclosed final ENV8/README patches and frozen excluded PERF reconstruct every A context file. All C++/headers remain original; only final runtime config changes.'};dump(r/'docs/round391-archive-reconstruction.json',reconstruction)
folder=w/'final-make';folder.mkdir();controls={'a':r/'.build/round263/final-make/track-a','c':r/'.build/round263/final-make/track-c','d':r/'.build/round334/final-make/track-d'}
for t,p in controls.items():shutil.copyfile(p,folder/f'track-{t}');(folder/f'track-{t}').chmod(0o755);assert sha(folder/f'track-{t}')==sha(p)
argv=['make','BUILD_DIR=.build/round391/final-make','all'];q=subprocess.run(argv,cwd=r,capture_output=True,text=True,timeout=180);dump(w/'Make.json',{'argv':argv,'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr,'scope':'Actual rootMake, byte-identical original C++/headers and cached originalA263/C263/currentD334 native binaries, no repeated compiler. Nativefallback12 unchanged; runtime8 explicitly tested, final image ENV8 tested separately.'});assert q.returncode==0 and not q.stderr and 'clang++'not in q.stdout and 'g++'not in q.stdout,(q.stdout,q.stderr)
pub=read(r/'docs/public-sha256.json')['tracks'];runs=[]
def replay(t,data,inputs,expected,threads,label):
 assert{p.name:sha(p)for p in data.iterdir()if p.is_file()}==inputs;dest=w/'combined-native'/t/label;dest.mkdir(parents=True);env=dict(os.environ);env.pop('SPEED_DEMON_THREADS',None)
 if threads is not None:env['SPEED_DEMON_THREADS']=str(threads)
 q=subprocess.run([str(folder/f'track-{t}'),'--data',str(data),'--out',str(dest)],capture_output=True,text=True,env=env,timeout=180);assert q.returncode==0 and not q.stdout and not q.stderr,(t,threads,q.returncode,q.stderr);assert[p.name for p in dest.iterdir()]==[pub[t]['output']];actual=sha(dest/pub[t]['output']);assert actual==expected;assert{p.name:sha(p)for p in data.iterdir()if p.is_file()}==inputs;runs.append({'track':t,'case':label,'requested_threads':threads,'native_cli_fallback12':threads is None,'binary_sha256':sha(folder/f'track-{t}'),'inputs_sha256':inputs,'sha256':actual})
for t in'acd':
 for threads in[1,6,12,None]:replay(t,r/f'.data/{t}/public-full-seed1',pub[t]['inputs_sha256'],pub[t]['expected_output_sha256'][0],threads,'public-'+('native-default12'if threads is None else str(threads)))
replay('a',r/'.data/a/public-full-seed1',pub['a']['inputs_sha256'],pub['a']['expected_output_sha256'][0],8,'public-8')
fresh=next(x for x in proofs['image']['runs']if x['case']=='full-seed3911'and x['threads']==8)
for threads in[8,None]:replay('a',r/fresh['data_folder'],fresh['inputs_sha256'],fresh['expected_sha256'],threads,'full3911-'+('native-default12'if threads is None else str(threads)))
images=dict(prior['images']);images['a']=proofs['build']['image_id'];inputs=[]
for row in prior['inputs']:
 p=row['path'];h=sha(r/p)
 if p.startswith('track-a/'):assert h==pre['source_sha256'][p]
 else:assert h==row['sha256']
 inputs.append({'path':p,'sha256':h,'image_id':images[p[6]],'scope':'391 only final A ENV8/README; all C++/headers/original generic build prefix unchanged. C/D original. Local image identity, not organizer ELF.'})
assert len(inputs)==30;sets={};readmes={};submitted=w/'submitted-source';submitted.mkdir()
for t in'acd':
 names=sorted(str(p.relative_to(r))for p in(r/f'track-{t}').iterdir()if p.is_file()and p.name!='PERF.md');assert names==prior['complete_file_sets_excluding_PERF'][t];sets[t]=names;readmes[t]=sha(r/f'track-{t}/README.md')
 for p in names:dest=submitted/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(r/p,dest)
shutil.copy2(r/'Makefile',submitted/'Makefile');assert sha(r/'Makefile')==prior['Makefile_sha256'];scope='A391 ONLY final-image ENV default8, nativefallback12 and original GENERIC full1000003/sample130363/default12 PGO/C++/headers exact. Native8-vs12 is1.008–1.031 time ratio for1.75–2.61MB less processRSS, a memory/time hypothesis, not chargedM/Intel/K. Fresh cached exact original178 ASAN29+2 andTSAN29+2 at8; pinned cached exactCpp343 GNUstrict29+2 retains disclosed historical mtune scheduling flag ONLY for logic checks, never deployed. Actual candidate Dockerfile offline build reuses ALL3 compiler/training RUN steps from cache; executable8dd0a2e5... EXACTLY original b57, finalconfig differs only ENV8. Actual image38+2,29true default8+2normalerrors+2deferredfullsink failures, actual cached rootMake/native15 PASS. Initial output-open test omitted required summary.txt DIRECTORY; valid empty-input success was correctly rejected by driver assertion, preserved and fixture setup corrected in every mode; all completed valid runs reused. One real all-track trial now required. Retain only supported A totalK>32.070167/75.305061, else restore Docker/README/original image and make one cooled real confirmation. No #1/holdout/judging/eligibility/understanding/prize guarantee.'
proof={'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'official_score':False,'actual_board_confirmation_pending':True,'source_parent':head,'inputs':inputs,'images':images,'Makefile_sha256':sha(r/'Makefile'),'complete_file_sets_excluding_PERF':sets,'README_sha256':readmes,'native_public_default_runs':runs,'proof_reports':{m:f'docs/round391-a-{m}-proof.json'for m in proofs},'production_elf_sha256':proofs['build']['elf_sha256'],'scope':scope};dump(r/'docs/round391-candidate-source-match.json',proof)
(a/'README.md').write_text('# A391: final runtime default8, one actual trial pending\n\n'+scope+'\n\nNo new C++ compiler/model/generator/oracle/PGO work. Strict binaries/source/flags are explicitly bound. All2changed source-context files reconstruct from disclosed patches.\n');dump(r/'docs/round391-proof-archive.json',{'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'official_score':False,'patches':patches,'reconstruction':reconstruction,'executed_drivers':{str(p.relative_to(r)):sha(p)for p in a.iterdir()if p.is_file()},'reports':{f'docs/round391-a-{m}-proof.json':sha(r/f'docs/round391-a-{m}-proof.json')for m in proofs},'scope':scope})
# Correct a known historical prose count without rewriting any executed driver or result.
p=r/'docs/round384-archive-reconstruction.json';oldrec=read(p)
if 'All10' in oldrec.get('scope',''):
 former=oldrec['scope'];oldrec['scope']=former.replace('All10',f"All{oldrec['files']}");oldrec['caption_correction']={'former_scope':former,'reason':'Count prose corrected to actual verified files field and frozen manifest length; no source/hash/test execution changed.'};dump(p,oldrec);pa=read(r/'docs/round384-proof-archive.json');pa['reports'][str(p.relative_to(r))]=sha(p);pa['reconstruction']=oldrec;pa['historical_context_count_correction']=oldrec['caption_correction'];dump(r/'docs/round384-proof-archive.json',pa)
for name in['track-a/PERF.md','docs/RESULTS.md','docs/SUBMISSION.md']:
 p=r/name;p.write_text(p.read_text()+'\n\n'+scope+' Exact docs/round391-proof-archive.json/round391-candidate-source-match.json.\n')
p=r/'docs/STATE.md';state=p.read_text();i=state.index('# Original385 real-confirmed');p.write_text('# A391 all local proof passed; one real default8 trial next\n\n'+scope+' Root now ONLY A Dockerfile/README changed, all CPP/header/Make/othertracks source exact original385. Original snapshot/rollback .build/round391/original-retained, original image b57 retained. Source30/Make/README/fullsets/submitted/localimage proof docs/round391-candidate-source-match.json. Commit/push/normal alltrack watcher next; no new candidate until terminal decision/restoration.\n\n'+state[i:]);dump(w/'ACTIVE.json',{'status':'all_local_proof_passed_real_pending','scope':scope});print('INTEGRATED391 ENV8-only after all proofs; source30/Make/native15/cacheELFsame/reconstructionPASS; one real trial next',flush=True)
