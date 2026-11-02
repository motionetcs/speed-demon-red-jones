from pathlib import Path
import datetime,difflib,hashlib,json,shutil,subprocess
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round372';assert not w.exists();w.mkdir();s=w/'source';s.mkdir()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();prior=json.loads((r/'docs/round371-final-source-match.json').read_text());bindings={x['path']:x['sha256']for x in prior['inputs']};bindings['Makefile']=prior['Makefile_sha256'];assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip()==prior['source_commit']
for p,h in bindings.items():assert sha(r/p)==h,p
shutil.copytree(r/'track-c',s/'track-c');(w/'original-retained').mkdir();shutil.copytree(r/'track-c',w/'original-retained/track-c')
p=s/'track-c/names.hpp';old=p.read_text();new=old.replace('std::vector<Entry> entries;','std::vector<Entry> entries,recent;').replace(':entries(16384),words(',':entries(16384),recent(8192),words(')
start=new.index('    bool first(std::string_view key,size_t country,uint64_t hash){');end=new.index('\n};\nstruct NameEvent',start)
replacement='''    bool first(std::string_view key,size_t country,uint64_t hash){
        uint32_t fingerprint=static_cast<uint32_t>(hash);
        // This owner-private hint stores only stable arena indices, never answers.
        // Growth relocates the primary entries but does not move stored keys.
        auto& hint=recent[(hash>>2)&(recent.size()-1)];
        uint32_t index=hint.index;
        if(!index||hint.hash!=fingerprint||bytes(index)!=key){
            size_t i=fingerprint&(entries.size()-1);
            for(;;){
                auto& e=entries[i];
                if(!e.index){
                    if(used>=entries.size()*7/8){grow();i=fingerprint&(entries.size()-1);continue;}
                    uint32_t created=make(key);e={fingerprint,created};++used;break;
                }
                if(e.hash==fingerprint&&bytes(e.index)==key)break;
                i=(i+1)&(entries.size()-1);
            }
            index=entries[i].index;hint={fingerprint,index};
        }
        auto& bits=at(index)[1+country/64];uint64_t bit=uint64_t(1)<<(country%64);
        bool fresh=!(bits&bit);bits|=bit;return fresh;
    }'''
new=new[:start]+replacement+new[end:];assert new!=old and 'recent(8192)'in new;p.write_text(new);(w/'names.hpp.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/track-c/names.hpp',tofile='b/track-c/names.hpp')))
p=s/'track-c/main.cpp';old=p.read_text();new=old.replace('if(finished[reader])continue;auto& queue=queues[size_t(reader)*owners+owner];','if(finished[reader])continue;\n                                auto& queue=queues[size_t(reader)*owners+owner];').replace('if(!queue.ready.load(std::memory_order_acquire))continue;progress=true;','if(!queue.ready.load(std::memory_order_acquire))continue;\n                                progress=true;');assert new!=old;p.write_text(new);(w/'main.cpp.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/track-c/main.cpp',tofile='b/track-c/main.cpp')))
p=s/'track-c/README.md';old=p.read_text();new=old+'\n\nEach owner keeps an8192-entry lookup hint table of fingerprint and stable arena index. A hint must match the entire key before it can skip primary probing. Misses use the original authoritative table, whose growth does not change arena indices. Country membership is still computed and updated on every row; the hints contain no stored answers or data from earlier runs.\n';p.write_text(new);(w/'README.md.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/track-c/README.md',tofile='b/track-c/README.md')))
scope='C372 owner-private8192x8B stable-index lookup hints in current8B-primary Names: existing32-bit fingerprint plus full key length/everybyte required on a hit; miss exact original authoritative probing/grow. Arena indices remain stable across primarytable grow/storage vector relocation; hints never hold entry refs or caller pointers. Exact original per-country first bit evaluated/updated on every event, not cached output, seed recognition or persistent data. Fixed hint payload65536B/owner (262144B at default4owners), not a measured RSS/cgroup gain. Main only2 legacy GCC-Werror clause line breaks; original C175 decoded/raw parser, NameEvent32B/queue/roles/default12/ISA/allowed PGO untouched. A178/D334 unchanged. Need independent collision/zero1/growth/hint eviction/owned stablekeys/long/binary/country/all-topology/cache-miss/cancel models and current strict/race/GNU/image/default/source/real proof if native screen supports gain.'
pre={'created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_parent':prior['source_commit'],'official_score':False,'selected_in_root':False,'scope':scope,'source_sha256':{str(p.relative_to(s)):sha(p)for p in(s/'track-c').iterdir()if p.is_file()},'root_selected_bindings':bindings,'control_binary':str(r/'.build/round263/final-make/track-c'),'control_binary_sha256':sha(r/'.build/round263/final-make/track-c'),'duplicate_review':'Own C PERF/index/patch search:75/170/340 prefetch/interleaved owner probes,128/140/163/204/280 primary placement/grouping,104/202 eventlayout,89/315 shared-table and320 RMWguard. No prior separate fixed owner-private stable-index lookup hint front-end found. PriorA endpointcaches are different authoritative storage/key domains. No old proof transferred.','primary_concepts':[{'url':'https://abseil.io/about/design/swisstables','scope':'Hash metadata filters require exact equality; no Swiss/competitor code copied, no grouped table implementation selected.'},{'url':'https://eel.is/c++draft/vector.capacity','scope':'Vector reallocation invalidates vector element refs. Hints store indices to separately owned stable key blocks, not refs into rehashed entry vector or moved unique_ptr vector elements.'}],'current_model_provenance':'Original C queue/parser evidence retained only by exact original source/token identity; new Names first/cache path requires new source-specific proofs, not prior-source relabel.'}
(w/'preflight.json').write_text(json.dumps(pre,indent=2)+'\n');shutil.copyfile(Path(__file__),w/'prepare.py');screen=(r/'.build/round370/screen.py').read_text().replace('370','372').replace('rawcanonical/count-only field API','owner-private stable-index hint');compile(screen,'screen372.py','exec');(w/'screen.py').write_text(screen)
note=scope+' Isolated one native compile/public1/6/12/4full13-pair screen next under inherited exclusive lock; selected root371 all30 untouched. No board request, generator/oracle/profile/PGO/new model yet. Do not duplicate work; other authorized chat CPU HOLD. Canonical source and totalK unmeasured.'
(w/'ACTIVE.json').write_text(json.dumps({'status':'native_screen_prepared','selected_in_root':False,'note':note},indent=2)+'\n');p=r/'docs/STATE.md';p.write_text('# Active isolated C372 lookup-hint screen; original371 selected\n\n'+note+'\n\n'+p.read_text());print('PREPARED372 isolated stable-index hint table; root source30 unchanged',flush=True)
