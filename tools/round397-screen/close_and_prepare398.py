from pathlib import Path
import datetime,difflib,hashlib,json,shutil,subprocess,tempfile
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();read=lambda p:json.loads(Path(p).read_text())
def dump(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
prior=read(r/'docs/round396-final-source-match.json');parent=prior['source_commit'];assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip()==parent
w=r/'.build/round397';pre=read(w/'preflight.json');rep=read(w/'confirmation/report.json');assert rep['passed']and len(rep['runs'])==90;assert all(sha(r/p)==h for p,h in pre['root_selected_bindings'].items());a=r/'tools/round397-screen';assert not a.exists();a.mkdir()
for name,src in[('prepare.py',w/'prepare.py'),('screen.py',w/'screen.py'),('close_and_prepare398.py',Path(__file__)),('preflight.json',w/'preflight.json'),('report.json',w/'confirmation/report.json'),('compile.json',w/'compile.json'),('base-a-PERF.md',w/'source/track-a/PERF.md')]:shutil.copy2(src,a/name)
patches=[]
for p in sorted(w.glob('*.patch')):
 dest=r/('docs/prototype-patches/round397-a-single-row-'+p.name);shutil.copy2(p,dest);patches.append({'path':str(dest.relative_to(r)),'sha256':sha(dest)})
with tempfile.TemporaryDirectory(prefix='round397-reconstruct-')as tmp:
 base=Path(tmp)
 for p in pre['source_sha256']:
  dest=base/p;dest.parent.mkdir(parents=True,exist_ok=True)
  if dest.name=='PERF.md':shutil.copy2(a/'base-a-PERF.md',dest)
  else:dest.write_bytes(subprocess.check_output(['git','show',parent+':'+p],cwd=r))
 for row in patches:
  q=subprocess.run(['git','apply',str(r/row['path'])],cwd=base,capture_output=True,text=True);assert q.returncode==0,q.stderr
 assert all(sha(base/p)==h==sha(w/'source'/p)for p,h in pre['source_sha256'].items())
summary={n:{'paired_median_ratio':x['paired_median_ratio'],'paired_wins':x['paired_wins'],'native_rss_delta_bytes':x['variants']['candidate']['median_native_rss_bytes']-x['variants']['control']['median_native_rss_bytes']}for n,x in rep['summary'].items()};limits='Single-row prehash/cache hint is weak/mixed .995740/1.002450/1.005568 (8/5/6wins), near-flat RSS. REJECT before new actual-header prehash-vs-wrapper/guard/collision/long/privateowner/cancel models, main strict/race/untrained/GNU/image/default/actual proof. No target gain or general-correctness certificate is inferred; original root untouched.'
(a/'README.md').write_text('# A397: rejected after native screen\n\n'+pre['scope']+'\n\n'+limits+'\n\n'+pre['duplicate_review']+'\n');dump(r/'docs/round397-a-single-row-prefetch-screen.json',{'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'decision':'REJECT_NATIVE_ONLY','source_parent':parent,'scope':pre['scope'],'official_score':False,'selected_in_root':False,'runs':90,'summary':summary,'limitations':limits,'patches':patches,'frozen_source_sha256':pre['source_sha256'],'reconstruction_passed':True,'files':{str(p.relative_to(r)):sha(p)for p in a.iterdir()if p.is_file()}});dump(w/'ACTIVE.json',{'status':'rejected_native_only','no_active_work':True,'summary':summary,'limitations':limits});p=r/'track-a/PERF.md';p.write_text(p.read_text()+'\n\nA397 single-row prehash/cache-prefetch: REJECT_NATIVE_ONLY. '+json.dumps(summary,sort_keys=True)+'. '+limits+' Fullpublic1/6/12 and13rotating3fulls/input/output/source/ELF hashesPASS; onecompile90calls. Exact docs/round397-a-single-row-prefetch-screen.json/tools/round397-screen.\n')
# A new C architecture, isolated until every proof and a real score pass.
w=r/'.build/round398';s=w/'source';assert not w.exists();assert datetime.datetime.now(datetime.timezone.utc)<datetime.datetime(2026,11,2,14,tzinfo=datetime.timezone.utc);w.mkdir();s.mkdir();shutil.copytree(r/'track-c',s/'track-c');bindings={x['path']:x['sha256']for x in prior['inputs']};bindings['Makefile']=prior['Makefile_sha256'];assert all(sha(r/p)==h for p,h in bindings.items())
p=s/'track-c/names.hpp';old=p.read_text();new=old.replace('#include <algorithm>','#include <algorithm>\n#include <bit>');new=new.replace('size_t words,used=0,next=0,remaining=0;','size_t words,used=0,next=0,remaining=0,country_count;');a='explicit Names(size_t countries):entries(16384),words((countries+63)/64){}';b='explicit Names(size_t countries):entries(16384),words((countries+63)/64),country_count(countries){if(countries>SIZE_MAX-63)throw std::runtime_error("country width overflow");}';assert new.count(a)==1;new=new.replace(a,b)
a='size_t capacity=std::max<size_t>(8192,extra);storage.emplace_back(new uint64_t[capacity]);next=0;remaining=capacity;';b='size_t capacity=std::max<size_t>(8192,extra);std::unique_ptr<uint64_t[]> block(new uint64_t[capacity]);storage.push_back(std::move(block));next=0;remaining=capacity;';assert new.count(a)==1;new=new.replace(a,b)
a='    bool first(std::string_view key,size_t country,uint64_t hash){';b='    uint32_t intern(std::string_view key,uint64_t hash){';assert new.count(a)==1;new=new.replace(a,b)
a='''        auto& bits=at(entries[i].index)[1+country/64];uint64_t bit=uint64_t(1)<<(country%64);
        bool fresh=!(bits&bit);bits|=bit;return fresh;
    }
};''';b='''        return entries[i].index;
    }
    bool first(std::string_view key,size_t country,uint64_t hash){
        if(country>=country_count)throw std::runtime_error("country outside name table");
        auto& bits=at(intern(key,hash))[1+country/64];uint64_t bit=uint64_t(1)<<(country%64);
        bool fresh=!(bits&bit);bits|=bit;return fresh;
    }
    void merge_from(const Names& other){
        if(country_count!=other.country_count||words!=other.words)throw std::runtime_error("incompatible name country widths");
        for(const auto& e:other.entries)if(e.index){
            uint32_t index=intern(other.bytes(e.index),e.hash);
            auto* destination=at(index)+1;const auto* source=other.at(e.index)+1;
            for(size_t word=0;word<words;++word)destination[word]|=source[word];
        }
    }
    void add_counts(std::vector<uint64_t>& counts)const{
        if(counts.size()!=country_count)throw std::runtime_error("incompatible country counts");
        for(const auto& e:entries)if(e.index){
            const auto* membership=at(e.index)+1;
            for(size_t word=0;word<words;++word)for(uint64_t bits=membership[word];bits;bits&=bits-1){
                size_t country=word*64+std::countr_zero(bits);
                if(country>=counts.size())throw std::runtime_error("name membership padding set");
                ++counts[country];
            }
        }
    }
};''';assert new.count(a)==1;new=new.replace(a,b);p.write_text(new);(w/'names.hpp.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/track-c/names.hpp',tofile='b/track-c/names.hpp')))
p=s/'track-c/main.cpp';old=p.read_text();start=old.index('        unsigned threads = worker_count();');end=old.index('        std::sort(groups.begin()',start)
body='''        unsigned threads = worker_count();
        auto boundaries=record_boundaries(header.p,records.data+records.size,threads);
        struct Local{std::vector<Group> groups;std::unique_ptr<Names> names;};
        std::vector<Local> locals(threads);for(auto& local:locals)local.groups=groups;
        std::atomic<bool> canceled{false};
        auto consume=[&]<typename Code>(const std::vector<Code>& region_lookup){
            constexpr Code no_region=std::numeric_limits<Code>::max();
            parallel(threads,[&](unsigned worker){
                try{
                    auto& local=locals[worker];local.names=std::make_unique<Names>(groups.size());
                    Csv csv{boundaries[worker],boundaries[worker+1]};std::string name_scratch,unused;
                    while(csv.p<csv.end){
                        if(canceled.load(std::memory_order_relaxed))throw std::runtime_error("record parsing canceled");
                        csv.bom();uint64_t id=csv.integer();Field name=csv.field(name_scratch,false);csv.comma();
                        uint64_t hash=Names::hash_key(name.value);
                        Field note=csv.field(unused,false);csv.comma();uint64_t region=csv.integer();int64_t amount=csv.amount();csv.newline();
                        size_t country=region<region_lookup.size()&&region_lookup[region]!=no_region?region_lookup[region]:unmatched;
                        Group& group=local.groups[country];++group.count;group.ids+=static_cast<int64_t>(id);group.sum+=amount;
                        group.minimum=std::min(group.minimum,amount);group.maximum=std::max(group.maximum,amount);
                        group.name_bytes+=name.bytes;group.note_bytes+=note.bytes;
                        local.names->first(name.value,country,hash);
                    }
                }catch(...){canceled.store(true,std::memory_order_relaxed);throw;}
            });
        };
        if(narrow_lookup.empty())consume(lookup);else consume(narrow_lookup);
        auto names=std::move(locals.front().names);
        for(size_t worker=1;worker<locals.size();++worker){names->merge_from(*locals[worker].names);locals[worker].names.reset();}
        std::vector<uint64_t> distinct(groups.size());names->add_counts(distinct);
        for(const auto& local:locals)for(size_t i=0;i<groups.size();++i){auto& group=groups[i];const auto& value=local.groups[i];group.count+=value.count;group.ids+=value.ids;group.sum+=value.sum;group.minimum=std::min(group.minimum,value.minimum);group.maximum=std::max(group.maximum,value.maximum);group.names+=value.names;group.name_bytes+=value.name_bytes;group.note_bytes+=value.note_bytes;}
        for(size_t i=0;i<groups.size();++i)groups[i].names+=distinct[i];
''';new=old[:start]+body+old[end:];p.write_text(new);(w/'main.cpp.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/track-c/main.cpp',tofile='b/track-c/main.cpp')))
p=s/'track-c/README.md';old=p.read_text();new=old+'\n\nEach requested worker parses once into private ordinary aggregates and a complete private full-key/country-bitmap Names table. After all workers join, the first table receives each other table through exact key lookup and wordwise set union; each merged source table is then freed. Final distinct country counts are materialized from the union. There is no per-row queue transfer or shared mutable name dictionary. This trades duplicate temporary name storage and a serial merge for more parsing workers and less communication. Every country width and key byte remains exact.\n';p.write_text(new);(w/'README.md.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/track-c/README.md',tofile='b/track-c/README.md')))
scope='C398 fully private per-parser exact Names tables and postjoin full-key membership union. All requested1..12 workers parse one quote-safe partition with original Csv/lookup/cents/boundaries; ordinary totals stay private. Original lookup/arena/growth body factored into intern returning stable index; first still sets exactly one bit. After original jthread-based parallel returns successfully, reuse worker0 table, merge every other table by stored low32 fingerprint and FULL byte equality, OR complete dynamic country words, free source after merge, then count each set bit exactly once. Added exact country-width/count compatibility and padding guards, owned unique_ptr before storage-vector insertion prevents allocation-exception leak without zeroing key payloads. No per-row queue or shared-name writes; original unused NameEvent/NameQueue declarations remain charged, not hidden. No extra parse, offset catalogue, fixed4-width, lossyhash/equality, extra threads, ISA/PGO/default/host/seed/answer shortcut. Extra duplicated private names/allocator arenas and serial merge can lose. Needs fresh independent union/stdset/collision0/1/grow/arena/long/guard/selfmerge/width/padding/earlysourcefree/fault/lifetime/threadfailure models and main every-budget/country/adversarial/untrained/strict/race/GNU/image/default/Make/real proof before promotion; old SPSC/concurrent-shared proof is not a certificate for new design.'
pre={'created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_parent':parent,'official_score':False,'selected_in_root':False,'scope':scope,'source_sha256':{str(p.relative_to(s)):sha(p)for p in(s/'track-c').iterdir()if p.is_file()},'root_selected_bindings':bindings,'control_binary':str(r/'.build/round263/final-make/track-c'),'control_binary_sha256':sha(r/'.build/round263/final-make/track-c'),'duplicate_review':'Own whole C PERF and prototype patches searched. Old2 uses shared concurrent global names plus private membership and postjoin union, not private full-name maps. Old20 parses twice and routes all row offsets; retained67 parses once into8readers/4owners with per-row SPSC.393 post-EOF count only retains all queues/4owners; it lost.398 intentionally combines per-reader complete maps and joined union, eliminating per-row communication rather than claiming deferred counting alone wins. No fully private single-parse/postjoin whole-key-map merge found. Existing user-authorized chat does read-only duplicate/safety review, no CPU/source changes.','primary_sources':[{'url':'https://timsong-cpp.github.io/cppwp/n4861/thread.jthread.mem','scope':'Primary C++20 thread completion synchronizes with successful join return; actual helper uses jthread RAII then reads private tables. Conceptual, not full exception/race certificate.'},{'url':'https://timsong-cpp.github.io/cppwp/n4861/thread.thread.member','scope':'Primary join semantics; no OS fairness or successful launch guarantee inferred.'},{'url':'https://timsong-cpp.github.io/cppwp/n4861/bit.count','scope':'Unsigned set-bit iteration for exact membership materialization, not approximate counting.'}],'frozen_spec':{'path':'tools/official/specs/c-join.md','sha256':sha(r/'tools/official/specs/c-join.md'),'scope':'Section3 exact per-country names after full CSV decoding; canonical key injectivity/parser remain original, no narrowing.'}}
dump(w/'preflight.json',pre);shutil.copy2(Path(__file__),w/'prepare.py');screen=(r/'.build/round390/screen.py').read_text().replace('390','398').replace('main-owned preallocated vector buffers','per-parser private Names/postjoin union');compile(screen,'screen398.py','exec');(w/'screen.py').write_text(screen);dump(w/'ACTIVE.json',{'status':'native_screen_prepared','selected_in_root':False,'scope':scope});p=r/'docs/STATE.md';state=p.read_text();state=state[state.index('# Original396 real-confirmed; no active jobs'):];p.write_text('# Active isolated C398 private-parser Names/joined union screen; selected396 unchanged\n\n'+scope+' One native compile/public1/6/12/fourfull13pairs next under shared lock. A397 rejected native-only .995740/1.002450/1.005568 and fully archived; no other CPU/watcher active. Current source30/Make/root/HEAD/origin remains original passing396, PRIVATE/MIT. Do not integrate before all new source-specific proofs/actual board. New risky starts stop14:00, final evidencehead aim14:15, runtime/Git freeze15:00; publication only approved15:00–16:00 after final frozen passing/privacy review.\n\n'+state);print('ARCHIVED397 rejected; PREPARED398 private-parser maps and joined exact union, selected396 unchanged',flush=True)
