from pathlib import Path
from collections import Counter
import datetime,hashlib,json,re,struct,subprocess
r=Path.cwd();w=r/'.build/round360';elf=r/'.build/c-original-abi/solution';dis=r/'.build/c-original-abi/disassembly.txt';prior=r/'docs/c-original-field-abi-inspection.json';proof=r/'docs/round353-final-source-match.json'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
binding=json.loads(prior.read_text());selected=json.loads(proof.read_text());assert sha(elf)==binding['elf_sha256']=='406fe1f9130ba9f98b612caa08f83a75b1299466b4a34ac10d659f928a7ecc83';assert sha(dis)==binding['disassembly_sha256']=='0694720ed7e841485d0c0203facba00d4e888aae0c4e5608cf40c31944124321';assert binding['original_image_id']==selected['images']['c']
source={x['path']:x['sha256'] for x in selected['inputs'] if x['path'].startswith('track-c/')}
for rel,h in source.items():assert sha(r/rel)==h,rel
assert sha(r/'track-c/main.cpp')==binding['original_main_sha256']
b=elf.read_bytes();h=struct.unpack_from('<16sHHIQQQIHHHHHH',b);assert h[0][:6]==b'\x7fELF\x02\x01' and h[2]==62
sections=[struct.unpack_from('<IIQQQQIIQQ',b,h[6]+i*h[11]) for i in range(h[12])];names=sections[h[13]];strs=b[names[4]:names[4]+names[5]]
def cstr(data,off):return data[off:data.find(b'\0',off)].decode('utf-8',errors='replace')
byname={cstr(strs,s[0]):s for s in sections};symbols={}
for s in sections:
 if s[1] not in [2,11]:continue
 st=sections[s[6]];table=b[st[4]:st[4]+st[5]]
 for off in range(s[4],s[4]+s[5],s[9]):
  name,info,other,shndx,value,size=struct.unpack_from('<IBBHQQ',b,off)
  if value and name:symbols.setdefault(value,[]).append({'name':cstr(table,name),'type':info&15,'size':size})
relocations={}
for name,s in byname.items():
 if s[1]!=4 or 'plt' not in name:continue
 for off in range(s[4],s[4]+s[5],s[9]):
  addr,info,addend=struct.unpack_from('<QQq',b,off);relocations[addr]={'kind':info&0xffffffff,'resolver':addend,'symbols':symbols.get(addend,[])}
plt=byname['.plt'];stubs={}
for delta in range(plt[5]-5):
 off=plt[4]+delta
 if b[off:off+2]!=b'\xff\x25':continue
 addr=plt[3]+delta;got=addr+6+struct.unpack_from('<i',b,off+2)[0]
 if got in relocations:stubs[addr]={'address':hex(addr),'got_address':hex(got),'relocation':relocations[got]}
loads=[struct.unpack_from('<IIQQQQQQ',b,h[5]+i*h[9]) for i in range(h[10])];loads=[p for p in loads if p[0]==1]
def bytes_at(addr,n):
 for p in loads:
  if p[3]<=addr and addr+n<=p[3]+p[5]:return b[p[2]+addr-p[3]:p[2]+addr-p[3]+n]
 raise AssertionError(('unmapped',hex(addr)))
fn='';calls=[];narrow_calls=[];narrow_functions=set();direct_other=[];indirect=[]
for line in dis.read_text().splitlines():
 header=re.match(r'^([0-9a-f]+) <(.*)>:$',line)
 if header:fn=header[2]
 narrow=('main::' in fn and 'operator()<unsigned char>' in fn and fn.endswith('operator()(unsigned int) const') and 'parallel<' not in fn and '.cold' not in fn)
 if narrow:narrow_functions.add(fn)
 call=re.match(r'^\s*([0-9a-f]+):\s+call\s+([0-9a-f]+)(?:\s|$)(.*)',line)
 if call:
  addr,target=int(call[1],16),int(call[2],16)
  if target in stubs:
   instruction=bytes_at(addr,5);assert instruction[0]==0xe8 and addr+5+struct.unpack_from('<i',instruction,1)[0]==target
   row={'caller':fn,'instruction':line.strip(),'call_address':hex(addr),'plt':stubs[target]};calls.append(row)
   if narrow:narrow_calls.append(row)
  elif narrow:direct_other.append({'instruction':line.strip(),'target':hex(target)})
 elif narrow and re.match(r'^\s*[0-9a-f]+:\s+call\s+\*',line):indirect.append(line.strip())
def aliases(row):return '/'.join(sorted(set(s['name'] for s in row['plt']['relocation']['symbols'] if s['type']==10))) or 'unresolved_IFUNC'
report={'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'official_score':False,'executed_programs_or_compilers':False,'scope':'Read-only parsing of already-existing original C production ELF and its already-recorded GNU disassembly. Every direct call-to-PLT used below is checked against the actual ELF E8 bytes and target stub FF25/GOT/IRELATIVE relocation, not inferred from symbol spelling alone. No disassembler rerun, compiler, model, generator, benchmark, training, Docker execution or board fetch. Static call-site counts are NOT execution frequencies, costs or a speedup.','current_head_context':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'restored_C_source_sha256':source,'source_anchor':str(proof.relative_to(r)),'source_anchor_sha256':sha(proof),'prior_ELF_image_binding':str(prior.relative_to(r)),'prior_ELF_image_binding_sha256':sha(prior),'image_id':binding['original_image_id'],'local_ELF_path':str(elf.relative_to(r)),'local_ELF_sha256':sha(elf),'ELF_type':h[1],'ELF_machine':h[2],'local_disassembly_path':str(dis.relative_to(r)),'local_disassembly_sha256':sha(dis),'plt_stub_count':len(stubs),'plt_stubs':list(stubs.values()),'whole_ELF_direct_PLT_call_sites':len(calls),'whole_ELF_direct_PLT_alias_counts':dict(Counter(aliases(x) for x in calls)),'default_narrow_worker_functions':sorted(narrow_functions),'default_narrow_direct_PLT_calls':narrow_calls,'default_narrow_PLT_alias_counts':dict(Counter(aliases(x) for x in narrow_calls)),'default_narrow_other_direct_calls':direct_other,'default_narrow_indirect_calls':indirect,'primary_docs':'https://gcc.gnu.org/onlinedocs/gcc/Code-Gen-Options.html','docs_scope':'Current primary GCC manual describes GOT-call substitution for PLT calls. Versioned15.3/15.2 HTML opens were unavailable; this is generic documented behavior, not an exact-version emitted-change proof. Static linking does not itself imply absence of IFUNC PLT stubs, as the bound ELF demonstrates.','limitations':'Original exact C source/PGO/local image bound. Not the unexposed organizer ELF. A/D current original production ELF/disassembly not located in existing named extracts; their feasibility is not established here. No dynamic frequency, Intel profile, branch-miss, cache or cycle claim. A flags-only candidate would still need actual compiler/linker output showing the intended call transformation, exact current-image checks and a real board score.'}
assert len(narrow_functions)==1;out=w/'report.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(out),'report_sha256':sha(out),'image':report['image_id'],'ELF_sha256':sha(elf),'plt_stubs':len(stubs),'default_narrow_PLT_calls':len(narrow_calls),'default_narrow_alias_counts':report['default_narrow_PLT_alias_counts'],'default_narrow_other_direct_calls':len(direct_other),'default_narrow_indirect_calls':len(indirect)},indent=2))
