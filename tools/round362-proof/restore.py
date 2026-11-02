from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round362';restore=r/'.build/round363';assert not restore.exists();restore.mkdir()
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip();assert head=='fe3dca6c41e718b9150e34ab444774a28d166809';pre=read(w/'frozen.json');proof=read(r/'docs/round362-committed-source-match.json');board=read(r/'docs/board-round362-noplt.json');assert board['passed']and board['commit']==head
for row in proof['inputs']:assert sha(r/row['path'])==row['sha256']
assert board['tracks']['c']['K']==20.634447<23.033578
scored=dict(proof);scored.update(observed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),actual_board_confirmation_pending=False,source_commit=head,actual_board_report='docs/board-round362-noplt.json',actual_records=board['tracks'],actual_all_gates_passed=True,decision='REJECT complete362C fno-plt/main2linebreak/README/image: realK20.634447<best23.033578; A/Dunchangedlowerrepeats variation, no causalphase/Intelbinary claim.');dump(r/'docs/round362-scored-source-match.json',scored)
for name in ['Dockerfile','main.cpp','README.md']:shutil.copyfile(w/'original-retained/track-c'/name,r/'track-c'/name)
original=read(r/'docs/round358-final-source-match.json')
for row in original['inputs']:assert sha(r/row['path'])==row['sha256'],row['path']
assert sha(r/'Makefile')==original['Makefile_sha256']
for t,h in original['README_sha256'].items():assert sha(r/f'track-{t}/README.md')==h
snapshot=restore/'source';snapshot.mkdir()
for t in 'acd':shutil.copytree(r/f'track-{t}',snapshot/f'track-{t}')
shutil.copy2(r/'Makefile',snapshot/'Makefile');dump(restore/'restore-partial.json',{'phase':'completeoriginalCrestored','root_source_matches_passing358_all30':True,'A178_C175_D334':True,'image':pre['original_C_image']})
common=['docker','run','--rm','--pull=never','--platform','linux/amd64','--network=none','--read-only','--memory=8g','--memory-swap=8g','--pids-limit=512','--cap-drop=ALL','--security-opt=no-new-privileges','--user','65534:65534','--tmpfs','/tmp:rw,exec,size=1g'];pub=read(r/'docs/public-sha256.json')['tracks'];fresh=read(r/'docs/round356-c-asan-fresh-full.json');ref=next(x for x in fresh['checks']if x['case']=='full-seed3623');cases=[('public-full-seed1',r/'.data/c/public-full-seed1',pub['c']['inputs_sha256'],pub['c']['expected_output_sha256'][0]),('full-seed3623',r/'.data/c/full-seed3623',None,ref['reference_sha256'])];runs=[]
for label,data,recorded,expected in cases:
 hashes={p.name:sha(p)for p in data.iterdir()if p.is_file()}
 if recorded:assert hashes==recorded
 for threads in [1,6,12,None]:
  dest=restore/'original-image'/label/('default'if threads is None else str(threads));dest.mkdir(parents=True);dest.chmod(0o777)
  if threads is None:argv=[*common,'-v',str(data)+':/data:ro','-v',str(dest)+':/out:rw',pre['original_C_image']]
  else:argv=[*common,'-e','SPEED_DEMON_THREADS='+str(threads),'-v',str(data)+':/data:ro','-v',str(dest)+':/out:rw',pre['original_C_image'],'--data','/data','--out','/out']
  q=subprocess.run(argv,capture_output=True,text=True,timeout=180);assert q.returncode==0 and not q.stdout and not q.stderr,(label,threads,q.returncode,q.stderr);assert[p.name for p in dest.iterdir()]==['aggregates.txt'];actual=sha(dest/'aggregates.txt');assert actual==expected;runs.append({'case':label,'threads':threads,'true_ENTRYPOINT_noarg_nooverride_default':threads is None,'inputs_sha256':hashes,'sha256':actual,'image_id':pre['original_C_image'],'scope':'Freshrollback control using immutableoriginalC263image, no build/training/oldproofrelabel.'});dump(restore/'original-image-partial.json',{'runs':runs})
 assert{p.name:sha(p)for p in data.iterdir()if p.is_file()}==hashes
