from pathlib import Path
import datetime,difflib,hashlib,json,shutil,subprocess
r=Path.cwd();w=r/'.build/round359';s=w/'source';d=w/'diagnostic-source';assert not s.exists() and not d.exists();s.mkdir();d.mkdir();shutil.copytree(r/'track-a',s/'track-a');shutil.copytree(r/'track-a',d/'track-a')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
old=(s/'track-a/endpoint_table.hpp').read_text();a=old.index('    uint16_t intern(std::string_view value){')
new=old[:a]+'''    static size_t second(uint32_t hash){
        size_t first=hash&4095,other=(hash>>12)&4095;
        return other==first?(other^1):other;
    }
    static bool matches(const Slot& cached,std::string_view value,uint32_t hash){
        return cached.id!=UINT16_MAX&&cached.hash==hash&&cached.length==value.size()&&(value.empty()||std::memcmp(cached.data,value.data(),value.size())==0);
    }
    uint16_t intern(std::string_view value){
        if(value.size()>UINT16_MAX)return shared.intern(value,std::hash<std::string_view>{}(value));
        uint32_t hash=hash_key(value);size_t first=hash&4095;
        if(matches(slots[first],value,hash))return slots[first].id;
        size_t other=second(hash);
        if(matches(slots[other],value,hash))return slots[other].id;
        uint16_t id=shared.intern(value,std::hash<std::string_view>{}(value));
        Slot pending{shared.canonical[id].data(),hash,static_cast<uint16_t>(value.size()),id};
        if(slots[first].id==UINT16_MAX){slots[first]=pending;return id;}
        if(slots[other].id==UINT16_MAX){slots[other]=pending;return id;}
        size_t current=first;
        for(unsigned step=0;step<8;++step){
            Slot evicted=slots[current];slots[current]=pending;pending=evicted;
            if(pending.id==UINT16_MAX)break;
            size_t primary=pending.hash&4095;
            current=current==primary?second(pending.hash):primary;
        }
        return id;
    }
};
static_assert(sizeof(LocalEndpoints::Slot)==16);
'''
(s/'track-a/endpoint_table.hpp').write_text(new)
(w/'endpoint_table.hpp.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/track-a/endpoint_table.hpp',tofile='b/track-a/endpoint_table.hpp')))
fields=['calls','first_hits','second_hits','short_misses','long_fallbacks','empty_misses','conflict_misses','relocation_steps','dropped_entries']
stats='struct alignas(64) CacheCounters {'+''.join('uint64_t '+name+'=0;' for name in fields)+'};\n'
transforms=[]
def instrument(text,kind):
 block=text[text.index('struct LocalEndpoints {'):]
 edits=[]
 def change(before,after):
  nonlocal block
  assert block.count(before)==1,(kind,before,block.count(before));block=block.replace(before,after);edits.append({'before':before,'after':after})
 change('    Endpoints& shared;','    CacheCounters& stats;Endpoints& shared;')
 change('explicit LocalEndpoints(Endpoints& table):shared(table){}','explicit LocalEndpoints(Endpoints& table,CacheCounters& counters):stats(counters),shared(table){}')
 change('    uint16_t intern(std::string_view value){','    uint16_t intern(std::string_view value){\n        ++stats.calls;')
 change('if(value.size()>UINT16_MAX)return shared.intern(value,std::hash<std::string_view>{}(value));','if(value.size()>UINT16_MAX){++stats.long_fallbacks;return shared.intern(value,std::hash<std::string_view>{}(value));}')
 if kind=='direct':
  change('if(cached.id!=UINT16_MAX&&cached.hash==hash&&cached.length==value.size()&&(value.empty()||std::memcmp(cached.data,value.data(),value.size())==0))return cached.id;','if(cached.id!=UINT16_MAX&&cached.hash==hash&&cached.length==value.size()&&(value.empty()||std::memcmp(cached.data,value.data(),value.size())==0)){++stats.first_hits;return cached.id;}')
  change('        uint16_t id=shared.intern(value,std::hash<std::string_view>{}(value));','        ++stats.short_misses;if(cached.id==UINT16_MAX)++stats.empty_misses;else ++stats.conflict_misses;\n        uint16_t id=shared.intern(value,std::hash<std::string_view>{}(value));')
 else:
  change('if(matches(slots[first],value,hash))return slots[first].id;','if(matches(slots[first],value,hash)){++stats.first_hits;return slots[first].id;}')
  change('if(matches(slots[other],value,hash))return slots[other].id;','if(matches(slots[other],value,hash)){++stats.second_hits;return slots[other].id;}')
  change('        uint16_t id=shared.intern(value,std::hash<std::string_view>{}(value));','        ++stats.short_misses;if(slots[first].id==UINT16_MAX||slots[other].id==UINT16_MAX)++stats.empty_misses;else ++stats.conflict_misses;\n        uint16_t id=shared.intern(value,std::hash<std::string_view>{}(value));')
  change('        for(unsigned step=0;step<8;++step){','        for(unsigned step=0;step<8;++step){\n            ++stats.relocation_steps;')
  change('        return id;\n    }','        if(pending.id!=UINT16_MAX)++stats.dropped_entries;\n        return id;\n    }')
 original_instrumented=block
 for edit in reversed(edits):
  assert block.count(edit['after'])==1;block=block.replace(edit['after'],edit['before'])
 assert block==text[text.index('struct LocalEndpoints {'):]
 renamed=original_instrumented.replace('LocalEndpoints','DirectEndpoints' if kind=='direct' else 'CuckooEndpoints')
 transforms.append({'kind':kind,'edits_in_order':edits,'reverse_edits_restore_exact_production_class':True})
 return renamed
