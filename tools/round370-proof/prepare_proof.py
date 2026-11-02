from pathlib import Path
import datetime,hashlib,json,shutil
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round370';pre=json.loads((w/'preflight.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
for p,h in pre['source_sha256'].items():assert sha(w/'source'/p)==h
assert not(w/'raw_fields_model.cpp').exists()
main=(w/'source/track-c/main.cpp').read_text();block=main[main.index('struct Field {'):main.index('// A singleton quote')];(w/'csv_model.hpp').write_text('#pragma once\n#include "source/track-c/io.hpp"\n#include "source/track-c/quote_scan.hpp"\n'+block)
model=r'''#include "csv_model.hpp"
#include <array>
#include <cassert>
#include <iostream>
#include <random>
#include <string>
#include <sys/mman.h>
#include <unistd.h>

uint64_t checks=0;
std::string interior(std::string_view value){
    std::string result;
    for(char byte:value){result.push_back(byte);if(byte=='"')result.push_back(byte);}
    return result;
}
void verify_at(const char* memory,std::string_view value,bool quoted,std::string_view tail){
    std::string raw=quoted?interior(value):std::string(value);
    size_t consumed=raw.size()+(quoted?2:0);
    Csv csv{memory,memory+consumed+tail.size()};auto field=csv.field();
    assert(field.value==raw&&field.bytes==value.size()&&csv.p==memory+consumed);
    if(tail==",")csv.comma();else csv.newline();
    assert(csv.p==csv.end);++checks;
}
void verify(std::string_view value,bool quoted,std::string_view tail){
    std::string raw=quoted?interior(value):std::string(value);
    std::string input=(quoted?"\""+raw+"\"":raw)+std::string(tail);
    verify_at(input.data(),value,quoted,tail);
}
int main(){
    static_assert(sizeof(Field)==sizeof(std::string_view)+sizeof(size_t));
    for(unsigned byte=0;byte<256;++byte)for(size_t n=0;n<=256;++n){
        std::string value(n,char(byte));
        for(std::string_view tail:{std::string_view(),std::string_view(","),std::string_view("\n"),std::string_view("\r\n")}){
            verify(value,true,tail);
            if(byte!='"'&&byte!=','&&byte!='\r'&&byte!='\n')verify(value,false,tail);
        }
    }
    std::mt19937_64 random(0x370f13ULL);
    for(unsigned trial=0;trial<20000;++trial){
        std::string value(size_t(random()%384),' ');
        for(char& byte:value)byte=char(random()%256);
        verify(value,true,trial%2?"\r\n":",");
    }
    for(std::string_view label:{"id","name","note","region_id","amount","country"}){
        for(bool quoted:{false,true}){
            std::string input=(quoted?"\""+interior(label)+"\"":std::string(label))+",";
            Csv csv{input.data(),input.data()+input.size()};assert(csv.field().value==label);csv.comma();assert(csv.p==csv.end);++checks;
        }
        for(size_t at=0;at<=label.size();++at)for(unsigned byte=0;byte<256;++byte){
            std::string decoded(label);decoded.insert(at,1,char(byte));
            std::string input="\""+interior(decoded)+"\",";Csv csv{input.data(),input.data()+input.size()};
            // The expected decoded bytes are known before encoding; no parsing oracle is copied.
            assert((csv.field().value==label)==(decoded==label));csv.comma();assert(csv.p==csv.end);++checks;
        }
    }
    for(std::string_view value:{std::string_view("\xef\xbb\xbf"),std::string_view("a\xef\xbb\xbf\n\"z "),std::string_view("\""),std::string_view("\"\"\""),std::string_view(" ")})verify(value,true,"\r\n");
    for(char byte:{'x','"','\n'})verify(std::string(1048576,byte),true,",");
    size_t page=size_t(sysconf(_SC_PAGESIZE));
    char* pages=static_cast<char*>(mmap(nullptr,page*3,PROT_NONE,MAP_PRIVATE|MAP_ANON,-1,0));
    assert(pages!=MAP_FAILED&&mprotect(pages+page,page,PROT_READ|PROT_WRITE)==0);
    for(size_t n=0;n<=512;++n)for(bool quoted:{false,true}){
        std::string value(n,quoted?'"':'a');std::string raw=quoted?interior(value):value;std::string input=quoted?"\""+raw+"\"":raw;
        for(bool right:{false,true}){
            char* start=right?pages+2*page-input.size():pages+page;
            if(!input.empty())std::memcpy(start,input.data(),input.size());
            verify_at(start,value,quoted,{});
        }
        if(quoted){
            input.pop_back();char* start=pages+2*page-input.size();std::memcpy(start,input.data(),input.size());
            Csv csv{start,start+input.size()};bool threw=false;try{csv.field();}catch(const std::runtime_error&){threw=true;}
            assert(threw);++checks;
            start=pages+page;std::memcpy(start,input.data(),input.size());start[input.size()]='"';
            csv={start,start+input.size()};threw=false;try{csv.field();}catch(const std::runtime_error&){threw=true;}
            assert(threw);++checks;
        }
    }
    assert(munmap(pages,page*3)==0);
    std::cout<<"PASS370 constructed rawcanonical/decodedcount/quote-free-header-equivalence/all-byte/UTF8/BOM/1MiB/logical-and-protected-tail models "<<checks<<" checks\n";
}
''';(w/'raw_fields_model.cpp').write_text(model)
driver=(r/'.build/round357/native_proof.py').read_text().replace('round357','round370').replace('PASS357','PASS370').replace('new32bit exactmodel/main strict proof; independentABA/GCC/image/actual pending','rawfield/header-equivalence exactmodel/main strict proof; GNU/image/actual pending')
start=driver.index("files={name:sha(w/name)");end=driver.index("for p,h in pre['source_sha256'].items():",start)
driver=driver[:start]+'''files={name:sha(w/name)for name in ['raw_fields_model.cpp','csv_model.hpp']};manifest={'created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'preflight_sha256':sha(w/'preflight.json'),'source_sha256':pre['source_sha256'],'model_files_sha256':files,'scope':'Fresh370 constructed-field/header-equivalence/boundary/long/all-byte rawlexer model under failfastASAN/UBSAN; NEWcurrentmain ASAN+TSAN replay356saved input/referencebytes, no regenerated/oracled oldfixtures. Originalheader-only Names/queue/numeric/source protocols retainedONLYby exactbytes, no356/357newqueue/startupcallback proof transferred to original370 protocol. Newfresh3851/3853samples/3863full generated once and officialreference-compared. GNU/image/default/actual stillrequired.'};dump(w/'proof-manifest.json',manifest)
''' +driver[end:]
a=driver.index("'retained_plain_startup_fault_proof':");b=driver.index(",'compiles':[]",a);driver=driver[:a]+"'unchanged_headers_sha256':pre['unchanged_C_headers_sha256']"+driver[b:]
a=driver.index(" folder=out/mode;folder.mkdir(exist_ok=True);binary=folder/'queue-model'");b=driver.index(" binary=folder/'track-c'",a)
driver=driver[:a]+''' folder=out/mode;folder.mkdir(exist_ok=True)
 if mode=='asan':
  binary=folder/'field-model';compile(mode+'-field-model',w/'raw_fields_model.cpp',binary,flags);q=subprocess.run([str(binary)],capture_output=True,text=True,env=env,timeout=300);row={'mode':mode,'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr,'binary_sha256':sha(binary)};dump(folder/'model-attempt.json',row);assert q.returncode==0 and q.stdout.startswith('PASS370')and not q.stderr,(q.returncode,q.stdout,q.stderr[-2500:]);row['passed']=True;dump(folder/'model.json',row);report['models'].append(row);save();print('PASS370 constructed field/header model',flush=True)
''' +driver[b:]
driver=driver.replace('NEW357exactsource executions','NEW370exactsource executions').replace('no356sourceproofsubstitution','no356sourceproofsubstitution')
# Add new independent datasets only after saved bank replays are complete.
a=driver.index("for p,h in pre['source_sha256'].items():assert sha(s/p)==h,p",driver.index('for mode,flags'))
fresh='''report['fresh_suites']=[]
for mode,scale,seed in [('asan','sample',3851),('tsan','sample',3853),('asan','full',3863)]:
 path=r/f'docs/round370-c-{mode}-fresh-{scale}{seed}.json';assert not path.exists()and not(r/f'.data/c/{scale}-seed{seed}').exists(),'Do not duplicate generator/reference work';argv=['python3','tools/verify.py','--run-id',f'round370-{mode}-fresh-{scale}{seed}','--source-root',str(s),'--binary-dir',str(out/mode),'--tracks','c','--threads','1','6','12','--scale',scale,'--seeds',str(seed),'--report',str(path)]
 if scale=='full':argv.append('--skip-adversarial')
 print('RUN370 fresh',mode,scale,seed,flush=True);q=subprocess.run(argv,cwd=r,capture_output=True,text=True,env=dict(env,PYTHONPATH=str(r/'tools')),timeout=1200);(out/f'fresh-{mode}-{seed}.stdout').write_text(q.stdout);(out/f'fresh-{mode}-{seed}.stderr').write_text(q.stderr);row={'mode':mode,'scale':scale,'seed':seed,'command':argv,'returncode':q.returncode,'path':str(path.relative_to(r))};report['fresh_suites'].append(row);save();assert q.returncode==0 and read(path)['passed'],(q.returncode,q.stdout[-1200:],q.stderr[-2500:]);row['sha256']=sha(path);save()
'''
driver=driver[:a]+fresh+driver[a:];compile(driver,'native_proof370.py','exec');(w/'native_proof.py').write_text(driver);shutil.copyfile(Path(__file__),w/'prepare_proof.py');print('PREPARED370 newrawfield model/source-specific strict+independent native driver; sourcefrozen')
