from pathlib import Path
import datetime,hashlib,json,os,re,shutil,subprocess,tempfile
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round362';s=w/'source'
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
pre=read(w/'frozen.json');prior=read(r/'docs/round358-final-source-match.json');proofs={m:read(w/f'proof/{m}/report.json')for m in ['fresh','gcc','build','image','defaults']};assert all(x['passed']for x in proofs.values());head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip();assert head==pre['source_parent']==prior['source_commit'];assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,11,2,14,tzinfo=datetime.timezone.utc);assert not(r/'docs/round362-candidate-source-match.json').exists();shape=read(w/'emitted/call-shape.json');assert shape['passed']
for p,h in pre['source_sha256'].items():assert sha(s/p)==h,p
for p,h in pre['root_selected_bindings'].items():assert sha(r/p)==h,p
for p,h in pre['unchanged_C_cpp_sha256'].items():assert sha(s/p)==sha(r/p)==h,p
assert re.sub(r'\s+','',(s/'track-c/main.cpp').read_text())==re.sub(r'\s+','',(r/'track-c/main.cpp').read_text())
for name in ['Dockerfile','main.cpp','README.md']:
 p='track-c/'+name;assert(r/p).read_bytes()==(w/'original-retained'/p).read_bytes();shutil.copyfile(s/p,r/p)
dump(w/'integration-partial.json',{'phase':'C_Docker_GOTflag_main2linebreak_README_integrated','source_parent':head,'algorithm_tokens_unchanged':True,'A178_D334_unchanged':True})
archive=r/'tools/round362-proof';archive.mkdir()
for name in ['prepare.py','proof.py','chain.py','csv_model.hpp','extract.py']:shutil.copy2(w/name,archive/name)
for t in 'acd':shutil.copy2(s/f'track-{t}/PERF.md',archive/f'base-{t}-PERF.md')
patches=[]
for name in ['Dockerfile','main.cpp','README.md']:
 dest=r/f'docs/prototype-patches/round362-c-direct-GOTs-{name}.patch';shutil.copy2(w/(name+'.patch'),dest);patches.append({'path':str(dest.relative_to(r)),'sha256':sha(dest)})
shutil.copy2(w/'frozen.json',r/'docs/round362-preflight.json');(archive/'README.md').write_text('# C362 exact compiler trial\n\nExplicit fno-plt at end of both original native-ISA GCC full1000003/sample130363 PGO passes; two existing queue statement linebreaks only, token equality checked. Every CSV/name/table/queue/region/money/worker algorithm is original C175; no rejected349 parser return change. New failfast strict GCC237 references/25 normalerrors plus exact raw/decoded byte/guard/numeric402810/offsetname models; one offlinePGO image651 references/50 errors;77 true noargument/nooverride defaults/9 errors. Previously generated independent234/352/356 data/references are reused byhash only; no newgenerator/oracle. Source-specific new237+25 strict/main,651+50 image,77+9 defaults passed, with exact actualproduction callshape report. Original race/header protocol proof remains sourceidentity bound, no newTSAN claimed.\n\nLocal compiler/image identities and emulated correctness are not organizer ELF/timing or score gains. Real totalK must exceed23.033578, else fullmain/Docker/README/image rollback. Reconstruction uses recordedparent plus three disclosedpatches and separately frozenexcludedPERFs. Only executable entersfinalimage, no PGOdata/traininginputs/publicseed1.\n')
folder=w/'final-make';folder.mkdir();controls={'a':r/'.build/round263/final-make/track-a','c':r/'.build/round352/final-make/track-c','d':r/'.build/round334/final-make/track-d'};expected={'a':'75db96e1b101aa09555e5576b201ef5c1a365b52b51339cce5763182e4d09b27','c':'a24ad08000d4620ca4dd110f07cc7849be5a6aa481c9bca51d7f7750f3d7682b','d':'cf0ab08ff09b091ad9954cd365e92a1b0d014c5c31f5ecb2a74f15453761c404'}
oldnative=read(r/'.build/round352/frozen.json');assert sha(r/'Makefile')==oldnative['Makefile_sha256']
for path,h in pre['source_sha256'].items():
 if path.startswith('track-c/')and Path(path).suffix in ['.cpp','.hpp']:assert h==oldnative['source_sha256'][path]
