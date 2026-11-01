from pathlib import Path
import json,os,subprocess,sys
r=Path.cwd();w=r/'.build/round305';native=json.loads((w/'native-proof/report.json').read_text());assert native['passed'];report=r/'docs/round305-c-asan-fresh-full.json';data=r/'.data/c/full-seed3313'
if report.exists():assert json.loads(report.read_text())['passed'];print('Already terminalPASS305 fresh full',flush=True);raise SystemExit(0)
assert not data.exists(),'Do not regenerate existing completed data/reference; inspect recovery first'
cmd=[sys.executable,'tools/verify.py','--run-id','round305-asan-fresh-full','--source-root',str(w/'source'),'--binary-dir',str(w/'native-proof/asan'),'--tracks','c','--threads','1','6','12','--scale','full','--seeds','3313','--skip-adversarial','--report',str(report)]
q=subprocess.run(cmd,capture_output=True,text=True,env=dict(os.environ,PYTHONPATH=str(r/'tools'),ASAN_OPTIONS='halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1'),timeout=1200);(w/'fresh-native.stdout').write_text(q.stdout);(w/'fresh-native.stderr').write_text(q.stderr);(w/'fresh-native.command.json').write_text(json.dumps({'command':cmd,'returncode':q.returncode},indent=2)+'\n');assert q.returncode==0,(q.returncode,q.stdout[-1500:],q.stderr[-1500:]);assert json.loads(report.read_text())['passed'];print('PASS305 new untrained full3313 ASAN/reference1/6/12',flush=True)
