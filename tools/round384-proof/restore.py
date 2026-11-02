from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round384';restore=r/'.build/round385'
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,j):p.write_text(json.dumps(j,indent=2)+'\n')
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip();proof=read(r/'docs/round384-committed-source-match.json');board=read(r/'docs/board-round384-fixed-words4.json');original=read(r/'docs/round377-final-source-match.json');assert head==proof['source_commit']==board['commit']=='ce9361c5d7e9e74c6165cf202c49c84d670fe103'
assert board['passed']and board['tracks']['c']['K']<23.033578
assert max(datetime.datetime.fromisoformat(board['tracks'][t]['dispatched_at'].replace('Z','+00:00'))for t in'acd')+datetime.timedelta(seconds=300)==datetime.datetime(2026,11,2,10,37,2,tzinfo=datetime.timezone.utc)
assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,11,2,14,tzinfo=datetime.timezone.utc)
assert not restore.exists();restore.mkdir();shutil.copy2(Path(__file__),restore/'restore.py')
for row in proof['inputs']:assert sha(r/row['path'])==row['sha256']
scored=dict(proof);scored.update(actual_board_confirmation_pending=False,actual_board_report='docs/board-round384-fixed-words4.json',actual_records=board['tracks'],actual_all_gates_passed=True,decision='REJECT384: four-word name stride trial has real totalK below retained23.033578/68.118071. Complete main/names/README/image rollback, preserve all proofs and actual result.');dump(r/'docs/round384-scored-source-match.json',scored)
for name in ['main.cpp','names.hpp','README.md']:shutil.copyfile(r/'.build/round377/submitted-source/track-c'/name,r/'track-c'/name)
for row in original['inputs']:assert sha(r/row['path'])==row['sha256'],row['path']
assert sha(r/'Makefile')==original['Makefile_sha256']
for t,h in original['README_sha256'].items():assert sha(r/f'track-{t}/README.md')==h
common=['docker','run','--rm','--pull=never','--platform','linux/amd64','--network=none','--read-only','--memory=8g','--memory-swap=8g','--pids-limit=512','--cap-drop=ALL','--security-opt=no-new-privileges','--user','65534:65534','--tmpfs','/tmp:rw,exec,size=1g'];pub=read(r/'docs/public-sha256.json')['tracks'];fresh=read(r/'docs/round370-c-asan-fresh-full3863.json');row=next(x for x in fresh['checks']if x['case']=='full-seed3863');cases=[('public-full-seed1',r/'.data/c/public-full-seed1',pub['c']['inputs_sha256'],pub['c']['expected_output_sha256'][0]),('full-seed3863',r/'.data/c/full-seed3863',None,row['reference_sha256'])];runs=[]
for label,data,recorded,expected in cases:
 hashes={p.name:sha(p)for p in data.iterdir()if p.is_file()}
 if recorded:assert hashes==recorded
 for threads in [1,6,12,None]:
  dest=restore/'original-image'/label/('default'if threads is None else str(threads));dest.mkdir(parents=True);dest.chmod(0o777);argv=[*common]
  if threads is not None:argv+=['-e','SPEED_DEMON_THREADS='+str(threads)]
  argv+=['-v',str(data)+':/data:ro','-v',str(dest)+':/out:rw',original['images']['c']]
  if threads is not None:argv+=['--data','/data','--out','/out']
  q=subprocess.run(argv,capture_output=True,text=True,timeout=180);assert q.returncode==0 and not q.stdout and not q.stderr,(label,threads,q.returncode,q.stderr);assert[p.name for p in dest.iterdir()]==['aggregates.txt'];actual=sha(dest/'aggregates.txt');assert actual==expected;runs.append({'case':label,'threads':threads,'true_ENTRYPOINT_noarg_nooverride_default':threads is None,'inputs_sha256':hashes,'sha256':actual,'image_id':original['images']['c']});dump(restore/'original-image-partial.json',{'runs':runs})
 assert{p.name:sha(p)for p in data.iterdir()if p.is_file()}==hashes
