from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round357';restore=r/'.build/round358';assert not restore.exists();restore.mkdir()
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip();assert head=='aad6b7855fe3d3fa09bb6aaf7f570e8c82bec9da';pre=read(w/'preflight.json');proof=read(r/'docs/round357-committed-source-match.json');board=read(r/'docs/board-round357-atomic-waits.json');assert board['passed']and board['commit']==head
for row in proof['inputs']:assert sha(r/row['path'])==row['sha256']
assert board['tracks']['c']['K']==18.207246<23.033578
scored=dict(proof);scored.update(observed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),actual_board_confirmation_pending=False,source_commit=head,actual_board_report='docs/board-round357-atomic-waits.json',actual_records=board['tracks'],actual_all_gates_passed=True,decision='REJECT complete357Cmain/names/parallel/batchwait/epoch/cancel/image: realK18.207246<best23.033578; A/Dunchangedlowerrepeats variation, no causalphase/Intelbinary claim.');dump(r/'docs/round357-scored-source-match.json',scored)
for name in ['main.cpp','names.hpp','parallel.hpp']:shutil.copyfile(r/'.build/round353/submitted-source/track-c'/name,r/'track-c'/name)
original=read(r/'docs/round353-final-source-match.json')
for row in original['inputs']:assert sha(r/row['path'])==row['sha256'],row['path']
assert sha(r/'Makefile')==original['Makefile_sha256']
for t,h in original['README_sha256'].items():assert sha(r/f'track-{t}/README.md')==h
snapshot=restore/'source';snapshot.mkdir()
for t in 'acd':shutil.copytree(r/f'track-{t}',snapshot/f'track-{t}')
shutil.copy2(r/'Makefile',snapshot/'Makefile');dump(restore/'restore-partial.json',{'phase':'completeoriginalCrestored','root_source_matches_passing353_all30':True,'A178_C175_D334':True,'image':original['images']['c']})
common=['docker','run','--rm','--pull=never','--platform','linux/amd64','--network=none','--read-only','--memory=8g','--memory-swap=8g','--pids-limit=512','--cap-drop=ALL','--security-opt=no-new-privileges','--user','65534:65534','--tmpfs','/tmp:rw,exec,size=1g'];pub=read(r/'docs/public-sha256.json')['tracks'];fresh=read(w/'native-proof/asan/matrix.json');ref=next(x for x in fresh['runs']if x['case']=='full-seed3623');cases=[('public-full-seed1',r/'.data/c/public-full-seed1',pub['c']['inputs_sha256'],pub['c']['expected_output_sha256'][0]),('full-seed3623',r/'.data/c/full-seed3623',None,ref['expected_sha256'])];runs=[]
for label,data,recorded,expected in cases:
 hashes={p.name:sha(p)for p in data.iterdir()if p.is_file()}
 if recorded:assert hashes==recorded
 for threads in [1,6,12,None]:
  dest=restore/'original-image'/label/('default'if threads is None else str(threads));dest.mkdir(parents=True);dest.chmod(0o777)
  if threads is None:argv=[*common,'-v',str(data)+':/data:ro','-v',str(dest)+':/out:rw',original['images']['c']]
  else:argv=[*common,'-e','SPEED_DEMON_THREADS='+str(threads),'-v',str(data)+':/data:ro','-v',str(dest)+':/out:rw',original['images']['c'],'--data','/data','--out','/out']
  q=subprocess.run(argv,capture_output=True,text=True,timeout=180);assert q.returncode==0 and not q.stdout and not q.stderr,(label,threads,q.returncode,q.stderr);assert[p.name for p in dest.iterdir()]==['aggregates.txt'];actual=sha(dest/'aggregates.txt');assert actual==expected;runs.append({'case':label,'threads':threads,'true_ENTRYPOINT_noarg_nooverride_default':threads is None,'inputs_sha256':hashes,'sha256':actual,'image_id':original['images']['c'],'scope':'Freshrollback control using immutableoriginalC263image, no build/training/oldproofrelabel.'});dump(restore/'original-image-partial.json',{'runs':runs})
 assert{p.name:sha(p)for p in data.iterdir()if p.is_file()}==hashes
