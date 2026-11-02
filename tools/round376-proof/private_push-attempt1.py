from pathlib import Path
import datetime,hashlib,json,re,shutil,subprocess,sys
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round376'
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def digest(b):return hashlib.sha256(b).hexdigest()
def dump(p,j):p.write_text(json.dumps(j,indent=2)+'\n')
proof=read(r/'docs/round376-candidate-source-match.json');parent=proof['source_parent'];assert parent=='83630432c7acd216b9813027a2e863fe0fd8aaee'
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip()==parent
assert subprocess.check_output(['git','branch','--show-current'],cwd=r,text=True).strip()=='speed-demon'
assert not subprocess.check_output(['git','diff','--cached','--name-only'],cwd=r,text=True).strip()
now=datetime.datetime.now(datetime.timezone.utc);assert datetime.datetime(2026,11,2,8,52,16,tzinfo=datetime.timezone.utc)<=now<datetime.datetime(2026,11,2,14,tzinfo=datetime.timezone.utc)
assert not(w/'push.json').exists();assert subprocess.check_output(['git','remote','get-url','origin'],cwd=r,text=True).strip()in['https://github.com/motionetcs/speed-demon-red-jones.git','git@github.com:motionetcs/speed-demon-red-jones.git']
for row in proof['inputs']:assert sha(r/row['path'])==row['sha256']
assert len(proof['inputs'])==30 and sha(r/'Makefile')==proof['Makefile_sha256'];assert sha(r/'docs/emoji-result.jpg')=='39c27548e6513e81ae0badc343f5ad862ad361b4a7319af368a7deed540e7573'
shutil.copy2(Path(__file__),w/'private_push.py');archive=r/'tools/round376-proof';shutil.copy2(w/'private_push.py',archive/'private_push.py')
pa=read(r/'docs/round376-proof-archive.json');pa['executed_proof_drivers']={str(p.relative_to(r)):sha(p)for p in archive.rglob('*')if p.is_file()};dump(r/'docs/round376-proof-archive.json',pa)
patterns={'github_token':rb'(?<![A-Za-z0-9_-])(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{25,})','openai_style_token':rb'(?<![A-Za-z0-9_-])sk-[A-Za-z0-9_-]{20,}','aws_access_id':rb'(?<![A-Z0-9])AKIA[0-9A-Z]{16}(?![A-Z0-9])','private_key_pem':rb'-----BEGIN (?:[A-Z]+ )?PRIVATE KEY-----'}
def scan():
 files=[p for p in subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=r).decode().split('\0')if p and(r/p).is_file()];findings=[]
 for p in files:
  data=(r/p).read_bytes()
  for kind,pattern in patterns.items():
   if re.search(pattern,data):findings.append({'path':p,'kind':kind})
 assert not findings,findings;assert sorted(p for p in files if Path(p).suffix.lower()in['.png','.jpg','.jpeg'])==['docs/emoji-result.jpg'];return files
