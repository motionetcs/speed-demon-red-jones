from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess,tempfile
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round395';s=w/'source';read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();digest=lambda b:hashlib.sha256(b).hexdigest()
def dump(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
m=read(w/'frozen.json');plan=read(w/'proof-plan.json');old=read(r/'docs/round392-final-source-match.json');parent=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip();assert parent==old['source_commit']==m['source_parent'];assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,11,2,14,15,tzinfo=datetime.timezone.utc)
native=read(w/'native-proof/report.json');linux={x:read(w/'linux-proof'/x/'report.json')for x in['gcc','build','image','defaults']};assert native['passed']and all(x['passed']for x in linux.values());assert all(sha(w/p)==h for p,h in m['source_sha256'].items());assert sha(s/'Makefile')==old['Makefile_sha256']==plan['candidate_Makefile_sha256'];assert not(r/'docs/round395-candidate-source-match.json').exists();assert all(sha(r/x['path'])==x['sha256']for x in old['inputs'])
assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=r,text=True).strip()
changed=['main.cpp','load_cursors.hpp','edge_store.hpp','README.md'];rollback=w/'rollback-original';assert not rollback.exists();rollback.mkdir();shutil.copytree(r/'track-d',rollback/'track-d');shutil.copyfile(r/'Makefile',rollback/'Makefile')
for name in changed:
 p=r/'track-d'/name;assert p.read_bytes()==(r/'.build/round392/submitted-source/track-d'/name).read_bytes();p.write_bytes((s/'track-d'/name).read_bytes())
for row in old['inputs']:
 p=row['path'];assert sha(r/p)==(sha(s/p)if p.startswith('track-d/')else row['sha256']),p
dump(w/'integration-partial.json',{'phase':'candidate_integrated_local_only','source_parent':parent,'changed_runtime_and_readme':['track-d/'+x for x in changed],'source_original_snapshot':'.build/round392/submitted-source','actual_board_confirmation_pending':True})
a=r/'tools/round395-proof';a.mkdir()
for name in['prepare.py','screen.py','confirm.py','prepare_proof.py','native_proof.py','loader_hints_model.cpp','linux_proof.py','integrate.py','frozen.json','proof-plan.json','proof-bank.json']:
 shutil.copy2(w/name,a/name)
shutil.copy2(s/'track-d/PERF.md',a/'base-d-PERF.md')
patches=[]
for p in sorted(w.glob('*.patch')):
 dest=r/('docs/prototype-patches/round395-d-loader-read-hints-'+p.name);shutil.copy2(p,dest);patches.append({'path':str(dest.relative_to(r)),'sha256':sha(dest)})
frozen={p[len('source/'):]:h for p,h in m['source_sha256'].items()}
with tempfile.TemporaryDirectory(prefix='round395-reconstruct-')as tmp:
 base=Path(tmp)
 for p in frozen:
  dest=base/p;dest.parent.mkdir(parents=True,exist_ok=True)
  if dest.name=='PERF.md':shutil.copy2(a/'base-d-PERF.md',dest)
  else:dest.write_bytes(subprocess.check_output(['git','show',parent+':'+p],cwd=r))
 for row in patches:
  q=subprocess.run(['git','apply',str(r/row['path'])],cwd=base,capture_output=True,text=True);assert q.returncode==0,q.stderr
 assert all(sha(base/p)==h==sha(s/p)for p,h in frozen.items())
