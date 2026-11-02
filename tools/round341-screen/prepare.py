from pathlib import Path
import datetime,difflib,hashlib,json,shutil,subprocess
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round341';assert not w.exists();w.mkdir();s=w/'source';s.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
root=json.loads((r/'docs/round334-final-source-match.json').read_text());bindings={row['path']:row['sha256'] for row in root['inputs']};bindings['Makefile']=root['Makefile_sha256'];assert root['passed'] and root['actual_all_gates_passed']
for p,h in bindings.items():assert sha(r/p)==h,p
for track in 'acd':shutil.copytree(r/f'track-{track}',s/f'track-{track}')
shutil.copy2(r/'Makefile',s/'Makefile');p=s/'track-c/main.cpp';old=p.read_text()
helper='''// Presence plus exact rank addresses only country codes actually in the lookup.
template<class Code> struct RankedRegions {
    std::vector<uint64_t> bits;std::vector<uint32_t> prefix;std::vector<Code> codes;size_t extent;
    explicit RankedRegions(const std::vector<uint16_t>& source):extent(source.size()){
        if(extent>SIZE_MAX-63)throw std::runtime_error("region bitmap size overflow");
        size_t count=static_cast<size_t>(std::count_if(source.begin(),source.end(),[](uint16_t x){return x!=UINT16_MAX;}));
        if(count>UINT32_MAX)throw std::runtime_error("region rank capacity");
        bits.resize((extent+63)/64);prefix.resize(bits.size());codes.reserve(count);
        for(size_t word=0;word<bits.size();++word){
            prefix[word]=static_cast<uint32_t>(codes.size());
            for(size_t id=word*64;id<std::min(extent,(word+1)*64);++id){
                uint16_t code=source[id];if(code==UINT16_MAX)continue;
                if(code>=std::numeric_limits<Code>::max())throw std::runtime_error("region country code width");
                bits[word]|=uint64_t(1)<<(id%64);codes.push_back(static_cast<Code>(code));
            }
        }
    }
    size_t size()const{return extent;}
    Code operator[](size_t id)const{
        uint64_t word=bits[id/64],bit=uint64_t(1)<<(id%64);
        if(!(word&bit))return std::numeric_limits<Code>::max();
        return codes[size_t(prefix[id/64])+std::popcount(word&(bit-1))];
    }
};

'''
new=old.replace('#include <numeric>','#include <numeric>\n#include <bit>\n#include <limits>').replace('struct Field {',helper+'struct Field {')
before='''        std::vector<uint8_t> narrow_lookup;
        if (unmatched <= UINT8_MAX) {
            narrow_lookup.assign(lookup.begin(), lookup.end());
            std::vector<uint16_t>().swap(lookup);
        }'''
after='''        std::unique_ptr<RankedRegions<uint8_t>> narrow_lookup;
        std::unique_ptr<RankedRegions<uint16_t>> wide_lookup;
        if(unmatched<=UINT8_MAX)narrow_lookup=std::make_unique<RankedRegions<uint8_t>>(lookup);
        else wide_lookup=std::make_unique<RankedRegions<uint16_t>>(lookup);
        std::vector<uint16_t>().swap(lookup);'''
assert before in new;new=new.replace(before,after).replace('const std::vector<Code>& region_lookup','const RankedRegions<Code>& region_lookup').replace('size_t country=region<region_lookup.size()&&region_lookup[region]!=no_region?region_lookup[region]:unmatched;','Code mapped=region<region_lookup.size()?region_lookup[region]:no_region;\n                            size_t country=mapped!=no_region?mapped:unmatched;').replace('if(narrow_lookup.empty())consume(lookup);else consume(narrow_lookup);','if(narrow_lookup)consume(*narrow_lookup);else consume(*wide_lookup);');assert 'const RankedRegions<Code>&' in new and 'if(narrow_lookup.empty())' not in new;p.write_text(new);patch=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/track-c/main.cpp',tofile='b/track-c/main.cpp'));(w/'main.cpp.patch').write_text(patch)
pre={'created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_parent':subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip(),'official_score':False,'selected_in_root':False,'scope':'C341 exact ranked region lookup: presence bit per actual original dense-map index, uint32 rank prefix per64 bits and compact8/16-bit code array in original index order; full-ID bounds/hole checks and exact popcount rank recover country. Build from existing original dense map to preserve all prior out-of-order/duplicate overwrite behavior, no catalogue/region-distribution assumption. Same narrow<=255 condition/missing sentinel and all-country16bit fallback, checked extent/count/country width; actually free original dense map before reads. Single mapped code lookup in existing consume template; original name table/queue/quotes/numeric/roles/PGO/flags/defaults unchanged. Fewer live lookup bytes at cost of build/popcount/dependent reads; native RSS is not organizer charged M. No cached output/seed/harness/host/counter/exemption changes. Fresh independent map/stdmap/everybit/seam/gap/rank0/MAX/narrowwide/duplicate/guard/lifetime/currentmain strict/race/untrained/GCC/image/default/Make proof required if native supports.','source_sha256':{str(q.relative_to(s)):sha(q) for q in sorted((s/'track-c').iterdir()) if q.is_file()},'control_binary':str(r/'.build/round263/final-make/track-c'),'control_binary_sha256':sha(r/'.build/round263/final-make/track-c'),'root_main_sha256':sha(r/'track-c/main.cpp'),'root_names_sha256':sha(r/'track-c/names.hpp'),'root_selected_bindings':bindings,'duplicate_check':'Earlier23 direct country-code map and24 narrow uint8 dense region lookup remain baseline.198 sparse NAME-country lists rejected by profile, not region map.335 compacts NAME length metadata only and rejected.341 new presence/rank region map, original owned name/country bitmap unchanged. No prior same ranked region lookup found in own PERF.','primary_concepts':['https://eel.is/c++draft/bit.count'],'primary_scope':'Standard popcount semantics and ordinary exact rank over a finite presence bitvector; independently written representation, no external library/code or performance theorem. Frozen C region/generator specs consulted; domain not narrowed.'}
(w/'preflight.json').write_text(json.dumps(pre,indent=2)+'\n');driver=(r/'tools/round338-screen/screen.py').read_text().replace('round338','round341').replace('C338 conditional owner counter','C341 ranked region lookup');(w/'screen.py').write_text(driver);shutil.copy2('/private/tmp/speed-demon-prepare341.py',w/'prepare.py');print(json.dumps({'prepared':str(w),'root_unchanged':True,'candidate_main_sha256':sha(p),'helper_lines':len(helper.splitlines())}))
