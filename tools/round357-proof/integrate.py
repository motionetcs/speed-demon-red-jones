from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round357';s=w/'source'
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
pre=read(w/'preflight.json');prior=read(r/'docs/round353-final-source-match.json');head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip()
assert head==pre['source_parent']==prior['source_commit']=='781f2ea889c110b470720000729c7eedfadc67af'
assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,11,2,14,tzinfo=datetime.timezone.utc)
assert not(w/'integration-partial.json').exists()
proofs={m:read(w/f'proof/{m}/report.json')for m in ['model','gcc','build','image','defaults']};native=read(w/'native-proof/report.json');assert native['passed'] and all(x['passed']for x in proofs.values())
for p,h in pre['source_sha256'].items():assert sha(s/p)==h,p
for p,h in pre['root_selected_bindings'].items():assert sha(r/p)==h,p
changed=['main.cpp','names.hpp','parallel.hpp']
for p,h in pre['source_sha256'].items():
 if Path(p).name not in changed+['PERF.md']:assert sha(r/p)==h,p
for name in changed:shutil.copyfile(s/('track-c/'+name),r/('track-c/'+name))
dump(w/'integration-partial.json',{'phase':'C_three_files_integrated_only','source_parent':head,'runtime':'C357 atomic batch waits/sticky cancellation/owner uint32 epochs/startup cancellation','selected_for_trial_only':True,'original353_rollback':'.build/round353/submitted-source'})
p=r/'docs/STATE.md';p.write_text('# C357 local integration for one real trial; original353 preserved\n\n357 native ASAN/TSAN and actual GNU15.3 queue/startup models passed. One new allowed-PGO image, GCC231+25, image645+50,77 actual defaults+9 all passed. Current root three C files now357; A178/D334 unchanged. Actual root Make/composite checks running under exclusive lock; no commit/push/real gain yet. Session43506 terminal; do not repeat any completed strict/compiler/model/training/image work. Frozen native references/data are reused by hash only. Prior353 exact source/image snapshot retained for full rollback. A355 rejected native-only (mixed time plus3MB); C354/356 superseded before GNU/image/board. Other authorized chat prepares isolated359, CPU HOLD until explicit release.\n\n'+p.read_text())
folder=w/'final-make';folder.mkdir();controls={'a':r/'.build/round263/final-make/track-a','d':r/'.build/round334/final-make/track-d'};expected={'a':'75db96e1b101aa09555e5576b201ef5c1a365b52b51339cce5763182e4d09b27','d':'cf0ab08ff09b091ad9954cd365e92a1b0d014c5c31f5ecb2a74f15453761c404'}
for t,p in controls.items():assert sha(p)==expected[t];shutil.copyfile(p,folder/f'track-{t}');(folder/f'track-{t}').chmod(0o755)
assert sha(r/'Makefile')==prior['Makefile_sha256'];cmd=['make','BUILD_DIR=.build/round357/final-make','all'];q=subprocess.run(cmd,cwd=r,capture_output=True,text=True,timeout=180);dump(w/'Make.json',{'command':cmd,'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr,'scope':'Actual root Make compiles changed C once; exact source-bound originalA263/currentD334 controls copied. No new A/D compiler/training.'});assert q.returncode==0 and not q.stderr and q.stdout.count('clang++')==1,(q.stdout,q.stderr)
pub=read(r/'docs/public-sha256.json')['tracks'];runs=[]
def replay(t,data,inputs,expected,threads,label):
 assert {p.name:sha(p)for p in data.iterdir()if p.is_file()}==inputs
 dest=w/'combined-native'/t/label;dest.mkdir(parents=True);env=dict(os.environ);env.pop('SPEED_DEMON_THREADS',None)
 if threads is not None:env['SPEED_DEMON_THREADS']=str(threads)
 q=subprocess.run([str(folder/f'track-{t}'),'--data',str(data),'--out',str(dest)],capture_output=True,text=True,env=env,timeout=180)
 assert q.returncode==0 and not q.stdout and not q.stderr,(t,threads,q.returncode,q.stderr)
 output=pub[t]['output'];assert [p.name for p in dest.iterdir()]==[output];actual=sha(dest/output);assert actual==expected
 assert {p.name:sha(p)for p in data.iterdir()if p.is_file()}==inputs
 runs.append({'track':t,'case':label,'requested_threads':threads,'configured_native_default':12 if threads is None else None,'binary_sha256':sha(folder/f'track-{t}'),'inputs_sha256':inputs,'sha256':actual,'scope':'Actual Make/native composite correctness only; no timing/Intel/board gain claim.'})
for t in 'acd':
 for threads in [1,6,12,None]:replay(t,r/f'.data/{t}/public-full-seed1',pub[t]['inputs_sha256'],pub[t]['expected_output_sha256'][0],threads,'public-'+('default'if threads is None else str(threads)))
matrix=read(w/'native-proof/asan/matrix.json');fresh=[x for x in matrix['runs'] if x.get('data_folder')=='.data/c/full-seed3623'];assert fresh
row=fresh[0];data=r/row['data_folder'];inputs=row['inputs_sha256'];expected_hash=row.get('reference_sha256',row.get('expected_output_sha256',row.get('sha256')));assert isinstance(expected_hash,str)
for threads in [1,6,12,None]:replay('c',data,inputs,expected_hash,threads,'full3623-'+('default'if threads is None else str(threads)))
inputs=[]
for old in prior['inputs']:
 path=old['path'];assert sha(r/path)==sha(s/path) if (s/path).exists() else sha(r/path)==old['sha256'],path
 if path.startswith('track-c/'):row={'path':path,'sha256':sha(r/path),'image_id':proofs['build']['image_id'],'scope':'357 exact batch-wait source with fresh native/GNU strict/race/models/image/default proof; local image, not organizer ELF.'}
 else:assert sha(r/path)==old['sha256'];row=dict(old)
 inputs.append(row)
assert len(inputs)==30;sets={};readmes={};submitted=w/'submitted-source';submitted.mkdir()
for t in 'acd':
 files=sorted(str(p.relative_to(r))for p in(r/f'track-{t}').iterdir()if p.is_file()and p.name!='PERF.md');assert files==prior['complete_file_sets_excluding_PERF'][t];sets[t]=files;readmes[t]=sha(r/f'track-{t}/README.md')
 for path in files:
  dest=submitted/path;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(r/path,dest)
shutil.copyfile(r/'Makefile',submitted/'Makefile');images=dict(prior['images'],c=proofs['build']['image_id'])
proof={'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'official_score':False,'actual_board_confirmation_pending':True,'source_parent':head,'inputs':inputs,'Makefile_sha256':sha(r/'Makefile'),'images':images,'complete_file_sets_excluding_PERF':sets,'README_sha256':readmes,'native_public_default_runs':runs,'c_image':{'id':proofs['build']['image_id'],'elf_sha256':proofs['build']['elf_sha256'],'bytes':proofs['build']['image_bytes'],'scope':'Local replay identity, not organizer ELF.'},'proof_archive':'docs/round357-proof-archive.json','scope':'C357 standard atomic waits at batch boundaries; sticky queue cancellation and bounded uint32 owner epochs; callback cancels before thread/vector startup failure joins. Actual root Make one C compile/16 composite calls, exact all30/Make/README/fullsets/localimage. Source-specific native ASAN/TSAN and pinned GNU failfast ASAN/main/queue/startup models, one unchanged allowed-PGO image and actual defaults passed. Real K>23.033578 required; else full three-C-file/originalimage rollback358. A178/D334 unchanged.'}
dump(r/'docs/round357-candidate-source-match.json',proof);dump(w/'integration-partial.json',{'phase':'complete_local_candidate_proof','passed':True,'actual_board_confirmation_pending':True});print('PASS357 actual Make/16native/all30/image identity; ready archive/private real trial',flush=True)
