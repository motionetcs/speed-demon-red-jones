from pathlib import Path
import datetime,hashlib,json,shlex,shutil,subprocess,xml.etree.ElementTree as ET,re
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');old=r/'.build/round346/linux-allocation';w=r/'.build/round346/linux-allocation-live';assert not w.exists();w.mkdir();w.chmod(0o777)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text())
def dump(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
previous=read(old/'report.json');assert previous['passed'];report={'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'official_score':False,'selected_in_root':False,'scope':'New live-owner allocation diagnostic resolves whether346 v1postJOIN allocator-retention savings existed while name payloads were stillLIVE. Same two v1source snapshots get serialized read-only malloc_info immediately BEFORE each owner Names destructor, plus original region/joined snapshots. One new GCCcompile/source each, no originalsuccessful diagnostic repeated. No production runtime/image/header modification, no training, sanitizers, benchmark, counter/tunable/host/harness manipulation. Snapshot serialization perturbs scheduling; sampled allocator state is NOT processpeak/cgroupchargedM or precisecausal timing. Need actualvalidated image/board before scoreclaim.','previous_diagnostic_sha256':sha(old/'report.json'),'sources':[],'cases':[x for x in previous['cases'] if x['track']=='c'],'primary_source':'https://man7.org/linux/man-pages/man3/malloc_info.3.html'}
for variant in ['control','candidate']:
 folder=w/variant/'track-c';folder.parent.mkdir();shutil.copytree(old/f'c-{variant}/track-c',folder);p=folder/'main.cpp';base=p.read_text();new=base.replace('#include <malloc.h>','#include <malloc.h>\n#include <mutex>').replace('static void allocation_snapshot(const char* label){','static std::mutex allocation_diagnostic_mutex;\nstatic void allocation_snapshot(const char* label){\n    std::lock_guard guard(allocation_diagnostic_mutex);')
 before='''                            if(!progress)std::this_thread::yield();
                        }
                    }
                }catch''';after='''                            if(!progress)std::this_thread::yield();
                        }
                        allocation_snapshot("owner_done");
                    }
                }catch''';assert new.count(before)==1;new=new.replace(before,after);p.write_text(new);report['sources'].append({'variant':variant,'v1instrumented_main_sha256':hashlib.sha256(base.encode()).hexdigest(),'live_instrumented_main_sha256':sha(p),'files_sha256':{str(q.relative_to(w)):sha(q) for q in folder.iterdir() if q.is_file()},'scope':'Only additional mutex serialization and owner-before-destruction diagnostics; original andcandidate algorithms unchanged from frozen345/346sources.'})
script=['set -eu','mkdir -p /out/stdio','getconf GNU_LIBC_VERSION >/out/glibc.txt']
for variant in ['control','candidate']:
 source='/repo/'+str((w/variant/'track-c/main.cpp').relative_to(r));script+=['g++ -std=c++20 -O3 -DNDEBUG -pthread -static -march=native '+shlex.quote(source)+' -o /out/'+variant+'-bin','sha256sum /out/'+variant+'-bin >/out/'+variant+'-bin.sha256']
for n,case in enumerate(report['cases']):
 for variant in ['control','candidate']:
  name=f'{n}-{variant}';script+=['SPEED_DEMON_THREADS=12 /out/'+variant+'-bin --data '+shlex.quote('/repo/'+case['data_folder'])+' --out /out/'+name+' >/out/stdio/'+name+'.out 2>/out/stdio/'+name+'.err']
compiler=previous['compiler_image'];argv=['docker','run','--rm','--pull=never','--platform','linux/amd64','--network=none','--read-only','--memory=8g','--memory-swap=8g','--pids-limit=512','--cap-drop=ALL','--security-opt=no-new-privileges','--user','65534:65534','--tmpfs','/tmp:rw,exec,size=1g','-i','-v',str(r)+':/repo:ro','-v',str(w)+':/out:rw',compiler,'/bin/sh','-s'];report['command']={'argv':argv,'stdin':'\n'.join(script)+'\n'};dump(w/'partial.json',report);q=subprocess.run(argv,input='\n'.join(script)+'\n',capture_output=True,text=True,timeout=900);(w/'driver.stdout').write_text(q.stdout);(w/'driver.stderr').write_text(q.stderr);report['returncode']=q.returncode;dump(w/'partial.json',report);assert q.returncode==0 and not q.stderr,(q.returncode,q.stdout[-1500:],q.stderr[-1500:]);report['runs']=[]
for n,case in enumerate(report['cases']):
 for variant in ['control','candidate']:
  name=f'{n}-{variant}';out=w/name;assert [p.name for p in out.iterdir()]==['aggregates.txt'] and sha(out/'aggregates.txt')==case['expected_sha256'];assert not (w/'stdio'/(name+'.out')).read_bytes();text=(w/'stdio'/(name+'.err')).read_text();parts=re.findall(r'SDALLOC ([a-z_]+)\n(.*?)SDALLOC_END\n',text,re.S);assert len(parts)==6 and [p[0] for p in parts].count('owner_done')==4;states=[]
  for phase,xml in parts:
   x=ET.fromstring(xml);get=lambda tag,kind:int(next(e for e in x.findall(tag) if e.get('type')==kind).get('size'));states.append({'phase':phase,'heap_count':len(x.findall('heap')),'allocator_system_current_bytes':get('system','current'),'allocator_system_max_bytes':get('system','max'),'allocator_mmap_bytes':get('total','mmap'),'allocator_current_brk_plus_mmap_bytes':get('system','current')+get('total','mmap')})
  live=max(x['allocator_current_brk_plus_mmap_bytes'] for x in states if x['phase']=='owner_done');report['runs'].append({'case':case['case'],'variant':variant,'states':states,'max_sampled_live_owner_allocator_current_bytes':live,'sha256':sha(out/'aggregates.txt'),'binary_sha256':sha(w/(variant+'-bin')),'stderr_XML_sha256':sha(w/'stdio'/(name+'.err'))})
for row in report['sources']:
 for p,h in row['files_sha256'].items():assert sha(w/p)==h,p
for case in report['cases']:assert {p.name:sha(p) for p in (r/case['data_folder']).iterdir() if p.is_file()}==case['inputs_sha256']
comparisons=[]
for case in report['cases']:
 pair={x['variant']:x for x in report['runs'] if x['case']==case['case']};comparisons.append({'case':case['case'],'sampled_live_allocator_candidate_minus_control_bytes':pair['candidate']['max_sampled_live_owner_allocator_current_bytes']-pair['control']['max_sampled_live_owner_allocator_current_bytes'],'control':pair['control']['max_sampled_live_owner_allocator_current_bytes'],'candidate':pair['candidate']['max_sampled_live_owner_allocator_current_bytes'],'scope':'Sampled allocator bytes withpayloadstillalive, NOT actualpeak or chargedM; compareseparately withv1postjoinretention.'})
report.update(passed=True,completed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),comparison=comparisons,glibc=(w/'glibc.txt').read_text().strip());dump(w/'report.json',report);print('PASS346 live-owner allocation diagnostic',json.dumps(comparisons),flush=True)