dump(r/'docs/round363-original-c-image-controls.json',{'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'official_score':False,'runs':runs,'scope':'8fresh originalCimage public/newuntrained3623 at1/6/12/true default12; no newcompiler/PGO or rejected352image substitution.'})
folder=restore/'final-make';folder.mkdir();controls={'a':r/'.build/round263/final-make/track-a','c':r/'.build/round263/final-make/track-c','d':r/'.build/round334/final-make/track-d'};expected={'a':'75db96e1b101aa09555e5576b201ef5c1a365b52b51339cce5763182e4d09b27','c':'db8972d55c2a7b58a42f83dc42aab8df84fe9bdf4761dfd121368a6e0278037a','d':'cf0ab08ff09b091ad9954cd365e92a1b0d014c5c31f5ecb2a74f15453761c404'}
for t,p in controls.items():assert sha(p)==expected[t];shutil.copyfile(p,folder/f'track-{t}');(folder/f'track-{t}').chmod(0o755)
cmd=['make','BUILD_DIR=.build/round363/final-make','all'];q=subprocess.run(cmd,cwd=r,capture_output=True,text=True,timeout=180);assert q.returncode==0 and not q.stderr and 'clang++'not in q.stdout and 'g++'not in q.stdout;dump(restore/'Make.json',{'command':cmd,'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr,'scope':'ActualrootMakewithbyteverifiedcachedoriginalA/C263,CURRENTD334; no repeatedcompiler.'});native=[]
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
new={'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'official_score':False,'actual_board_confirmation_pending':True,'source_parent':head,'inputs':inputs,'Makefile_sha256':original['Makefile_sha256'],'images':original['images'],'complete_file_sets_excluding_PERF':original['complete_file_sets_excluding_PERF'],'README_sha256':original['README_sha256'],'native_public_default_runs':native,'original_C_image_controls':'docs/round363-original-c-image-controls.json','scope':'Complete362C fno-plt/mainlinebreak/README/image rollback. All30originalpassing358 runtime/build/metadata/Make/fullsets/README/images match; fresh8originalCimage public/new3623 incltruedefault, actualcachedMake and12composite nativepublic/default PASS. No newcompiler/models/PGO or352proofrelabel. One normalcooled363 realconfirmation required.'};dump(r/'docs/round363-candidate-source-match.json',new)
note='362/fe3dca6c41e718b9150e34ab444774a28d166809 passes allrealA/C/Dgates, but C run-6c16f2baccbd T.076354/M12271616/S672/K20.634447/65.729642 loses retainedbestK23.033578/68.118071. REJECT complete -fno-plt inboth originalstatic/nativePGOpasses andmain2tokenidenticalstylelinebreaks/README/imagechange; exact original A178/C175/D334/source30/Make/README/images358 restored. Fresh originalC263public+untrained3623 at1/6/12/true-default8imagecalls, cachedrootMake/native12PASS, no compiler/model/PGO/reference regeneration repeated. New362GNUmodels/main237+25/oneimage651+50/default77+9/Make16 and actualproduction4memcmp+1memset GOTcall transformation remain historical. Fewerstaticstubjumps did not establish a target gain; no dynamicfrequency/phase/causal claim. A74.632678/D65.247823 lowerunchangedrepeats variation. Onecooled363push only>=06:57:29UTC afterdispatch06:52:29. Exactrejectedsource round362-scored-source-match.json/board-round362-noplt.json; restoredproof round363-candidate-source-match.json. Bestscores unchanged; PRIVATE/MIT/publicationwindow unchanged.'
for name in ['track-c/PERF.md','docs/RESULTS.md','docs/SUBMISSION.md']:
 p=r/name;p.write_text(p.read_text()+'\n\n'+note+'\n')
p=r/'docs/STATE.md';p.write_text('# Original363 restored; cooled realconfirmation pending\n\n'+note+'\n\nHEADstillrejected362untilrollback363commit/push; root/snapshot .build/round363/submitted-source EXACT passing358. Watch32826terminal alltracksPASS; no newcandidate before363realconfirmation. Complete original .build/round362/original-retained retained. No compiler/model/training/oracle work active. Otherauthorizedchat CPUHOLD. Runtime+Gitfreeze15:00/risky14:00/publicationONLYapproved15:00–16:00UTC afterfinalcleanreview.\n\n'+p.read_text());dump(restore/'restore-partial.json',{'phase':'complete_original_local_proof','passed':True,'earliest_next_push_utc':'2026-11-02T06:57:29Z'});print('RESTORED363 exactoriginalA178/C175/D334; originalimage8/native12PASS; cooldown>=06:57:29UTC',flush=True)
