from pathlib import Path
import datetime,hashlib,json,subprocess
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round361';assert not w.exists();w.mkdir();out=w/'out';out.mkdir();out.chmod(0o777)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source='''#include <cstring>
extern "C" __attribute__((noinline)) bool same(const char* a,const char* b,unsigned long size){return std::memcmp(a,b,size)==0;}
int main(int argc,char** argv){return same(argv[0],argv[argc-1],1)?0:1;}
''';(w/'probe.cpp').write_text(source)
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip();assert head=='99aa8f8dadd39cb6edb70dad34f8427b5fa0ff65';proof=json.loads((r/'docs/round358-final-source-match.json').read_text());bindings={x['path']:x['sha256']for x in proof['inputs']};bindings['Makefile']=proof['Makefile_sha256']
for p,h in bindings.items():assert sha(r/p)==h
image='gcc:15@sha256:eb5e64286ad47187b32bda75c6b6916166ecb41da56559b8b09e0001748d2cce'
script='''set -eu
g++ --version >/out/compiler.txt
for mode in baseline noplt; do
 extra=
 if test "$mode" = noplt; then extra=-fno-plt; fi
 g++ -std=c++20 -O3 -march=native -DNDEBUG -pthread -static -Wall -Wextra -Wpedantic -Werror $extra /work/probe.cpp -o /out/$mode
 objdump -d --disassemble=same /out/$mode >/out/$mode.disassembly.txt
 readelf -Wr /out/$mode >/out/$mode.relocations.txt
 /out/$mode
done
'''
argv=['docker','run','--rm','--pull=never','--platform','linux/amd64','--network=none','--read-only','--memory=8g','--memory-swap=8g','--pids-limit=512','--cap-drop=ALL','--security-opt=no-new-privileges','--user','65534:65534','--tmpfs','/tmp:rw,exec,size=1g','-i','--entrypoint','/bin/sh','-v',str(w)+':/work:ro','-v',str(out)+':/out:rw',image,'-s']
report={'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'official_score':False,'production_candidate':False,'scope':'One minimal unshipped static GNU15.3 IFUNC memcmp equality-call shape probe: exactly two compiles/link modes baseline and fno-plt, no PGO/training/benchmark/host or selectedsource changes. Static instruction evidence only, not current wholeproduction emittedshape or speed/correctness/score proof.','source_parent':head,'root_bindings':bindings,'probe_sha256':sha(w/'probe.cpp'),'argv':argv,'script':script,'primary_source':'https://gcc.gnu.org/onlinedocs/gcc/Code-Gen-Options.html#fno-plt'}
(w/'partial.json').write_text(json.dumps(report,indent=2)+'\n');q=subprocess.run(argv,input=script,text=True,capture_output=True,timeout=180);(w/'stdout').write_text(q.stdout);(w/'stderr').write_text(q.stderr);assert q.returncode==0 and not q.stdout and not q.stderr,(q.returncode,q.stderr)
for p,h in bindings.items():assert sha(r/p)==h
report.update(passed=True,completed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),compiler=(out/'compiler.txt').read_text(),baseline_disassembly=(out/'baseline.disassembly.txt').read_text(),noplt_disassembly=(out/'noplt.disassembly.txt').read_text(),output_sha256={p.name:sha(p)for p in out.iterdir()if p.is_file()});(w/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS361 minimal static IFUNC probe; no production/timing/official gain',report['baseline_disassembly'],report['noplt_disassembly'],flush=True)
