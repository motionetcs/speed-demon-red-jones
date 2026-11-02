from pathlib import Path
import datetime, difflib, hashlib, json, shutil, subprocess
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh'); w=r/'.build/round393'; s=w/'source'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
read=lambda p:json.loads(Path(p).read_text())
parent=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip()
assert parent=='9a1dbc4b00846389bbba70d80c976a2407a70b54'
assert read(r/'docs/round392-final-source-match.json')['actual_all_gates_passed']
assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,11,2,14,tzinfo=datetime.timezone.utc)
assert not w.exists();w.mkdir();s.mkdir();shutil.copytree(r/'track-c',s/'track-c')
proof=read(r/'docs/round392-final-source-match.json');bindings={x['path']:x['sha256']for x in proof['inputs']};bindings['Makefile']=proof['Makefile_sha256']
assert all(sha(r/p)==h for p,h in bindings.items())
p=s/'track-c/names.hpp';old=p.read_text();new=old.replace('#include <algorithm>','#include <algorithm>\n#include <bit>');assert new!=old
a='''    bool first(std::string_view key,size_t country,uint64_t hash){'''
b='''    void add_counts(std::vector<uint64_t>& counts)const{
        for(const auto& e:entries)if(e.index){
            auto* membership=at(e.index)+1;
            for(size_t word=0;word<words;++word)
                for(uint64_t bits=membership[word];bits;bits&=bits-1)
                    ++counts[word*64+std::countr_zero(bits)];
        }
    }
    bool first(std::string_view key,size_t country,uint64_t hash){'''
assert new.count(a)==1;new=new.replace(a,b);p.write_text(new)
(w/'names.hpp.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/track-c/names.hpp',tofile='b/track-c/names.hpp')))
p=s/'track-c/main.cpp';old=p.read_text();new=old
a='else for(const auto& e:queue.rows)distinct[owner][e.country]+=names.first(e.value(),e.country,e.hash);'
b='else for(const auto& e:queue.rows)names.first(e.value(),e.country,e.hash);'
assert new.count(a)==1;new=new.replace(a,b)
a='''                            if(!progress)std::this_thread::yield();
                        }
                    }
                }catch(...)'''
b='''                            if(!progress)std::this_thread::yield();
                        }
                        names.add_counts(distinct[owner]);
                    }
                }catch(...)'''
assert new.count(a)==1;new=new.replace(a,b);p.write_text(new)
(w/'main.cpp.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/track-c/main.cpp',tofile='b/track-c/main.cpp')))
p=s/'track-c/README.md';old=p.read_text();new=old+'\n\nOwner workers update their exact per-name country bitmaps for every event, then materialize per-country distinct counts once after all of their reader queues end. Set-bit iteration uses the full dynamic country width and every exact stored name. The single-worker path retains immediate counting; the original canonical keys, private hash owners and SPSC protocol are unchanged.\n';p.write_text(new)
(w/'README.md.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/track-c/README.md',tofile='b/track-c/README.md')))
scope='C393 owner-private deferred distinct-count materialization. Original Names::first full-key/table/arena/country-bit update unchanged; owner ignores its bool return on each event and after all reader EOFs traverses its occupied entries and complete dynamic membership words, removing each nonzero lowest set bit to increment the corresponding distinct country once. Main serial owners0 path still immediate original first-return count. No new input-domain/group-count/key bound, no fixed words, no destructive bitmap scan, no cross-owner merge, no protocol/queue/batch/thread/hash/parser/ISA/PGO/default/host change. Potential benefit removes per-row distinct-array load/add/store and dead first-return extraction; cost adds final table/word/setbit scan. Work depends on actual unique names/memberships, not seed recognition. No native/target gain assumed. Before promotion requires new extracted padding-zero/last-word/collision/empty/grow/index/stdset/allwidth/guard/privateowner/count conservation, main strict/race/independent/adversarial/untrained/GNU/image/true-default/rootMake/real proof.'
pre={'created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_parent':parent,'official_score':False,'selected_in_root':False,'scope':scope,'source_sha256':{str(p.relative_to(s)):sha(p)for p in(s/'track-c').iterdir()if p.is_file()},'root_selected_bindings':bindings,'control_binary':str(r/'.build/round263/final-make/track-c'),'control_binary_sha256':sha(r/'.build/round263/final-make/track-c'),'duplicate_review':'Own all C PERF and prototype patches searched before code.338 conditional per-row counter is exact duplicate of first considered if(first) idea; stopped before implementation/compile. Old round2 private-membership prototype does deferred set-bit reduction BUT uses shared concurrent names, thread-private sparse membership and a postjoin cross-thread union/fourword width, with slower native result.393 instead traverses existing current owner-private exact offset arena with no added private memberships/merge/allocation/fixed4-width. This is an explicit materially new-layout retest, not invented novelty or reused old proof. No current private-owner post-EOF materialization found.','primary_sources':[{'url':'https://timsong-cpp.github.io/cppwp/n4861/bit.count','scope':'C++20 unsigned countr_zero least-significant zero count, used ONLY on nonzero local copy. Conceptual primary standard semantics, no implementation imported.'}],'frozen_spec':{'path':'tools/official/specs/c-join.md','sha256':sha(r/'tools/official/specs/c-join.md'),'scope':'Section3 exact byte-string names_distinct per actual joined country; every supported country width and empty group behavior preserved.'},'old_proof_scope':'Unchanged primitive source provenance is not a certificate for new reduction/read lifetime/padding/count arithmetic. No new proof yet.'}
(w/'preflight.json').write_text(json.dumps(pre,indent=2)+'\n');shutil.copy2(Path(__file__),w/'prepare.py')
script=(r/'.build/round390/screen.py').read_text().replace('390','393').replace('main-owned preallocated vector buffers','owner-private deferred bitmap counting');compile(script,'screen393.py','exec');(w/'screen.py').write_text(script)
(w/'ACTIVE.json').write_text(json.dumps({'status':'native_screen_prepared','selected_in_root':False,'scope':scope},indent=2)+'\n')
p=r/'docs/STATE.md';p.write_text('# Active isolated C393 deferred owner counts; selected392 real-confirmed unchanged\n\n'+scope+' One compile and sequential public1/6/12/fourfull13pairs next under shared lock. No selected runtime/Git/image/board change; no other active job. Snapshot .build/round393/source, exact preflight/patches. Stop risky starts14:00 and runtime/commits/pushes15:00UTC; publication onlyapproved15:00–16:00 after frozen passing preservation/finalreview.\n\n'+p.read_text())
print('PREPARED393 isolated current owner-private post-EOF counts; selected392 unchanged',flush=True)
