from pathlib import Path
import datetime,hashlib,json,subprocess,sys,urllib.request
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');url='https://s3.amazonaws.com/raptors.dev/speeddemon.dev/2026/board/board.json';raw=r/'.out/board-watch/round391-current-full.json';proof_path=r/'docs/round391-feed-proof.json';retry='--retry' in sys.argv
actual=json.loads((r/'docs/board-round391-runtime8.json').read_text());assert actual['passed']and actual['commit']==subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip()
if retry:
 old=json.loads(proof_path.read_text());assert not old['passed']and old['attempt']==1;assert(datetime.datetime.now(datetime.timezone.utc)-datetime.datetime.fromisoformat(old['observed_at_utc'])).total_seconds()>=30
 failed=raw.with_name('round391-current-full-attempt1-malformed.json');assert hashlib.sha256(raw.read_bytes()).hexdigest()==old['sha256'];raw.rename(failed);old['raw_path']=str(failed.relative_to(r));(r/'docs/round391-feed-attempt1-malformed.json').write_text(json.dumps(old,indent=2)+'\n')
else:assert not raw.exists()and not proof_path.exists()
request=urllib.request.Request(url,headers={'User-Agent':'speed-demon-team-watch/1.0','Cache-Control':'no-cache'})
with urllib.request.urlopen(request,timeout=30)as response:
 status=response.status;headers=dict(response.headers);payload=response.read();assert status==200 and 'Content-Range'not in headers
raw.write_bytes(payload)
proof={'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':False,'attempt':2 if retry else 1,'source':url,'status':status,'headers':headers,'raw_path':str(raw.relative_to(r)),'bytes':len(payload),'sha256':hashlib.sha256(payload).hexdigest(),'scope':'One ordinary complete current publicfeed GET after terminal391 final runtime8 trial for rankings/source comparison. Raw bytes saved BEFORE parse. Only one delayed normal SAME-URL retry is allowed if producer JSON is malformed; no query/cachebuster/range/history/version/alternateidentity/access workaround and no partial reconstruction. Not unchanged-state polling.'};proof_path.write_text(json.dumps(proof,indent=2)+'\n')
try:feed=json.loads(payload)
except ValueError as e:
 proof['parse_error']=str(e);proof_path.write_text(json.dumps(proof,indent=2)+'\n');print('Producer malformed full HTTP response preserved, no ranking inferred; one delayed normal retry permitted');sys.exit(2)
proof.update(passed=True,feed_generated_at=feed['generated_at']);proof_path.write_text(json.dumps(proof,indent=2)+'\n');team=next(x for x in feed['teams']if x['slug']=='red-jones-00c4a7')
for t in 'acd':assert team['tracks'][t]['latest']['commit']==actual['commit']and team['tracks'][t]['latest']['run_id']==actual['tracks'][t]['run_id']
q=subprocess.run(['python3','tools/compare_board.py','--input',str(raw),'--baseline','.out/board-watch/round385-current-full.json','--snapshot','docs/round391-confirmed-board.json','--report','docs/round391-confirmed-comparison.json'],cwd=r,capture_output=True,text=True);assert q.returncode==0,q.stderr;print(q.stdout);print('Fullfeed saved',len(payload),proof['sha256'],proof['feed_generated_at'])
