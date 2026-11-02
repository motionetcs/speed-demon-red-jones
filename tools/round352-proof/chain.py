from pathlib import Path
import datetime,json,subprocess,sys
r=Path.cwd();w=r/'.build/round352'
assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,11,2,14,tzinfo=datetime.timezone.utc)
for mode in ['fresh','gcc','build','image','defaults']:
 p=w/'proof'/mode/'report.json'
 if p.exists():assert json.loads(p.read_text())['passed'];print('AlreadyterminalPASS352',mode,flush=True);continue
 subprocess.run([sys.executable,str(w/'proof.py'),mode],check=True)
print('PASS352 complete compiler/image/default chain; not promoted',flush=True)
