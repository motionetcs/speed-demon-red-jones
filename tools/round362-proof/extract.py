from pathlib import Path
import hashlib,json,subprocess,datetime
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round362';out=w/'emitted';out.mkdir();out.chmod(0o777)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
build=json.loads((w/'proof/build/report.json').read_text());assert all(json.loads((w/f'proof/{m}/report.json').read_text())['passed']for m in ['gcc','build','image','defaults']);image=build['image_id'];common=['docker','run','--rm','--pull=never','--platform','linux/amd64','--network=none','--read-only','--memory=8g','--memory-swap=8g','--pids-limit=512','--cap-drop=ALL','--security-opt=no-new-privileges','--user','65534:65534','--tmpfs','/tmp:rw,exec,size=1g']
commands=[];argv=[*common,'--entrypoint','cat',image,'/app/solution'];commands.append(argv)
with(out/'solution').open('wb')as stream:q=subprocess.run(argv,stdout=stream,stderr=subprocess.PIPE,timeout=120)
assert q.returncode==0 and not q.stderr;assert sha(out/'solution')==build['elf_sha256']
argv=[*common,'--entrypoint','objdump','-v',str(out)+':/bank:ro','gcc:15@sha256:eb5e64286ad47187b32bda75c6b6916166ecb41da56559b8b09e0001748d2cce','-d','-C','--no-show-raw-insn','/bank/solution'];commands.append(argv)
with(out/'disassembly.txt').open('w')as stream:q=subprocess.run(argv,stdout=stream,stderr=subprocess.PIPE,timeout=120)
assert q.returncode==0 and not q.stderr
report={'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'official_score':False,'image_id':image,'elf_sha256':sha(out/'solution'),'disassembly_sha256':sha(out/'disassembly.txt'),'commands':commands,'scope':'Exact once-built362 production image executable read without executing/retraining it; pinnedGNU objdump read-only. Static analysis may test ownhotcalls, not dynamic frequency/targetgain or organizerELF.'};(out/'extraction.json').write_text(json.dumps(report,indent=2)+'\n');print('EXTRACTED362',report['image_id'],report['elf_sha256'],report['disassembly_sha256'])
