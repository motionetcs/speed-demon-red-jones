import subprocess,sys
for script in ['.build/round305/fresh_native.py','.build/round305/linux_chain.py']:
 q=subprocess.run([sys.executable,script])
 if q.returncode:raise SystemExit(q.returncode)
print('PASS305 complete exact native/fresh/GCC/image/default local proof, root unmodified',flush=True)
