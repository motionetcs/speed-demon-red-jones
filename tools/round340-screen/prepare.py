from pathlib import Path
import datetime,difflib,hashlib,json,shutil,subprocess
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round340';assert not w.exists();w.mkdir();s=w/'source';s.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
root=json.loads((r/'docs/round334-final-source-match.json').read_text());bindings={row['path']:row['sha256'] for row in root['inputs']};bindings['Makefile']=root['Makefile_sha256'];assert root['passed'] and root['actual_all_gates_passed']
for p,h in bindings.items():assert sha(r/p)==h,p
for track in 'acd':shutil.copytree(r/f'track-{track}',s/f'track-{track}')
shutil.copy2(r/'Makefile',s/'Makefile');patches={}
method='''    // One owner interleaves complete private lookups; every grow restarts pending probes.
    template<class Event> void consume(const Event* events,size_t count,uint64_t* totals){
        struct Lane{std::string_view key;size_t country=0,slot=0;uint32_t fingerprint=0,index=0;unsigned phase=0;};
        std::array<Lane,4> lanes{};size_t next_event=0,active=0;
        auto finish=[&](Lane& lane,uint32_t index){
            auto& bits=at(index)[1+lane.country/64];uint64_t bit=uint64_t(1)<<(lane.country%64);
            totals[lane.country]+=!(bits&bit);bits|=bit;lane.phase=0;--active;
        };
        while(next_event<count||active){
            for(auto& lane:lanes)if(!lane.phase&&next_event<count){
                const auto& event=events[next_event++];lane.key=event.value();lane.country=event.country;
                lane.fingerprint=static_cast<uint32_t>(event.hash);lane.slot=lane.fingerprint&(entries.size()-1);
                lane.phase=1;++active;__builtin_prefetch(&entries[lane.slot],0,1);
            }
            for(auto& lane:lanes){
                if(lane.phase==1){
                    auto& entry=entries[lane.slot];
                    if(!entry.index){
                        if(used>=entries.size()*7/8){
                            grow();
                            for(auto& pending:lanes)if(pending.phase){
                                pending.slot=pending.fingerprint&(entries.size()-1);pending.phase=1;
                                __builtin_prefetch(&entries[pending.slot],0,1);
                            }
                            break;
                        }
                        uint32_t index=make(lane.key);entry={lane.fingerprint,index};++used;finish(lane,index);
                    }else if(entry.hash==lane.fingerprint){
                        lane.index=entry.index;lane.phase=2;__builtin_prefetch(at(lane.index),0,1);
                    }else{
                        lane.slot=(lane.slot+1)&(entries.size()-1);__builtin_prefetch(&entries[lane.slot],0,1);
                    }
                }else if(lane.phase==2){
                    if(bytes(lane.index)==lane.key)finish(lane,lane.index);
                    else{
                        lane.slot=(lane.slot+1)&(entries.size()-1);lane.phase=1;
                        __builtin_prefetch(&entries[lane.slot],0,1);
                    }
                }
            }
        }
    }
'''
p=s/'track-c/names.hpp';old=p.read_text();new=old.replace('#include <algorithm>','#include <algorithm>\n#include <array>');at=new.index('\n};\nstruct NameEvent');new=new[:at]+'\n'+method+new[at:];assert new.count('void consume(')==1;p.write_text(new);patches['names.hpp']=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/track-c/names.hpp',tofile='b/track-c/names.hpp'))
p=s/'track-c/main.cpp';old=p.read_text();before='else for(const auto& e:queue.rows)distinct[owner][e.country]+=names.first(e.value(),e.country,e.hash);';after='else names.consume(queue.rows.data(),queue.rows.size(),distinct[owner].data());';assert old.count(before)==1;new=old.replace(before,after);p.write_text(new);patches['main.cpp']=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/track-c/main.cpp',tofile='b/track-c/main.cpp'))
for name,patch in patches.items():(w/(name+'.patch')).write_text(patch)
pre={'created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_parent':subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip(),'official_score':False,'selected_in_root':False,'scope':'C340 owner-private four-lane lookup states: independently refill inactive lane, probe full original32-bit rejection fingerprint, separately prefetch and compare complete stable owned key/header, then exact original country-bit/add0or1 counter update. Empty-cell insertion/growth/owned arena original; any grow resets ALL active probe/compare lanes to new full-fingerprint home before further use. No entry reference across a grow, no new shared table/atomics, table slots and full keys stay authoritative. Every512-event queue batch fully drains before unchanged clear/releasefalse; EOF/roles12/allcountry/serialfirst/CSV/route/PGO/flags/defaults unchanged. Dynamically interleaves probe/key stalls; not just prefetched hints followed by original sequential first() calls. No catalogue/seed/cached answer/harness/host/counter/source-exemption change. Fresh event permutation/duplicates/same-low32/grow-between-phases/restart/long/guard/private-lifetime/country/currentmain strict/race/untrained/GCC/image/default/Make proof required if screen supports.','source_sha256':{str(q.relative_to(s)):sha(q) for q in sorted((s/'track-c').iterdir()) if q.is_file()},'control_binary':str(r/'.build/round263/final-make/track-c'),'control_binary_sha256':sha(r/'.build/round263/final-make/track-c'),'root_main_sha256':sha(r/'track-c/main.cpp'),'root_names_sha256':sha(r/'track-c/names.hpp'),'root_selected_bindings':bindings,'duplicate_check':'75 prefetched table/key/country for16 events then called original full first() sequentially and lost actual on old16-byte owner entries.340 explicitly retains/refills four independent probe/payload states and restarts all pending phases across growth on current8-byte owner entries; differs from a fixed prefetch batch. D284 interleaved independent graph query contexts and was rejected; no graph work/proof transferred. No prior C multi-phase private lookup state machine found in own PERF. 338 conditional counter rejected;340 retains original unconditional counter add bool and bitmap OR.','primary_concepts':['https://www.research.ed.ac.uk/en/publications/asynchronous-memory-access-chaining/'],'primary_scope':'Author/institution primary abstract on per-lookup state and independent refilling for irregular pointer chains; no paper/library implementation copied, no published performance estimate transferred. Existing exact source-bound248 profile motivates owners, not a causal cost certificate.'}
(w/'preflight.json').write_text(json.dumps(pre,indent=2)+'\n');driver=(r/'tools/round338-screen/screen.py').read_text().replace('round338','round340').replace('C338 conditional owner counter','C340 interleaved owner lookups');(w/'screen.py').write_text(driver);shutil.copy2('/private/tmp/speed-demon-prepare340.py',w/'prepare.py');print(json.dumps({'prepared':str(w),'root_unchanged':True,'candidate_names_sha256':sha(s/'track-c/names.hpp'),'candidate_main_sha256':sha(p),'method_lines':len(method.splitlines())}))