dump(r/'docs/round385-original-c-image-controls.json',{'passed':True,'official_score':False,'runs':runs,'scope':'8 fresh original C image public/new independent3863 replays including actual default; no compiler/PGO/model/data/oracle repetition.'})
folder=restore/'final-make';folder.mkdir();controls={'a':r/'.build/round263/final-make/track-a','c':r/'.build/round263/final-make/track-c','d':r/'.build/round334/final-make/track-d'}
for t,p in controls.items():shutil.copyfile(p,folder/f'track-{t}');(folder/f'track-{t}').chmod(0o755)
cmd=['make','BUILD_DIR=.build/round385/final-make','all'];q=subprocess.run(cmd,cwd=r,capture_output=True,text=True,timeout=180);assert q.returncode==0 and not q.stderr and 'clang++'not in q.stdout and 'g++'not in q.stdout;dump(restore/'Make.json',{'command':cmd,'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr,'scope':'Actual root Make uses exact original A263/C263/current D334 cached native binaries; no compiler repeated.'});native=[]
for t in 'acd':
 data=r/f'.data/{t}/public-full-seed1';assert{p.name:sha(p)for p in data.iterdir()if p.is_file()}==pub[t]['inputs_sha256']
 for threads in [1,6,12,None]:
  dest=restore/'native-public'/t/('default'if threads is None else str(threads));dest.mkdir(parents=True);env=dict(os.environ);env.pop('SPEED_DEMON_THREADS',None)
  if threads is not None:env['SPEED_DEMON_THREADS']=str(threads)
  q=subprocess.run([str(folder/f'track-{t}'),'--data',str(data),'--out',str(dest)],capture_output=True,text=True,env=env,timeout=180);assert q.returncode==0 and not q.stdout and not q.stderr,(t,threads,q.returncode,q.stderr);assert[p.name for p in dest.iterdir()]==[pub[t]['output']];actual=sha(dest/pub[t]['output']);assert actual in pub[t]['expected_output_sha256'];native.append({'track':t,'threads':threads,'native_default12':threads is None,'binary_sha256':sha(folder/f'track-{t}'),'inputs_sha256':pub[t]['inputs_sha256'],'sha256':actual})
submitted=restore/'submitted-source';submitted.mkdir()
for t,names in original['complete_file_sets_excluding_PERF'].items():
 assert sorted(str(p.relative_to(r))for p in(r/f'track-{t}').iterdir()if p.is_file()and p.name!='PERF.md')==names
 for name in names:d=submitted/name;d.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(r/name,d)
shutil.copyfile(r/'Makefile',submitted/'Makefile');inputs=[]
for row in original['inputs']:assert sha(r/row['path'])==row['sha256']==sha(submitted/row['path']);inputs.append({'path':row['path'],'sha256':row['sha256'],'image_id':original['images'][row['path'][6]],'scope':'Complete original A178/C175/D334 restored after384; local replay image identity.'})
proof={'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'official_score':False,'actual_board_confirmation_pending':True,'source_parent':head,'inputs':inputs,'Makefile_sha256':original['Makefile_sha256'],'images':original['images'],'complete_file_sets_excluding_PERF':original['complete_file_sets_excluding_PERF'],'README_sha256':original['README_sha256'],'native_public_default_runs':native,'original_C_image_controls':'docs/round385-original-c-image-controls.json','scope':'Complete384 main/names/README/image rollback; original passing377 source30/Make/fullsets/README/local images restored. Fresh original image8, cached actual Make/native12 pass. One cooled385 real confirmation required.'};dump(r/'docs/round385-candidate-source-match.json',proof)
x=board['tracks']['c'];note=f"C384/{head}, run{x['run_id']}, all real gatesPASS: T{x['T_s']}/M{x['M_bytes']}/S{x['S']}/K{x['K']}/{x['points']} points. REJECT real totalK below best23.033578/68.118071 despite native time hypothesis; source increased672→684. Full main/names/README/image rollback to A178/C175/D334 original377, all30/Make/README/fullsets/submitted proof docs/round385-candidate-source-match.json. Fresh original image8 public/untrained3863 incl true default and cached actual Make/native12 PASS; no compiler/model/training/reference repeated. C384 native/GNU/image/default/source evidence remains historical; no gain claim. One cooled ordinary385 confirmation, earliest10:37:02UTC after384dispatch10:32:02. PRIVATE/MIT and approved publication window unchanged."
for name in ['track-c/PERF.md','docs/RESULTS.md','docs/SUBMISSION.md']:
 p=r/name;p.write_text(p.read_text()+'\n\n'+note+'\n')
p=r/'docs/STATE.md';p.write_text('# Original385 restored; cooled real confirmation pending\n\n'+note+'\n\nHEADstillrejected384; selected working source original377 restored and snapshotted. No new candidate until real confirmation.\n\n'+p.read_text());dump(restore/'ACTIVE.json',{'status':'original_restored_local_passed','earliest_next_push_utc':'2026-11-02T10:37:02Z','note':note});print('RESTORED385 original all30; image8/native12PASS; cooled real confirmation pending',flush=True)