dump(r/'docs/round358-original-c-image-controls.json',{'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'official_score':False,'runs':runs,'scope':'8fresh originalCimage public/newuntrained3623 at1/6/12/true default12; no newcompiler/PGO or rejected352image substitution.'})
folder=restore/'final-make';folder.mkdir();controls={'a':r/'.build/round263/final-make/track-a','c':r/'.build/round263/final-make/track-c','d':r/'.build/round334/final-make/track-d'};expected={'a':'75db96e1b101aa09555e5576b201ef5c1a365b52b51339cce5763182e4d09b27','c':'db8972d55c2a7b58a42f83dc42aab8df84fe9bdf4761dfd121368a6e0278037a','d':'cf0ab08ff09b091ad9954cd365e92a1b0d014c5c31f5ecb2a74f15453761c404'}
for t,p in controls.items():assert sha(p)==expected[t];shutil.copyfile(p,folder/f'track-{t}');(folder/f'track-{t}').chmod(0o755)
cmd=['make','BUILD_DIR=.build/round358/final-make','all'];q=subprocess.run(cmd,cwd=r,capture_output=True,text=True,timeout=180);assert q.returncode==0 and not q.stderr and 'clang++'not in q.stdout and 'g++'not in q.stdout;dump(restore/'Make.json',{'command':cmd,'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr,'scope':'ActualrootMakewithbyteverifiedcachedoriginalA/C263,CURRENTD334; no repeatedcompiler.'});native=[]
for t in 'acd':
 data=r/f'.data/{t}/public-full-seed1';assert{p.name:sha(p)for p in data.iterdir()if p.is_file()}==pub[t]['inputs_sha256']
 for threads in [1,6,12,None]:
  dest=restore/'native-public'/t/('default'if threads is None else str(threads));dest.mkdir(parents=True);env=dict(os.environ);env.pop('SPEED_DEMON_THREADS',None)
  if threads is not None:env['SPEED_DEMON_THREADS']=str(threads)
  q=subprocess.run([str(folder/f'track-{t}'),'--data',str(data),'--out',str(dest)],capture_output=True,text=True,env=env,timeout=180);assert q.returncode==0 and not q.stdout and not q.stderr,(t,threads,q.returncode,q.stderr);assert[p.name for p in dest.iterdir()]==[pub[t]['output']];actual=sha(dest/pub[t]['output']);assert actual in pub[t]['expected_output_sha256'];native.append({'track':t,'threads':threads,'native_default12':threads is None,'binary_sha256':sha(folder/f'track-{t}'),'inputs_sha256':pub[t]['inputs_sha256'],'sha256':actual})
inputs=[]
for row in original['inputs']:assert sha(r/row['path'])==row['sha256']==sha(snapshot/row['path']);inputs.append(row)
submitted=restore/'submitted-source';submitted.mkdir()
for t,names in original['complete_file_sets_excluding_PERF'].items():
 assert sorted(str(p.relative_to(r))for p in(r/f'track-{t}').iterdir()if p.is_file()and p.name!='PERF.md')==names
 for name in names:
  dest=submitted/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(r/name,dest)
shutil.copyfile(r/'Makefile',submitted/'Makefile')
new={'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'official_score':False,'actual_board_confirmation_pending':True,'source_parent':head,'inputs':inputs,'Makefile_sha256':original['Makefile_sha256'],'images':original['images'],'complete_file_sets_excluding_PERF':original['complete_file_sets_excluding_PERF'],'README_sha256':original['README_sha256'],'native_public_default_runs':native,'original_C_image_controls':'docs/round358-original-c-image-controls.json','scope':'Complete357C main/names/parallel atomic-wait/epoch/sticky-cancel/startup-callback/image rollback. All30 original passing353 runtime/build/metadata/Make/fullsets/README/images match; fresh8originalCimage public/untrained3623 incl true default, actualcachedMake+12composite nativepublic/defaultPASS. No new compiler/models/PGO or rejected357 proof relabel. One cooled358 real confirmation required.'};dump(r/'docs/round358-candidate-source-match.json',new)
note='357/aad6b7855fe3d3fa09bb6aaf7f570e8c82bec9da passes allactualA/C/Dgates, but C run-74166fe13b92 T.093872/M12972032/S722/K18.207246/63.012213 loses best23.033578/68.118071. REJECT complete standardatomicbatchwait/uint32epoch/stickycancel/noexceptstartupcallback threefile change and357image; original A178/C175/D334/source30/Make/README/images353 restored. Fresh originalC263 public+untrainedfull3623 at1/6/12/true-default8imagecalls, actualcachedrootMake/compositenativepublic/default12PASS with no compiler/trainingduplicate. Native20%hypothesis did not transfer; actual source grew50, no targetphase/cause claimed. New357native strict/race/GNUmodels/main/image/default proof remains rejectedsourcehistory. A74.572129/D63.721519 are lowerunchangedsource repeats; no causalregression/gain. Onecooled358push only>=06:24:20UTC, after357dispatch06:19:20. Exact rejectedsource round357-scored-source-match.json, board-round357-atomic-waits.json; restoredsource round358-candidate-source-match.json. A359 cuckoocache native mixed/rejected despite fewer cache misses, no officialtrial. Current bestscores unchanged. PRIVATE/MIT/publicationwindow unchanged.'
for name in ['track-c/PERF.md','docs/RESULTS.md','docs/SUBMISSION.md']:
 p=r/name;p.write_text(p.read_text()+'\n\n'+note+'\n')
p=r/'docs/STATE.md';p.write_text('# Original358 fully restored; cooled real confirmation pending\n\n'+note+'\n\nHEADstillrejected357untilrollback358commit/push; root/snapshot .build/round358/submitted-source EXACT passing353 original. Do not start a new selected candidate before358confirmation. Watch19840 terminal alltracksPASS; compiler/model/image/Make work complete. Original353 snapshot remains rollback. Other authorized chat359 finished/rejected/CPUHOLD. No newcompile/training/oracle work. Riskystartsstop14:00/runtime+Gitfreeze15:00/publicationONLYapproved15:00–16:00.\n\n'+p.read_text());dump(restore/'restore-partial.json',{'phase':'complete_original_local_proof','passed':True,'earliest_next_push_utc':'2026-11-02T06:24:20Z'});print('RESTORED358 exactoriginalA178/C175/D334; originalimage8/native12PASS; cooldown>=06:24:20UTC',flush=True)
