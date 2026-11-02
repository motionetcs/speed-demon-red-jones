from pathlib import Path
import subprocess,sys
r=Path.cwd();w=r/'.build/round376'
for mode in ['gnu','build','image','defaults']:
 assert not(w/'proof'/mode/'report.json').exists(),'Do not repeat completed stage'
 subprocess.run([sys.executable,str(w/'linux_proof.py'),mode],cwd=r,check=True)
print('PASS376 Linux chain; integration/exact30/archive/rootMake/real trial still required',flush=True)
