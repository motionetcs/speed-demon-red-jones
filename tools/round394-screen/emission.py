from pathlib import Path
import datetime,hashlib,json,os,re,subprocess
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round394';d=w/'emission';assert not d.exists();d.mkdir()
image='gcc:15@sha256:eb5e64286ad47187b32bda75c6b6916166ecb41da56559b8b09e0001748d2cce'
source='''extern "C" void write_low(const void* p){__builtin_prefetch(p,1,1);}
extern "C" void write_high(const void* p){__builtin_prefetch(p,1,3);}
extern "C" void read_low(const void* p){__builtin_prefetch(p,0,1);}
extern "C" void read_high(const void* p){__builtin_prefetch(p,0,3);}
'''
(d/'prefetch.cpp').write_text(source)
cmd=['docker','run','--rm','-i','--platform','linux/amd64','--network','none','--read-only','--user','65534:65534','--memory','8g','--memory-swap','8g','--pids-limit','512','--cap-drop','ALL','--security-opt','no-new-privileges','--tmpfs','/tmp:rw,noexec,nosuid,size=256m',image,'g++','-x','c++','-std=c++20','-O3','-march=raptorlake','-S','-masm=intel','-fno-asynchronous-unwind-tables','-fno-ident','-o','-','-']
q=subprocess.run(cmd,input=source,capture_output=True,text=True,timeout=120)
(d/'probe.s').write_text(q.stdout);(d/'probe.stderr').write_text(q.stderr)
assert q.returncode==0 and not q.stderr,q.stderr
bodies={}
for name in ['write_low','write_high','read_low','read_high']:
 match=re.search(r'^'+name+r':\n(.*?)^\s*\.size\s+'+name+r',',q.stdout,re.M|re.S);assert match,name
 bodies[name]=[line.strip()for line in match[1].splitlines()if line.strip()and not line.lstrip().startswith('.')]
assert bodies['read_low']!=bodies['read_high'],'Positive read-locality probe must distinguish the hints'
result={'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'official_score':False,'scope':'One standalone emitted-instruction probe under exact pinned GCC image, explicit -march=raptorlake. This is not a production source/ELF, organizer executable, timing, cache effect or sanitizer proof. Actual production Docker flags remain unchanged. Read-only query hints are included only as a positive control for locality operand changes. No training/generator/oracle or production image build.','command':cmd,'returncode':q.returncode,'source_sha256':hashlib.sha256(source.encode()).hexdigest(),'assembly_sha256':hashlib.sha256(q.stdout.encode()).hexdigest(),'instruction_bodies':bodies,'write_instructions_identical':bodies['write_low']==bodies['write_high'],'read_instructions_differ':bodies['read_low']!=bodies['read_high']}
(d/'report.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'probe_passed':True,'instructions':bodies,'write_instructions_identical':result['write_instructions_identical']}),flush=True)
