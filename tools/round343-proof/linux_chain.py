from pathlib import Path
import datetime,json,subprocess
r=Path.cwd();w=r/'.build/round343';assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,11,2,14,tzinfo=datetime.timezone.utc)
for mode in ['gcc','build','image','defaults']:
 report=w/'linux-proof'/mode/'report.json';assert not report.exists(),'Do not duplicate completed '+mode
 subprocess.run(['python3',str(w/'linux_proof.py'),mode],check=True)
 assert json.loads(report.read_text())['passed']
print('PASS A343 complete pinned compiler/exact-image/default chain',flush=True)