(a/'README.md').write_text('''# D395 exact proof archive

Only existing graph-loader prefetch operands change from write/low-locality to read/high-locality. Every address, actual atomic operation/store and graph/search/synchronization body is preserved; inverse substitutions recover all three original compiled files. The exact changed code is freshly executed under native failfast ASAN/UBSAN, TSAN, pinned GCC strict checks, one original allowed-PGO image and true defaults. The joined-cursor model invokes both changed write-prefetch dispatches before unique concurrent claims; added compact/wide edge hint/set/get cases cover empty and partial batches. Unchanged map/queue/allocator bodies retain exact-source primitive provenance, not a new protocol theorem.

Saved independent Floyd, boundary, high-degree, full-width, every-budget, sample, full-public and untrained fixture/reference bytes are reused only by content hashes. No generation/oracle repeats or cached runtime answers. Compiler/model/replay completion markers prevent repeating successful work. Whole production image builds once with original pinned native GCC, byte-identical official generator1000003/full then130363/sample/default12; only executable enters runtime.

The prior394 ARM-only high-locality write hint gained about20% locally, but a tiny RaptorLake GCC probe showed identical prefetchw instructions for its two write-locality operands. It was stopped before broad production proof or board.395 actually changes the target instruction hypothesis to prefetcht0;394's gain is not transferred.395's native1–4%/independent3473~2% changes are hypotheses, not Intel timing, charged memory, organizer ELF or causal gains. One real all-track score is required before retention.
''')
for name,src in [('docs/round395-preflight.json',w/'frozen.json'),('docs/round395-proof-plan.json',w/'proof-plan.json'),('docs/round395-d-read-hints-native-screen.json',w/'screen/report.json'),('docs/round395-d-untrained3473-confirmation.json',w/'untrained-confirmation/report.json')]:shutil.copy2(src,r/name)
proofarchive={'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'official_score':False,'source_parent':parent,'source_sha256':m['source_sha256'],'candidate_Makefile_sha256':plan['candidate_Makefile_sha256'],'patches':patches,'archive_reconstruction_passed':True,'reconstructed_file_count':len(frozen),'model_sha256':plan['model_sha256'],'native_report_sha256':sha(w/'native-proof/report.json'),'linux_report_sha256':{x:sha(w/'linux-proof'/x/'report.json')for x in linux},'executed_drivers':{str(p.relative_to(r)):sha(p)for p in a.iterdir()if p.is_file()},'scope':'Exact changed hint source; all current native strict/race/model/main and GNU/image/default proofs complete. No old different-source pass substitution. No target gain until real board.'};dump(r/'docs/round395-proof-archive.json',proofarchive)
# Exact original Make flags match the one optimized isolated compile; reuse it.
screen=read(w/'screen/report.json');cmd=screen['compile']['command'];assert cmd[:9]==['clang++','-std=c++20','-O3','-DNDEBUG','-Wall','-Wextra','-Wpedantic','-pthread',str(s/'track-d/main.cpp')]
assert sha(w/'track-d-bin')==screen['binary_sha256']['candidate']
folder=w/'final-make';folder.mkdir();sources={'a':r/'.build/round263/final-make/track-a','c':r/'.build/round263/final-make/track-c','d':w/'track-d-bin'}
for t,p in sources.items():dest=folder/('track-'+t);shutil.copyfile(p,dest);dest.chmod(0o755)
makecmd=['make','BUILD_DIR=.build/round395/final-make','all'];q=subprocess.run(makecmd,cwd=r,capture_output=True,text=True,timeout=180);dump(w/'Make.json',{'command':makecmd,'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr,'scope':'Actual unchanged root Make uses source-exact original A263/C263 and once-compiled current395 D native control at the exact same flags. No optimized compiler or model is repeated.'});assert q.returncode==0 and not q.stderr and 'clang++'not in q.stdout and 'g++'not in q.stdout,(q.stdout,q.stderr)
pub=read(r/'docs/public-sha256.json')['tracks'];runs=[]
for t in'acd':
 data=r/'.data'/t/'public-full-seed1';assert {p.name:sha(p)for p in data.iterdir()if p.is_file()}==pub[t]['inputs_sha256']
 for threads in[1,6,12,None]:
  dest=w/'native-public'/t/('default'if threads is None else str(threads));dest.mkdir(parents=True);env=dict(os.environ);env.pop('SPEED_DEMON_THREADS',None)
  if threads is not None:env['SPEED_DEMON_THREADS']=str(threads)
  q=subprocess.run([str(folder/('track-'+t)),'--data',str(data),'--out',str(dest)],capture_output=True,text=True,env=env,timeout=180);assert q.returncode==0 and not q.stdout and not q.stderr,(t,threads,q.returncode,q.stderr);assert [p.name for p in dest.iterdir()]==[pub[t]['output']];h=sha(dest/pub[t]['output']);assert h in pub[t]['expected_output_sha256'];runs.append({'track':t,'threads':threads,'native_default12':threads is None,'binary_sha256':sha(folder/('track-'+t)),'inputs_sha256':pub[t]['inputs_sha256'],'sha256':h})
 assert {p.name:sha(p)for p in data.iterdir()if p.is_file()}==pub[t]['inputs_sha256']
images=dict(old['images'],d=linux['build']['image_id']);inputs=[]
for row in old['inputs']:
 p=row['path'];h=sha(r/p)
 if p.startswith('track-d/'):assert h==sha(s/p)
 else:assert h==row['sha256']
 inputs.append({'path':p,'sha256':h,'image_id':images[p[6]],'scope':'Fresh exact395 current code/local replay image for D; source-exact retained A178/C175 for unchanged components.'})
assert len(inputs)==30;sets={};readmes={};submitted=w/'submitted-source';submitted.mkdir()
for t,names in old['complete_file_sets_excluding_PERF'].items():
 assert sorted(str(p.relative_to(r))for p in(r/('track-'+t)).iterdir()if p.is_file()and p.name!='PERF.md')==names;sets[t]=names;readmes[t]=sha(r/('track-'+t+'/README.md'))
 for p in names:dest=submitted/p;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(r/p,dest)
shutil.copyfile(r/'Makefile',submitted/'Makefile');assert sha(r/'Makefile')==old['Makefile_sha256'];proof={'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'official_score':False,'actual_board_confirmation_pending':True,'source_parent':parent,'inputs':inputs,'Makefile_sha256':old['Makefile_sha256'],'images':images,'complete_file_sets_excluding_PERF':sets,'README_sha256':readmes,'native_public_default_runs':runs,'d_image':linux['build'],'proof_archive':'docs/round395-proof-archive.json','scope':'Only D existing loader-prefetch operands plus documentedREADME changed. Exact30 runtime/build/metadata/Make/fullsets/README/local replay images/current/submitted snapshot match freshly executed strict/race/GNU/image/default/currentMake proofs. Native gains are modest hypotheses. Retain only supported actual D K>20.571091/65.662866, else full four-file original392/2f14 rollback and one cooled confirmation. All five real gates must pass; number one/holdout/judging/eligibility/understanding/prizes not guaranteed.'};dump(r/'docs/round395-candidate-source-match.json',proof)
note=f"Candidate395 local proofPASS for ONE real loader-prefetch trial. Native threefull .988200/.988439/.960926 with10/11/11wins and saved independent untrained3473 .979529/13wins are modest hypotheses only. Inverse substitutions recover all three original compiled files; only advisory rw/locality operands change, all actual addresses/atomics/stores/synchronization/graph/search/full-width behavior exact. Fresh current-header native ASAN/TSAN model and main461+48/451+48, pinnedGNU model/main{len(linux['gcc']['runs'])}+{len(linux['gcc']['expected_failures'])}, ONE original native allowedPGO image{len(linux['image']['runs'])}+{len(linux['image']['expected_failures'])}, true default{len(linux['defaults']['runs'])}, cached actual rootMake/alltrack12/source30/Make/README/fullsets/images PASS. Image{linux['build']['image_id']}/ELF{linux['build']['elf_sha256']} are local replay identities only. No generator/oracle/compile/training duplicate. Actual D K must exceed20.571091/65.662866 to retain, else full main/load_cursors/edge_store/README/original2f14 rollback and one cooled real confirmation. No target gain yet. PRIVATE/MIT; no publication before approved15:00–16:00UTC window; runtime/commits/pushes stop15:00, risky starts14:00."
for name in['track-d/PERF.md','docs/RESULTS.md','docs/SUBMISSION.md']:
 p=r/name;p.write_text(p.read_text()+'\n\n'+note+'\n')
p=r/'docs/STATE.md';p.write_text('# D395 fully locally proved; one real trial next\n\n'+note+'\n\nHEAD remains original392; selected root now verified395 provisional. All native/GNU/build/image/default jobs terminal before integration. Original rollback .build/round395/rollback-original/track-d and .build/round392/submitted-source. Candidate snapshot .build/round395/submitted-source, exact docs/round395-candidate-source-match.json. Archive original executed privatepush/fetch/finalize drivers without changing them; reports can remain postcommit local until one final evidencehead. No new candidate before real result/decision/restoration.\n\n'+p.read_text());dump(w/'integration-partial.json',{'phase':'complete','candidate_proof':'docs/round395-candidate-source-match.json'});dump(w/'ACTIVE.json',{'status':'local_proof_passed_candidate_integrated_private_push_pending','selected_in_root':True,'actual_board_pending':True,'source_parent':parent,'no_active_job':True});print('PASS395 integrated exact source30/localimages/currentMake12; ONE real trial required',flush=True)
