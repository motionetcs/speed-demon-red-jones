from pathlib import Path
import json,subprocess,sys
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round384'
assert json.loads((w/'native-proof/report.json').read_text())['passed']
for mode in ['gcc','build','image','defaults']:
 assert not(w/'proof'/mode/'report.json').exists(),'Never duplicate completed stage'
 subprocess.run([sys.executable,str(w/'linux_proof.py'),mode],cwd=r,check=True)
print('PASS384 all Linux current-source proof; rootMake/source archive/one real board trial remain',flush=True)
