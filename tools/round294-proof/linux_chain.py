from pathlib import Path
import json,subprocess,sys
w=Path('.build/round294')
for mode in ['model','gcc','build','image','defaults']:
 p=w/'linux-proof'/mode/'report.json'
 if p.exists():assert json.loads(p.read_text())['passed'];print('Already terminalPASS294',mode,flush=True);continue
 q=subprocess.run([sys.executable,str(w/'linux_proof.py'),mode])
 if q.returncode:raise SystemExit(q.returncode)
print('PASS294 complete Linux chain; source not promoted',flush=True)
