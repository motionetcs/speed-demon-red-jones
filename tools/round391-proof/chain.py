from pathlib import Path
import subprocess,sys
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round391'
for mode in['native','gcc','build','image','defaults']:
 assert not(w/'proof'/mode/'report.json').exists(),'Never duplicate a completed stage'
 subprocess.run([sys.executable,str(w/'proof.py'),mode],cwd=r,check=True)
print('PASS391 fresh runtime8 strict/image/default proof; root Make/source archive/one real trial remain',flush=True)
