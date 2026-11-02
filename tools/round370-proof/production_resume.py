from pathlib import Path
import json,subprocess,sys
r=Path.cwd();w=r/'.build/round370'
for completed in ['header-proof/report.json','proof/fresh/report.json','proof/build/report.json']:
 assert json.loads((w/completed).read_text())['passed']
for mode in ['image','defaults']:
 assert not(w/'proof'/mode/'report.json').exists(),'No duplicate completed stage'
 subprocess.run([sys.executable,str(w/'production_proof.py'),mode],check=True,cwd=r)
print('PASS370 one image+actual default replay continuation',flush=True)
