from pathlib import Path
import json,subprocess,sys
w=Path('.build/round286')
for mode in ['gcc','build','image','defaults']:
 p=w/'linux-proof'/mode/'report.json'
 if p.exists():assert json.loads(p.read_text())['passed'];print('Already terminalPASS286',mode,flush=True);continue
 q=subprocess.run([sys.executable,str(w/'linux_proof.py'),mode])
 if q.returncode:raise SystemExit(q.returncode)
print('PASS286 complete Linux chain; source not yet promoted',flush=True)