combined=old[:old.index('struct LocalEndpoints {')]+stats+instrument(old,'direct')+'\n'+instrument(new,'cuckoo')+'''
static_assert(sizeof(DirectEndpoints::Slot)==16);
struct CompareEndpoints {
    DirectEndpoints direct;CuckooEndpoints cuckoo;
    CompareEndpoints(Endpoints& table,std::array<CacheCounters,2>& counters):direct(table,counters[0]),cuckoo(table,counters[1]){}
    uint16_t intern(std::string_view value){
        uint16_t id=direct.intern(value);
        if(cuckoo.intern(value)!=id)throw std::runtime_error("diagnostic cache ID disagreement");
        return id;
    }
};
'''
(d/'track-a/endpoint_table.hpp').write_text(combined)
p=d/'track-a/main.cpp';main=p.read_text();before='        unsigned threads = worker_count();';after=before+'\n        std::vector<std::array<CacheCounters,2>> cache_stats(threads);';assert main.count(before)==1;main=main.replace(before,after);before='            LocalEndpoints local_names(endpoints);';after='            CompareEndpoints local_names(endpoints,cache_stats[worker]);';assert main.count(before)==1;main=main.replace(before,after)
fmt='CACHE359 {"worker":%u,"variant":"%s",'+','.join('"'+f+'":%llu' for f in fields)+'}\\n'
args=','.join('static_cast<unsigned long long>(c.'+f+')' for f in fields)
log='''        for(unsigned worker=0;worker<threads;++worker)for(unsigned variant=0;variant<2;++variant){
            const auto& c=cache_stats[worker][variant];
            std::fprintf(stderr,'''+json.dumps(fmt)+''',worker,variant?"cuckoo":"direct",'''+args+''');
        }
'''
before='        std::vector<std::string_view> paths(';assert main.count(before)==1;main=main.replace(before,log+before);p.write_text(main)
(w/'diagnostic-transforms.json').write_text(json.dumps({'scope':'Unshipped paired-cache counts only; added counters reverse exactly to production class bytes before class renaming. Pure candidate contains one4096x16B table; shadow diagnostic contains both tables and reports no timing/memory gain.','transforms':transforms},indent=2)+'\n')
proof=json.loads((r/'docs/round353-final-source-match.json').read_text());bindings={x['path']:x['sha256'] for x in proof['inputs'] if x['path'].startswith('track-a/')};bindings['Makefile']=proof['Makefile_sha256']
for rel,h in bindings.items():assert sha(r/rel)==h,rel
pre={'created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_parent':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'official_score':False,'selected_in_root':False,'preparation_only':True,'scope':'A359 same4096x16B exact private front cache, second independent position from sampled32 hash high bits, full length/byte equality on both positions, bounded8-step cuckoo relocation. Displaced entries may be dropped only from optional cache; all missing/long keys still call original fullhash/fullkey shared interner, canonical publication and IDs0..4095 unchanged. No endpoint catalogue/seed/answers/host/harness/counters/exemptions/flags/PGO/default changes. Extra probes/relocation may lose; exact full-name/range/long/collision/cycle/eviction/guard/publication/lifetime/strict/race/untrained/GCC/image/default/Make/official proof needed if diagnostic/native support.','diagnostic_scope':'One unshipped paired-cache observer runs exact original/direct and exact candidate interners on identical actual per-worker parsed inputs with thread-private counters and equal-ID checks. Counters record hits/misses/conflicts/relocations only, not CPU cost or official gain. Shadow doubles cache metadata only in diagnostic, never candidate; no timing/RSS inference from it.','duplicate_check':'Own A201 bounded adjacent probes,336 single-slot second chance and348 fullhash reuse differ. Read-only PERF/profile/cache JSON and233 source search found no previous cache hit/miss/conflict count diagnostic or cuckoo relocation. No completed profile rerun.','control_binary':str(r/'.build/round263/final-make/track-a'),'control_binary_sha256':'75db96e1b101aa09555e5576b201ef5c1a365b52b51339cce5763182e4d09b27','source_sha256':{str(p.relative_to(s)):sha(p) for p in sorted((s/'track-a').iterdir()) if p.is_file()},'diagnostic_source_sha256':{str(p.relative_to(d)):sha(p) for p in sorted((d/'track-a').iterdir()) if p.is_file()},'root_selected_bindings':bindings,'binding_scope':'A runtime/build inputs and Make only; authorized unrelated C integration may advance under sole root ownership. No claim all30 composite353 inputs remain unchanged after C work.','prepare_script_sha256':sha(w/'prepare.py'),'execution_gate':'Explicit coordinated CPU lane release, inherited run_exclusive lock; diagnostic first. Production compile/screen only after diagnostic review and explicitGO.'}
assert sha(pre['control_binary'])==pre['control_binary_sha256'];(w/'preflight.json').write_text(json.dumps(pre,indent=2)+'\n')
driver=(r/'.build/round350/screen.py').read_text().replace('round350','round359').replace('A350 small-group bitonic networks','A359 two-choice cuckoo front-cache');(w/'screen.py').write_text(driver)
print(json.dumps({'prepared_only':True,'candidate_header_sha256':sha(s/'track-a/endpoint_table.hpp'),'diagnostic_header_sha256':sha(d/'track-a/endpoint_table.hpp'),'diagnostic_main_sha256':sha(d/'track-a/main.cpp'),'prepare_script_sha256':sha(w/'prepare.py'),'reverse_diagnostic_production_class_checks':True,'compiles':0,'runs':0},indent=2))
