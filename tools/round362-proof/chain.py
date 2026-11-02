import subprocess,sys
from pathlib import Path
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh')
for mode in ['fresh','gcc','build','image','defaults']:
 p=r/'.build/round362/proof'/mode/'report.json'
 assert not p.exists(),'Do not repeat completed mode'
 subprocess.run([sys.executable,str(r/'.build/round362/proof.py'),mode],cwd=r,check=True)
print('PASS362 Linux chain; actual production callshape/rootMake/realtrial pending',flush=True)
