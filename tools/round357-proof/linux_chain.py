from pathlib import Path
import datetime,json,subprocess,sys
w=Path('.build/round357')
assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,11,2,14,tzinfo=datetime.timezone.utc)
for mode in ['model','gcc','build','image','defaults']:
 p=w/'proof'/mode/'report.json'
 if p.exists():
  assert json.loads(p.read_text())['passed'];print('AlreadyterminalPASS357',mode,flush=True);continue
 subprocess.run([sys.executable,str(w/'linux_proof.py'),mode],check=True)
print('PASS357 complete Linux chain; realtrialpending',flush=True)
