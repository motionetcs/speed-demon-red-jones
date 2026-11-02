from pathlib import Path
import datetime,hashlib,json,shlex,shutil,subprocess,xml.etree.ElementTree as ET,re
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');work=r/'.build/round346/linux-allocation';assert not work.exists();work.mkdir();work.chmod(0o777)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
compiler='gcc:15@sha256:eb5e64286ad47187b32bda75c6b6916166ecb41da56559b8b09e0001748d2cce';report={'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'official_score':False,'selected_in_root':False,'scope':'Read-only allocation-lifetime diagnostic for new345mappedcache and346narrow-first hypotheses. Two fresh instrumented-source copies pertrack, oneGCC-O3static compile each, noPGO/no sanitizers/no performance measurement or host/allocator tunable. malloc_info snapshots allarenas plus mmap at completed/joined phases only. XML allocator-ownedcurrent/max bytes are NOT process peakRSS, cgroupchargedM, dynamicthreshold value, source-specific correctness or a causal official gain. Explicit currentglibc behavior question justifies new diagnostic, not unchanged-state polling. All instrumentation stays in ignoredunscored diagnostic snapshots, never candidate/selected runtime or images.','compiler_image':compiler,'sources':[],'cases':[],'commands':[]}
helper='''static void allocation_snapshot(const char* label){
    std::fprintf(stderr,"SDALLOC %s\\n",label);
    if(malloc_info(0,stderr)!=0)throw std::runtime_error("malloc_info diagnostic failed");
    std::fprintf(stderr,"SDALLOC_END\\n");
}
'''
for number,track in [(345,'a'),(346,'c')]:
 screen=read(r/f'.build/round{number}/confirmation/report.json');assert screen['passed'];pre=read(r/f'.build/round{number}/preflight.json')
 for p,h in pre['root_selected_bindings'].items():assert sha(r/p)==h,p
 for variant,base in [('control',r/'.build/round344/submitted-source'),('candidate',r/f'.build/round{number}/source')]:
  folder=work/f'{track}-{variant}'/f'track-{track}';folder.parent.mkdir();shutil.copytree(base/f'track-{track}',folder);p=folder/'main.cpp';before=p.read_text();after='#include <malloc.h>\n'+before.replace('int main(int argc, char** argv) {',helper+'int main(int argc, char** argv) {');assert after.count('static void allocation_snapshot')==1
  if track=='a':
   a='        std::vector<std::string_view> paths(';b='        writer.finish();';assert after.count(a)==1 and after.count(b)==1;after=after.replace(a,'        allocation_snapshot("parsed");\n'+a).replace(b,'        allocation_snapshot("joined");\n'+b)
  else:
   a='        Csv header{';b='        for(const auto& local:locals)for(size_t i=0;i<groups.size();++i)';assert after.count(a)==1 and after.count(b)==1;after=after.replace(a,'        allocation_snapshot("regions");\n'+a).replace(b,'        allocation_snapshot("joined");\n'+b)
  p.write_text(after);report['sources'].append({'track':track,'variant':variant,'base_main_sha256':hashlib.sha256(before.encode()).hexdigest(),'instrumented_main_sha256':sha(p),'instrumentation_scope':'Only malloc.h, diagnostic helper and two joined/main-thread calls; no algorithm edit. Same helper/call phases for paired originals and candidates.','files_sha256':{str(q.relative_to(work)):sha(q) for q in folder.iterdir() if q.is_file()}})
 for case in screen['cases'][:2]:
  data=Path(case['data_folder']);data=data if data.is_absolute() else r/data;data.resolve().relative_to(r);inputs={p.name:sha(p) for p in data.iterdir() if p.is_file()};assert inputs==case['inputs_sha256'];report['cases'].append({'track':track,'case':case['case'],'data_folder':str(data.relative_to(r)),'inputs_sha256':inputs,'expected_sha256':case.get('reference_sha256') or case.get('expected_sha256')})
script=['set -eu','mkdir -p /out/stdio','getconf GNU_LIBC_VERSION >/out/glibc.txt','g++ --version >/out/gcc.txt']
for track in 'ac':
 for variant in ['control','candidate']:
  name=f'{track}-{variant}';source='/repo/'+str((work/name/f'track-{track}/main.cpp').relative_to(r));flags='g++ -std=c++20 -O3 -DNDEBUG -pthread -static'+(' -march=native' if track=='c' else '');script += [flags+' '+shlex.quote(source)+' -o /out/'+name+'-bin','sha256sum /out/'+name+'-bin >/out/'+name+'-bin.sha256']
for n,case in enumerate(report['cases']):
 for variant in ['control','candidate']:
  label=f'{n}-{case["track"]}-{variant}';script+=['SPEED_DEMON_THREADS=12 /out/'+case['track']+'-'+variant+'-bin --data '+shlex.quote('/repo/'+case['data_folder'])+' --out /out/'+label+' >/out/stdio/'+label+'.out 2>/out/stdio/'+label+'.err']
argv=['docker','run','--rm','--pull=never','--platform','linux/amd64','--network=none','--read-only','--memory=8g','--memory-swap=8g','--pids-limit=512','--cap-drop=ALL','--security-opt=no-new-privileges','--user','65534:65534','--tmpfs','/tmp:rw,exec,size=1g','-i','-v',str(r)+':/repo:ro','-v',str(work)+':/out:rw',compiler,'/bin/sh','-s'];report['commands'].append({'argv':argv,'stdin':'\n'.join(script)+'\n'});dump(work/'partial.json',report)
q=subprocess.run(argv,input='\n'.join(script)+'\n',capture_output=True,text=True,timeout=900);(work/'driver.stdout').write_text(q.stdout);(work/'driver.stderr').write_text(q.stderr);report['returncode']=q.returncode;dump(work/'partial.json',report);assert q.returncode==0 and not q.stderr,(q.returncode,q.stdout[-2000:],q.stderr[-2000:]);report['runs']=[]
for n,case in enumerate(report['cases']):
 for variant in ['control','candidate']:
  label=f'{n}-{case["track"]}-{variant}';dest=work/label;output='summary.txt' if case['track']=='a' else 'aggregates.txt';assert [p.name for p in dest.iterdir()]==[output];assert sha(dest/output)==case['expected_sha256'];assert not (work/'stdio'/(label+'.out')).read_bytes();text=(work/'stdio'/(label+'.err')).read_text();parts=re.findall(r'SDALLOC ([a-z_]+)\n(.*?)SDALLOC_END\n',text,re.S);assert len(parts)==2;phases={}
  for phase,xml in parts:
   x=ET.fromstring(xml);get=lambda tag,kind:int(next(el for el in x.findall(tag) if el.get('type')==kind).get('size'));phases[phase]={'heap_count':len(x.findall('heap')),'allocator_system_current_bytes':get('system','current'),'allocator_system_max_bytes':get('system','max'),'allocator_mmap_bytes':get('total','mmap'),'allocator_free_fast_bytes':get('total','fast'),'allocator_free_rest_bytes':get('total','rest')};phases[phase]['allocator_current_brk_plus_mmap_bytes']=phases[phase]['allocator_system_current_bytes']+phases[phase]['allocator_mmap_bytes']
  report['runs'].append({'track':case['track'],'case':case['case'],'variant':variant,'phases':phases,'sha256':sha(dest/output),'diagnostic_binary_sha256':sha(work/f'{case["track"]}-{variant}-bin'),'stderr_XML_sha256':sha(work/'stdio'/(label+'.err'))})
for row in report['sources']:
 for p,h in row['files_sha256'].items():assert sha(work/p)==h,p
for case in report['cases']:assert {p.name:sha(p) for p in (r/case['data_folder']).iterdir() if p.is_file()}==case['inputs_sha256']
comparison=[]
for case in report['cases']:
 pair={x['variant']:x for x in report['runs'] if x['track']==case['track'] and x['case']==case['case']};comparison.append({'track':case['track'],'case':case['case'],'phase_current_allocator_deltas':{phase:pair['candidate']['phases'][phase]['allocator_current_brk_plus_mmap_bytes']-pair['control']['phases'][phase]['allocator_current_brk_plus_mmap_bytes'] for phase in pair['control']['phases']}})
report.update(passed=True,completed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),comparison=comparison,glibc=(work/'glibc.txt').read_text().strip(),primary_sources=['https://sourceware.org/glibc/manual/latest/html_node/Malloc-Tunable-Parameters.html','https://man7.org/linux/man-pages/man3/malloc_info.3.html']);dump(work/'report.json',report);print('PASS345/346 unscored Linuxallocation diagnostic',json.dumps(comparison),flush=True)
