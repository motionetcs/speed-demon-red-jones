from pathlib import Path
import json,subprocess,sys
r=Path.cwd();w=r/'.build/round370'
assert not(w/'header-proof/report.json').exists()
subprocess.run([sys.executable,str(w/'header_proof.py')],check=True,cwd=r)
for mode in ['fresh','build','image','defaults']:
 assert not(w/'proof'/mode/'report.json').exists(),'Do not duplicate completed stage'
 subprocess.run([sys.executable,str(w/'production_proof.py'),mode],check=True,cwd=r)
print('PASS370 production chain; actual rootMake/source archive/one real trial remain',flush=True)
