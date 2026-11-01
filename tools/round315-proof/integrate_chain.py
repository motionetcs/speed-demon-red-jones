import subprocess,sys
for script in ['.build/round315/integrate.py','.build/round315/post_make_screen.py']:
 q=subprocess.run([sys.executable,script])
 if q.returncode:raise SystemExit(q.returncode)
print('PASS315 source-specific integration and exact optimized postMake full confirmation; actual trial pending',flush=True)
