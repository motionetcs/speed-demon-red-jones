from pathlib import Path
from collections import Counter
import datetime,hashlib,json,re,struct
r=Path.cwd();w=r/'.build/round362-review';src=r/'.build/round362/source';emitted=r/'.build/round362/emitted'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
old=read(r/'.build/round360/report.json');assert sha(r/'.build/round360/report.json')=='0da422e25d41e997e4fa7deff72ae8487edbfd43c66ac795567dc98662ddd745'
assert sha(r/old['local_ELF_path'])==old['local_ELF_sha256'] and sha(r/old['local_disassembly_path'])==old['local_disassembly_sha256']
frozen=read(r/'.build/round362/frozen.json');build=read(r/'.build/round362/proof/build/report.json');extract=read(emitted/'extraction.json');assert build['passed'] and extract['passed'] and build['source_sha256']==frozen['source_sha256']
for rel,h in frozen['source_sha256'].items():assert sha(src/rel)==h,rel
assert frozen['C_main_whitespace_token_equal'] and frozen['original_C_image']==old['image_id']
assert sha(emitted/'solution')==extract['elf_sha256']==build['elf_sha256']=='9efaeb73cd89e56187e47daaa763684faf1572c89fb750eb983972fd440f7eb6'
assert sha(emitted/'disassembly.txt')==extract['disassembly_sha256']=='7af8bca730f57270877e8a0013eb66964a515f59ddd25ca957eb1e00e77a716b'
assert extract['image_id']==build['image_id']=='sha256:a7539af57e13740cfa13cc7c5a6f44bdd2204016e101e3e43425c256229a69c5'
b=(emitted/'solution').read_bytes();h=struct.unpack_from('<16sHHIQQQIHHHHHH',b);assert h[0][:6]==b'\x7fELF\x02\x01' and h[2]==62
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
 if s[1]!=4:continue
 for off in range(s[4],s[4]+s[5],s[9]):
  addr,info,addend=struct.unpack_from('<QQq',b,off)
  if info&0xffffffff==37:relocations[addr]={'section':name,'kind':37,'resolver':hex(addend),'symbols':symbols.get(addend,[])}
plt=byname['.plt'];stubs={}
for delta in range(plt[5]-5):
 off=plt[4]+delta
 if b[off:off+2]!=b'\xff\x25':continue
 addr=plt[3]+delta;got=addr+6+struct.unpack_from('<i',b,off+2)[0]
 if got in relocations:stubs[addr]={'stub_address':hex(addr),'got_address':hex(got),'relocation':relocations[got]}
loads=[struct.unpack_from('<IIQQQQQQ',b,h[5]+i*h[9]) for i in range(h[10])];loads=[p for p in loads if p[0]==1]
def bytes_at(addr,n):
 for p in loads:
  if p[3]<=addr and addr+n<=p[3]+p[5]:return b[p[2]+addr-p[3]:p[2]+addr-p[3]+n]
 raise AssertionError(('unmapped',hex(addr)))
def aliases(rel):return '/'.join(sorted(set(s['name'] for s in rel['symbols'] if s['type']==10))) or 'unresolved_IFUNC'
fn='';narrow_functions=set();direct_plt=[];got_ifunc=[];other_indirect=[];other_direct=[]
for line in (emitted/'disassembly.txt').read_text().splitlines():
 header=re.match(r'^([0-9a-f]+) <(.*)>:$',line)
 if header:fn=header[2]
 narrow=(fn.startswith('main::') and 'operator()<unsigned char>' in fn and 'operator()(unsigned int)' in fn and '.cold' not in fn)
 if not narrow:continue
 narrow_functions.add(fn)
 direct=re.match(r'^\s*([0-9a-f]+):\s+(?:addr32\s+)?call\s+([0-9a-f]+)(?:\s|$)(.*)',line)
 if direct:
  addr,target=int(direct[1],16),int(direct[2],16)
  if target in stubs:
   code=bytes_at(addr,6);start=1 if code[0]==0x67 else 0;assert code[start]==0xe8 and addr+start+5+struct.unpack_from('<i',code,start+1)[0]==target
   direct_plt.append({'caller':fn,'instruction':line.strip(),'call_address':hex(addr),'plt':stubs[target],'validated_machine_bytes':code[:start+5].hex()})
  else:other_direct.append(line.strip())
  continue
 indirect=re.match(r'^\s*([0-9a-f]+):\s+call\s+\*.*',line)
 if indirect:
  addr=int(indirect[1],16);code=bytes_at(addr,6)
  if code[:2]==b'\xff\x15':
   got=addr+6+struct.unpack_from('<i',code,2)[0]
   if got in relocations:
    got_ifunc.append({'caller':fn,'instruction':line.strip(),'call_address':hex(addr),'got_address':hex(got),'relocation':relocations[got],'aliases':aliases(relocations[got]),'validated_machine_bytes':code.hex()});continue
  other_indirect.append(line.strip())
assert narrow_functions
report={'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'official_score':False,'scope':'Read-only byte-validated comparison of original360 and exact once-built362 production image. No compiler/objdump/model/benchmark/training/image program/board rerun. Static sites are not dynamic frequency, cost, Intel speedup or organizer-ELF proof.','source_manifest':'.build/round362/frozen.json','source_manifest_sha256':sha(r/'.build/round362/frozen.json'),'candidate_source_sha256':frozen['source_sha256'],'source_guard_all_frozen_files_passed':True,'main_whitespace_token_equal_as_bound_in_frozen_manifest':True,'build_report_sha256':sha(r/'.build/round362/proof/build/report.json'),'extraction_report_sha256':sha(emitted/'extraction.json'),'original_report':'.build/round360/report.json','original_report_sha256':sha(r/'.build/round360/report.json'),'original_ELF_sha256':old['local_ELF_sha256'],'candidate_ELF_sha256':sha(emitted/'solution'),'candidate_disassembly_sha256':sha(emitted/'disassembly.txt'),'candidate_image_id':extract['image_id'],'original_narrow_PLT_alias_counts':old['default_narrow_PLT_alias_counts'],'candidate_narrow_functions':sorted(narrow_functions),'candidate_narrow_direct_PLT_calls':direct_plt,'candidate_narrow_GOT_IFUNC_calls':got_ifunc,'candidate_narrow_GOT_IFUNC_alias_counts':dict(Counter(x['aliases'] for x in got_ifunc)),'candidate_narrow_other_direct_calls':other_direct,'candidate_narrow_other_indirect_calls':other_indirect,'candidate_whole_ELF_PLT_stub_count':len(stubs),'interpretation':'Compare own default-narrow call sites rather than total PLT section size: prebuilt library objects are unchanged and retain their own PLT calls. Every recorded GOT IFUNC call is actual FF15 RIP-relative machine bytes targeting a known IRELATIVE slot; every remaining direct PLT call is byte-validated E8 to FF25 stub. No call frequency or score result is inferred.'}
out=w/'call-shape.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'report':str(out),'report_sha256':sha(out),'script_sha256':sha(w/'inspect.py'),'narrow_functions':len(narrow_functions),'original_narrow_PLT_alias_counts':report['original_narrow_PLT_alias_counts'],'candidate_narrow_direct_PLT_calls':len(direct_plt),'candidate_GOT_IFUNC_alias_counts':report['candidate_narrow_GOT_IFUNC_alias_counts'],'candidate_other_indirect_calls':len(other_indirect),'candidate_whole_ELF_PLT_stub_count':len(stubs)},indent=2))
