from pathlib import Path
import datetime,difflib,hashlib,json,shutil,subprocess
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round365';assert not w.exists();w.mkdir();s=w/'source';s.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
proof=json.loads((r/'docs/round363-final-source-match.json').read_text());head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip();assert head==proof['source_commit']=='72b55e083ab3251e4687f1e03df32625bccfd6c1'
bindings={x['path']:x['sha256']for x in proof['inputs']if x['path'].startswith('track-a/')};bindings['Makefile']=proof['Makefile_sha256']
for p,h in bindings.items():assert sha(r/p)==h
shutil.copytree(r/'track-a',s/'track-a');p=s/'track-a/endpoint_table.hpp';old=p.read_text();prefix=old[:old.index('struct LocalEndpoints {')]
new=prefix+'''struct LocalEndpoints {
    struct alignas(32) Slot {
        union { const char* data=nullptr; uint64_t words[3]; };
        uint32_t hash=0;uint16_t length=0,id=UINT16_MAX;
    };
    static_assert(sizeof(Slot)==32);
    Endpoints& shared;std::vector<Slot> slots=std::vector<Slot>(4096);
    explicit LocalEndpoints(Endpoints& table):shared(table){}
    static uint32_t hash_key(std::string_view v){
        if(v.size()<4){uint32_t h=2166136261U;for(unsigned char c:v)h=(h^c)*16777619U;return h;}
        uint32_t a,b,c;std::memcpy(&a,v.data(),4);std::memcpy(&b,v.data()+(v.size()-4)/2,4);std::memcpy(&c,v.data()+v.size()-4,4);
        uint32_t h=(a^std::rotl(b,11)^std::rotl(c,23)^uint32_t(v.size()))*0x9e3779b1U;return h^(h>>16);
    }
    // Through24 bytes these samples cover the complete key. At25..28 the
    // prefix contains a,b; the full hash bijectively determines the last c4.
    static std::array<uint64_t,3> encoded(std::string_view v){
        std::array<uint64_t,3> key{};
        if(v.size()<8){uint32_t a,c;std::memcpy(&a,v.data(),4);std::memcpy(&c,v.data()+v.size()-4,4);key[0]=uint64_t(a)<<32|c;}
        else if(v.size()<=24){std::memcpy(&key[0],v.data(),8);std::memcpy(&key[1],v.data()+(v.size()-8)/2,8);std::memcpy(&key[2],v.data()+v.size()-8,8);}
        else std::memcpy(key.data(),v.data(),24);
        return key;
    }
    uint16_t intern(std::string_view value){
        if(value.size()>UINT16_MAX)return shared.intern(value,std::hash<std::string_view>{}(value));
        uint32_t hash=hash_key(value);size_t i=hash&(slots.size()-1);
        const auto& cached=slots[i];bool packed=value.size()>=4&&value.size()<=28;
        if(cached.id!=UINT16_MAX&&cached.hash==hash&&cached.length==value.size()){
            if(packed){auto key=encoded(value);if(cached.words[0]==key[0]&&cached.words[1]==key[1]&&cached.words[2]==key[2])return cached.id;}
            else if(value.empty()||std::memcmp(cached.data,value.data(),value.size())==0)return cached.id;
        }
        uint16_t id=shared.intern(value,std::hash<std::string_view>{}(value));
        if(packed){auto key=encoded(value);slots[i]=Slot{.words={key[0],key[1],key[2]},.hash=hash,.length=static_cast<uint16_t>(value.size()),.id=id};}
        else slots[i]=Slot{.data=shared.canonical[id].data(),.hash=hash,.length=static_cast<uint16_t>(value.size()),.id=id};
        return id;
    }
};
''';p.write_text(new);assert new[:new.index('struct LocalEndpoints {')]==prefix;patch=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/track-a/endpoint_table.hpp',tofile='b/track-a/endpoint_table.hpp'));(w/'endpoint_table.hpp.patch').write_text(patch)
pre={'created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_parent':head,'official_score':False,'selected_in_root':False,'scope':'A365 exact4..28-byte cache key encoding: existing4096 direct slots grow16->32B/align32, payload24B + ORIGINALfull32 sampledhash + original len16/ID16.4..7 first/last4 coverallbytes;8..24 first/middle/last8 coverallbytes;25..28 storeprefix24 containingoldfirsta4/midb4, and equalfullh bijectivelydetermineslastc4 (oddmultiply, xor-shift, rotations invertible32bit), coveringallbytes. This is an injectivecomplete-key representation, not probabilistichash-only acceptance. Exactlength checkedbeforeactiveunionmemberread; aggregate designatedinitialization plustrivialcopy/assignment switchmemberlifetime, no pointer/integer punning.0..3/29..65535 retainoriginalfullmemcmp/pointer;>65535 unchangedauthoritativesharedfallback. Originalsharedinterner/fullstringequality/IDs/limit4096/cancellation, originalhash/bucket/algorithm/parse/hour/percentiles/allocator/flags/PGO/default12 unchanged. Extraeligiblebranch/loads,128KiBperworker(+64KiB,+786432Bat12), largerworking-set/source maylose; native screenrequiredbefore broadproof. Newactualheader union/guard/allbytes/hashcollision/length29gap/fullwidth/IDs/overalign/independent/adversarial/untrained/strict/race/GNU/image/default/Make/sourceproof requiredbefore anyprivatepush/realtrial. No seed/catalogue/answercache/harness/counter/identity/host/defaultbudget/exemption changes. Cacheholds computedinputkeys/IDs only, never precomputedanswers.','duplicate_check':'364same16B/4..12 rejectedread-only due1.27–3.46%traffic.365 growsnormalchargedslot to cover4..28 with44.71/40.41/53.36%totalcalls fromalreadyvalidated359summarycounts; no hit-lengthjoint timing known.359twochoice changesplacement/fallbacks,365keepsoriginalplacement/hash and removescanonical-load/memcmp for exactencodedeligiblehits;168globalcanonicalcopy/283inlinebytecmp distinct. Sharedprefix exact bytechecked.','source_sha256':{str(p.relative_to(s)):sha(p)for p in sorted((s/'track-a').iterdir())if p.is_file()},'root_selected_bindings':bindings,'control_binary':str(r/'.build/round263/final-make/track-a'),'control_binary_sha256':sha(r/'.build/round263/final-make/track-a'),'primary_sources':[{'url':'https://eel.is/c++draft/class.union','scope':'Activeunionmember lifetime and trivialassignment rules; not a proof of this newcache.'},{'url':'https://eel.is/c++draft/dcl.init.aggr','scope':'C++aggregate designatedanonymousunion memberinitialization; actualcompilers/strictmodelstillrequired.'}],'readonly_traffic_report':{'path':'.build/round364/traffic-review.json','sha256':sha(r/'.build/round364/traffic-review.json')}}
(w/'preflight.json').write_text(json.dumps(pre,indent=2)+'\n');shutil.copyfile(Path(__file__),w/'prepare.py')
screen=(r/'.build/round359/screen.py').read_text().replace('359','365').replace("diag=read(w/'diagnostic/report.json');assert diag['passed'], 'Diagnostic review required before separate candidate screen' ","assert read(r/'.build/round364/traffic-review.json')['per_call_length_traffic_available']")
screen=screen.replace('two-choice cuckoo front-cache','exact4..28 encoded front-cache')
compile(screen,'screen365.py','exec');(w/'screen.py').write_text(screen);print('PREPARED365 isolated exactkeyencoding32B; root unchanged')
