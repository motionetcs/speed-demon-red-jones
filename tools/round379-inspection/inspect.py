from pathlib import Path
import datetime,hashlib,json,subprocess
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round379-inspect';assert not w.exists();w.mkdir();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();prior=json.loads((r/'docs/round377-final-source-match.json').read_text())
for row in prior['inputs']:assert sha(r/row['path'])==row['sha256']
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip()==prior['source_commit'];image=prior['images']['d'];compiler='gcc:15@sha256:eb5e64286ad47187b32bda75c6b6916166ecb41da56559b8b09e0001748d2cce';report={'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Read-only static inspection of immutable CURRENTD334 local PGO replay ELF. No compilation, program/data/reference/model/training/timing run; no organizer ELF, instruction frequency, cache-miss or speed claim. Temporary container used only to copy own executable, then removed.','image_id':image,'commands':[]}
def command(argv,label):
 q=subprocess.run(list(map(str,argv)),cwd=r,capture_output=True,text=True,timeout=120);report['commands'].append({'label':label,'argv':list(map(str,argv)),'returncode':q.returncode});(w/(label+'.stdout')).write_text(q.stdout);(w/(label+'.stderr')).write_text(q.stderr);assert q.returncode==0,(label,q.stderr);return q.stdout
cid=command(['docker','create','--platform','linux/amd64','--network=none','--read-only','--user','65534:65534',image],'create').strip()
try:command(['docker','cp',cid+':/app/solution',w/'original-solution'],'copy')
finally:command(['docker','rm',cid],'remove')
assert sha(w/'original-solution')=='6b45fc7b9c30e82390c8e43df377755dcff5f1d42ee8996b40287860a6d48b1d'
common=['docker','run','--rm','--pull=never','--platform','linux/amd64','--network=none','--read-only','--memory=8g','--memory-swap=8g','--pids-limit=512','--cap-drop=ALL','--security-opt=no-new-privileges','--user','65534:65534','-v',str(w)+':/evidence:ro']
command([*common,compiler,'nm','--size-sort','--radix=d','-C','--defined-only','/evidence/original-solution'],'symbols');command([*common,compiler,'readelf','-W','-S','/evidence/original-solution'],'sections');command([*common,compiler,'objdump','-C','-d','--no-show-raw-insn','/evidence/original-solution'],'disassembly');own=[]
for line in(w/'symbols.stdout').read_text().splitlines():
 if any(x in line for x in ['main::{lambda','FastDistances','RadixHeap','SharedCursor','Scanner::','DegreeBytes']):own.append(line)
report.update(passed=True,elf_sha256=sha(w/'original-solution'),own_symbol_sizes_decimal=own,files_sha256={p.name:sha(p)for p in w.iterdir()if p.is_file()and p.suffix in ['.stdout','.stderr']});(w/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'passed':True,'scope':'Static local image only, no target timing','own_symbol_sizes_decimal':own[-30:]},indent=2),flush=True)