for t,p in controls.items():assert sha(p)==expected[t];shutil.copyfile(p,folder/f'track-{t}');(folder/f'track-{t}').chmod(0o755)
assert sha(r/'Makefile')==pre['Makefile_sha256'];cmd=['make','BUILD_DIR=.build/round362/final-make','all'];q=subprocess.run(cmd,cwd=r,capture_output=True,text=True,timeout=180);dump(w/'Make.json',{'command':cmd,'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr,'scope':'Actual rootMake uses source-bound cachedA263/C352tokenidenticalCPP/currentD334 binaries; no native compiler is repeated. C362 differs only in Dockerflags/README from original352 formattedCPP and nativeMakeflags unchanged. New GNU targetflags actually compiled/proved separately.'});assert q.returncode==0 and not q.stderr and q.stdout.count('clang++')==0,(q.stdout,q.stderr)
pub=read(r/'docs/public-sha256.json')['tracks'];runs=[]
def replay(t,data,inputs,expected,threads,label):
 assert{p.name:sha(p)for p in data.iterdir()if p.is_file()}==inputs;dest=w/'combined-native'/t/label;dest.mkdir(parents=True);env=dict(os.environ);env.pop('SPEED_DEMON_THREADS',None)
 if threads is not None:env['SPEED_DEMON_THREADS']=str(threads)
 q=subprocess.run([str(folder/f'track-{t}'),'--data',str(data),'--out',str(dest)],capture_output=True,text=True,env=env,timeout=180);assert q.returncode==0 and not q.stdout and not q.stderr,(t,threads,q.returncode,q.stderr);output=pub[t]['output'];assert[p.name for p in dest.iterdir()]==[output];actual=sha(dest/output);assert actual==expected;assert{p.name:sha(p)for p in data.iterdir()if p.is_file()}==inputs;runs.append({'track':t,'case':label,'requested_threads':threads,'configured_native_default':12 if threads is None else None,'binary_sha256':sha(folder/f'track-{t}'),'inputs_sha256':inputs,'sha256':actual,'scope':'Actual362composite native correctness only; nativeMakeflagsoriginal, targetloopflags onlyDocker/GCC/image.'})
for t in 'acd':
 for threads in [1,6,12,None]:replay(t,r/f'.data/{t}/public-full-seed1',pub[t]['inputs_sha256'],pub[t]['expected_output_sha256'][0],threads,'public-'+('default'if threads is None else str(threads)))
fresh=read(r/'docs/round356-c-asan-fresh-full.json');row=next(x for x in fresh['checks']if x['case']=='full-seed3623');expected_hash=row['reference_sha256'];data=r/'.data/c/full-seed3623';hashes={p.name:sha(p)for p in data.iterdir()if p.is_file()}
for threads in [1,6,12,None]:replay('c',data,hashes,expected_hash,threads,'full3623-'+('default'if threads is None else str(threads)))
inputs=[]
for old in prior['inputs']:
 path=old['path'];assert sha(r/path)==sha(s/path),path;row=dict(old)
 if path.startswith('track-c/'):row={'path':path,'sha256':sha(r/path),'image_id':proofs['build']['image_id'],'scope':'362 originalC175 algorithmtokens/main2linebreaks, directGOTcall compiler/PGO/image/true-defaultproof. Localidentity, not organizerELF.'}
 else:assert sha(r/path)==old['sha256']
 inputs.append(row)
assert len(inputs)==30;sets={};readmes={};submitted=w/'submitted-source';submitted.mkdir()
for t in 'acd':
 files=sorted(str(p.relative_to(r))for p in(r/f'track-{t}').iterdir()if p.is_file()and p.name!='PERF.md');assert files==prior['complete_file_sets_excluding_PERF'][t];sets[t]=files;readmes[t]=sha(r/f'track-{t}/README.md')
 for path in files:
  dest=submitted/path;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(r/path,dest)
shutil.copyfile(r/'Makefile',submitted/'Makefile');images=dict(prior['images'],c=proofs['build']['image_id'])
with tempfile.TemporaryDirectory(prefix='round362-archive-')as tmp:
 base=Path(tmp)
 for p,h in pre['source_sha256'].items():
  dest=base/p;dest.parent.mkdir(parents=True,exist_ok=True)
  if dest.name=='PERF.md':shutil.copy2(archive/('base-'+p[6]+'-PERF.md'),dest)
  else:dest.write_bytes(subprocess.check_output(['git','show',head+':'+p],cwd=r))
 for row in patches:q=subprocess.run(['git','apply',str(r/row['path'])],cwd=base,capture_output=True,text=True);assert q.returncode==0,q.stderr
 for p,h in pre['source_sha256'].items():assert sha(base/p)==h,p
recon={'passed':True,'source_parent':head,'all_frozen_files_match':True,'file_count':len(pre['source_sha256']),'scope':'Parent+3disclosedCpatches and exactexcludedPERF snapshots reconstruct ALL frozencontextfiles.'};dump(r/'docs/round362-archive-reconstruction.json',recon)
pa={'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'official_score':False,'scope':pre['scope'],'preflight_sha256':sha(r/'docs/round362-preflight.json'),'patches':patches,'C_main_token_equal':True,'unchanged_C_cpp_sha256':pre['unchanged_C_cpp_sha256'],'proof_reports':{m:{'path':f'docs/round362-c-{m}-proof.json','sha256':sha(r/f'docs/round362-c-{m}-proof.json')}for m in proofs},'executed_proof_drivers':{str(p.relative_to(r)):sha(p)for p in archive.iterdir()if p.is_file()},'image_id':proofs['build']['image_id'],'elf_sha256':proofs['build']['elf_sha256'],'archive_reconstruction':recon,'race_provenance':'Original C175 exactqueue/nameheader/sourcealgorithm tokens with prior nativeTSANsource-boundproof; no newconcurrency protocol or newTSAN claimed. NewGCCflagsstrict/models/image/default are freshlyexecuted. No rejected349interface or351header proof substitution.'};dump(r/'docs/round362-proof-archive.json',pa)
proof={'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'official_score':False,'actual_board_confirmation_pending':True,'source_parent':head,'inputs':inputs,'Makefile_sha256':sha(r/'Makefile'),'images':images,'complete_file_sets_excluding_PERF':sets,'README_sha256':readmes,'native_public_default_runs':runs,'c_image':{'id':proofs['build']['image_id'],'elf_sha256':proofs['build']['elf_sha256'],'bytes':proofs['build']['image_bytes'],'scope':'Localreplayidentity, not organizerELF.'},'proof_archive':'docs/round362-proof-archive.json','scope':'362C directGOTcall GCCtrial, originalC175algorithmtokens/main2linebreaks; exact30/root/frozen/submitted/Make/fullsets/README/localimages. FreshstrictGCC237+25/models, oneofflineallowedPGOimage651+50, trueENTRYPOINT/noarg/nooverride77+9, actualcachedrootMake+16composite nativepublic/fresh/defaultcallsPASS. A178/D334exactoriginalcontrols. ActualrealCtotalK>23.033578/68.118071 required forretention; elsefullCrollback.'};dump(r/'docs/round362-candidate-source-match.json',proof)
note='Candidate362 locally validated for ONE real C compilerflag trial: -fno-plt in BOTH unchanged originalstatic -O3 -march=native full1000003/sample130363 PGO passes. Two original queue statement linebreaks/tokenidentity and disclosedREADME only. No parser/queue/name/country/money/default12 algorithm change; A178/D334 exact. Prior independent234/352/356 data/referencebytes reused byhash without generator/oracle repetition; new pinnedGNU failfast raw/decoded/guard/numeric402810/name models+237valid/25errors, ONEofflinePGOimage651+50,77true noarg/nooverride defaults+9PASS. Original native race/header proof retained only by exact CPP/token identity, no newTSAN claimed. ActualrootMake uses exact-source cachedA263/C352formattedCPP/currentD334 controls with16 public/fresh3623/default outputsPASS; no repeatedclang. Actual production ownIFUNC/GOT callshape inspected and image/source bound, not a timing/frequency or organizerELF claim. Localimage'+proofs['build']['image_id']+'/ELF'+proofs['build']['elf_sha256']+' not organizeridentities. Retain ONLY real CtotalK>23.033578/68.118071; else completeDocker/main2linebreak/README/image263rollback. Source30/Make/README/fullsets/localimages in round362-candidate-source-match.json. PRIVATE/MIT; publication onlyapproved15:00–16:00UTC, runtime+Gitfreeze15:00/risky14:00. No newscoregain.'
for name in ['track-c/PERF.md','docs/RESULTS.md','docs/SUBMISSION.md']:
 p=r/name;p.write_text(p.read_text()+'\n\n'+note+'\n')
p=r/'docs/STATE.md';p.write_text('# C362 locally validated; ONE real trial pending\n\n'+note+'\n\nRootstillHEAD344 '+head+' pendingprivatecandidatecommit; source362 integratedlocally, snapshots/rollback/drivers/proof allcomplete. No newcandidate untilactualdecision. Session48291terminalallmodesPASS. Nativeintegration undercurrentexclusive lane completesonce; no duplicates.\n\n'+p.read_text());dump(w/'integration-partial.json',{'phase':'complete_local_candidate_proof','passed':True,'actual_board_confirmation_pending':True});print('PASS362 localcandidate/all30/Make/native16/exactimage/default; realtrialpending',flush=True)