files=scan();review=read(r/'docs/PUBLICATION-REVIEW.json');review['working_tree_credential_review']={'observed_at_utc':now.isoformat(),'source_commit':parent,'file_count':len(files),'scope':'Pre-private376 intended files: four configured credential heuristics, not an absence guarantee. Final frozen-head/history/image review still required before approved publication window.','findings':[]};dump(r/'docs/PUBLICATION-REVIEW.json',review)
changes=[row[3:]for row in subprocess.check_output(['git','status','--porcelain','-z'],cwd=r,text=True).split('\0')if row];allowed={'track-a/main.cpp','track-a/README.md','track-a/PERF.md','track-c/PERF.md','track-d/PERF.md'}
for p in changes:assert p in allowed or p.startswith('docs/')or any(p.startswith(f'tools/round{n}-')for n in range(372,377)),('Unexpected change',p)
q=subprocess.run(['git','diff','--check'],cwd=r,capture_output=True,text=True);assert q.returncode==0,q.stdout+q.stderr
subprocess.run(['git','add','--',*changes],cwd=r,check=True);staged=subprocess.check_output(['git','diff','--cached','--name-only'],cwd=r,text=True).splitlines();assert 'track-a/main.cpp'in staged and 'track-a/README.md'in staged and 'track-a/Dockerfile'not in staged
assert all(not(p.endswith('.cpp')or p.endswith('.hpp'))or p.startswith('tools/')or p=='track-a/main.cpp'for p in staged)
dump(w/'staged-review.json',{'source_parent':parent,'staged_paths':staged,'intended_files':len(files),'credential_pattern_findings':[],'scope':'Only A376 main/README, task-owned PERF/docs/review/proof archives; no data, output, profile, binary or runtime answer cache.'})
q=subprocess.run(['git','commit','-m','Balance parser work with exact newline-aligned ranges'],cwd=r,capture_output=True,text=True,timeout=120);dump(w/'commit.json',{'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr});assert q.returncode==0,(q.stdout,q.stderr)
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip()
for row in proof['inputs']:assert sha(r/row['path'])==row['sha256']==digest(subprocess.check_output(['git','show',head+':'+row['path']],cwd=r)),row['path']
assert sha(r/'Makefile')==proof['Makefile_sha256']==digest(subprocess.check_output(['git','show',head+':Makefile'],cwd=r))
for t,names in proof['complete_file_sets_excluding_PERF'].items():
 assert sorted(p for p in subprocess.check_output(['git','ls-tree','-r','--name-only',head,f'track-{t}/'],cwd=r,text=True).splitlines()if not p.endswith('/PERF.md'))==names
 assert sha(r/f'track-{t}/README.md')==proof['README_sha256'][t]==digest(subprocess.check_output(['git','show',head+f':track-{t}/README.md'],cwd=r))
committed=dict(proof);committed.update(source_commit=head,selected_commit=head,observed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());dump(r/'docs/round376-committed-source-match.json',committed)
q=subprocess.run([sys.executable,'tools/audit_entry.py'],cwd=r,capture_output=True,text=True,timeout=120);(w/'audit.stdout').write_text(q.stdout);(w/'audit.stderr').write_text(q.stderr);audit=read(r/'docs/ENTRY-AUDIT.json');assert q.returncode==0 and audit['source_commit']==head and audit['all_current_checks_passed'];assert audit['repository']['isPrivate']and(audit['repository'].get('licenseInfo')or{}).get('key')=='mit'
old=read(r/'docs/PUBLICATION-REVIEW.json');keep={k:v for k,v in old.items()if k in['tracked_image_identity','working_tree_credential_review','tracked_image_identity_recheck']};dump(w/'publication-review-before.json',old)
q=subprocess.run([sys.executable,'.build/review-publication.py'],cwd=r,capture_output=True,text=True,timeout=120);(w/'history-review.stdout').write_text(q.stdout);(w/'history-review.stderr').write_text(q.stderr);assert q.returncode==0,q.stderr
review=read(r/'docs/PUBLICATION-REVIEW.json');assert review['reviewed_head']==head and not review['credential_pattern_findings']and review['tracked_images']==['docs/emoji-result.jpg'];review.update(keep);files=scan();review['working_tree_credential_review']={'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_commit':head,'file_count':len(files),'scope':'376 current-head intended files/history reviewed with four heuristics, not an absence guarantee; sole unchanged public-board screenshot identity preserved. Final frozen-head publication review remains mandatory.','findings':[]};dump(r/'docs/PUBLICATION-REVIEW.json',review)
q=subprocess.run(['git','push','origin','HEAD:speed-demon'],cwd=r,capture_output=True,text=True,timeout=180);receipt={'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'commit':head,'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr,'repository':'motionetcs/speed-demon-red-jones','branch':'speed-demon','visibility':'PRIVATE','source_proof':'docs/round376-committed-source-match.json'};dump(w/'push.json',receipt);assert q.returncode==0,(q.stdout,q.stderr)
assert subprocess.check_output(['git','ls-remote','origin','refs/heads/speed-demon'],cwd=r,text=True).split()[0]==head
note=f'A376 PRIVATE pushed at{receipt["observed_at_utc"]}, HEAD/origin {head}; ONE normal all-track real trial pending. Baseline A K32.070167/points75.305061; keep only supported totalK gain, otherwise restore original371 main/README/image and one cooled real confirmation. Source30/Make/fullsets/README/submitted snapshot/local images bind docs/round376-committed-source-match.json. No new C/D candidate or extra training. Private until approved15:00–16:00UTC, risky starts stop14:00/runtime+Gitfreeze15:00.'
p=r/'docs/STATE.md';p.write_text('# C376 real board trial pending\n\n'+note+'\n\n'+p.read_text());dump(w/'ACTIVE.json',{'status':'private_pushed_real_board_pending','commit':head,'note':note});print('PUSHED376',head,'PRIVATE/MIT; one normal all-track watcher next',flush=True)
