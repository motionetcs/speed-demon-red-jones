from pathlib import Path
import json,subprocess,sys
w=Path('.build/round290')
models=w/'linux-proof/models/report.json'
if models.exists():assert json.loads(models.read_text())['passed'];print('Already terminalPASS290 GCC models',flush=True)
else:
 q=subprocess.run([sys.executable,str(w/'linux_models.py')])
 if q.returncode:raise SystemExit(q.returncode)
for mode in ['gcc','build','image','defaults']:
 p=w/'linux-proof'/mode/'report.json'
 if p.exists():assert json.loads(p.read_text())['passed'];print('Already terminalPASS290',mode,flush=True);continue
 q=subprocess.run([sys.executable,str(w/'linux_proof.py'),mode])
 if q.returncode:raise SystemExit(q.returncode)
print('PASS290 complete Linux chain; source not yet promoted',flush=True)
