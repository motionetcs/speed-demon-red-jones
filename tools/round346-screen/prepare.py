from pathlib import Path
import datetime,difflib,hashlib,json,shutil,subprocess
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round346';assert not w.exists();w.mkdir();s=w/'source';s.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
proof=json.loads((r/'docs/round344-final-source-match.json').read_text());assert proof['passed'] and proof['actual_all_gates_passed'];bindings={row['path']:row['sha256'] for row in proof['inputs']};bindings['Makefile']=proof['Makefile_sha256']
for p,h in bindings.items():assert sha(r/p)==h,p
for t in 'acd':shutil.copytree(r/f'track-{t}',s/f'track-{t}')
shutil.copy2(r/'Makefile',s/'Makefile');p=s/'track-c/main.cpp';old=p.read_text()
helper='''// Start with exact byte country codes; promote once when a real code needs more bits.
struct RegionLookup {
    std::vector<uint8_t> narrow=std::vector<uint8_t>(1000000,UINT8_MAX);
    std::vector<uint16_t> wide;
    void set(uint64_t id,uint16_t country){
        if(id>=SIZE_MAX)throw std::runtime_error("region index capacity");
        if(!narrow.empty()&&country<UINT8_MAX){
            if(id>=narrow.size())narrow.resize(static_cast<size_t>(id)+1,UINT8_MAX);
            narrow[static_cast<size_t>(id)]=static_cast<uint8_t>(country);
        }else{
            if(!narrow.empty()){
                wide.assign(narrow.begin(),narrow.end());
                std::replace(wide.begin(),wide.end(),uint16_t(UINT8_MAX),uint16_t(UINT16_MAX));
                std::vector<uint8_t>().swap(narrow);
            }
            if(id>=wide.size())wide.resize(static_cast<size_t>(id)+1,UINT16_MAX);
            wide[static_cast<size_t>(id)]=country;
        }
    }
};

'''
new=old.replace('struct Field {',helper+'struct Field {').replace('std::vector<uint16_t> lookup(1000000, missing);','RegionLookup lookup;')
before='''            if (id >= lookup.size()) lookup.resize(id + 1, missing);
            lookup[id] = dense;''';assert before in new;new=new.replace(before,'            lookup.set(id,dense);')
before='''        std::vector<uint8_t> narrow_lookup;
        if (unmatched <= UINT8_MAX) {
            narrow_lookup.assign(lookup.begin(), lookup.end());
            std::vector<uint16_t>().swap(lookup);
        }
''';assert before in new;new=new.replace(before,'').replace('if(narrow_lookup.empty())consume(lookup);else consume(narrow_lookup);','if(lookup.narrow.empty())consume(lookup.wide);else consume(lookup.narrow);');assert 'narrow_lookup' not in new and 'RegionLookup lookup;' in new;p.write_text(new);patch=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/track-c/main.cpp',tofile='b/track-c/main.cpp'));(w/'main.cpp.patch').write_text(patch)
pre={'created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_parent':subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip(),'official_score':False,'selected_in_root':False,'scope':'C346 dense region lookup starts at existing uint8 width and promotes ONCE to fulluint16 only when actual dense country code>=255. On promotion map every old missing255 to missing65535 BEFORE writing newlyvalid255, preserve all old codes/holes, original duplicate-ID lastwrite/order semantics and arbitrary indexgrowth; guard unrepresentableSIZE_MAX. Ordinary<=255-country inputs avoid original2MB uint16 map plus conversion into1MB map. Final record lookup/type dispatch, original data grammar/parser/names/queues/roles/default12/PGO/flags unchanged. No rank bitmap/per-record extra loads, country/domain narrowing, catalogue/seed/cached output/allocator tunable/env/host/timer/harness/counter/exemption change. Allocation-lifetime/defaultglibc-pattern hypothesis only, not measured chargedM or guaranteed dynamicthreshold behavior. Fresh actual RegionLookup vsindependent map/word/allcountry255/256/overwrites/holes/largeid/overflow/guard/exception/narrowwide/lifetime/currentmain strict/race/untrained/GCC/image/default/Make proof required if screen supports.','source_sha256':{str(p.relative_to(s)):sha(p) for p in sorted((s/'track-c').iterdir()) if p.is_file()},'control_binary':str(r/'.build/round263/final-make/track-c'),'control_binary_sha256':sha(r/'.build/round263/final-make/track-c'),'root_main_sha256':sha(r/'track-c/main.cpp'),'root_names_sha256':sha(r/'track-c/names.hpp'),'root_selected_bindings':bindings,'duplicate_check':'24 selected narrowlookup builds uint16 first then copies tobyte map;346 reverses construction with guarded fullwidth promotion, final lookup same.341 ranked-region bitmap changed per-recordlookup and lost;346 is dense and no popcount.198/335/329 changed NAME payload, not region map. Own PERF contains no narrow-first region construction/promotion trial. Notcombined345 mappedA cache or anyrejected code.','primary_concepts':['https://sourceware.org/glibc/manual/latest/html_node/Malloc-Tunable-Parameters.html'],'primary_scope':'Primaryglibc defaultmmapthreshold adapts to allocation patterns and mmap canfree storage; no mallopt/environment/control or current-glibc instrumentation changed. Actual memory/totalK must be measured on board. Independent event-written code only.'}
(w/'preflight.json').write_text(json.dumps(pre,indent=2)+'\n');driver=(r/'tools/round338-screen/screen.py').read_text().replace('round338','round346').replace('C338 conditional owner counter','C346 narrow-first region construction');(w/'screen.py').write_text(driver);shutil.copy2('/private/tmp/speed-demon-prepare346.py',w/'prepare.py');print(json.dumps({'prepared':str(w),'root_unchanged':True,'main_sha256':sha(p),'helper_lines':len(helper.splitlines())}))
