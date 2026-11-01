#include "source/track-c/names.hpp"
#include "offset_names_model.hpp"
#include <array>
#include <atomic>
#include <sys/mman.h>
#include <unistd.h>
#include <thread>

static size_t extra_checks=0;
static void guard_and_growth(){
    const size_t page=static_cast<size_t>(sysconf(_SC_PAGESIZE));
    auto* memory=static_cast<char*>(mmap(nullptr,page*3,PROT_NONE,MAP_PRIVATE|MAP_ANON,-1,0));
    assert(memory!=MAP_FAILED&&mprotect(memory+page,page,PROT_READ|PROT_WRITE)==0);
    Names table(257);table.entries.resize(8);std::set<std::pair<std::string,size_t>> reference;
    for(size_t length=0;length<=512;++length){
        char* start=memory+2*page-length;
        for(size_t j=0;j<length;++j)start[j]=char((j*73+length)%256);
        std::string saved(start,length);uint64_t hash=Names::hash_key(saved);
        for(size_t country:std::array<size_t,7>{0,1,63,64,127,255,256}){
            bool expected=reference.emplace(saved,country).second;
            assert(table.first(std::string_view(start,length),country,hash)==expected);++extra_checks;
        }
        if(length)std::memset(start,0,length);
        assert(!table.first(saved,256,hash));++extra_checks;
    }
    assert(munmap(memory,page*3)==0);
    for(unsigned pass=0;pass<3;++pass)for(unsigned i=0;i<24000;++i){
        std::string key="stable-pointee/"+std::to_string(i)+std::string(i%129,'x');
        uint64_t hash=(uint64_t(i%11)<<32)|uint32_t((i%997)*4);size_t country=(i+pass/2)%257;
        bool expected=reference.emplace(key,country).second;
        assert(table.first(key,country,hash)==expected);++extra_checks;
    }
    assert(table.entries.size()>16384&&table.storage.size()>8);
    for(const auto& item:reference){
        if(item.first.rfind("stable-pointee/",0)==0)continue;
        assert(!table.first(item.first,item.second,Names::hash_key(item.first)));++extra_checks;
    }
}
static void concurrent_private_owners(){
    constexpr unsigned owners=4;std::vector<std::string> keys;
    for(unsigned i=0;i<18000;++i)keys.push_back("owner-key/"+std::to_string(i)+std::string(i%17,'z'));
    std::array<size_t,owners> counts{};std::array<std::thread,owners> workers;
    for(unsigned owner=0;owner<owners;++owner)workers[owner]=std::thread([&,owner]{
        Names table(257);table.entries.resize(8);std::set<std::pair<std::string,size_t>> reference;
        for(unsigned pass=0;pass<3;++pass)for(unsigned i=0;i<keys.size();++i){
            uint64_t hash=Names::hash_key(keys[i]);if(hash%owners!=owner)continue;
            size_t country=(i+pass/2)%257;bool expected=reference.emplace(keys[i],country).second;
            assert(table.first(keys[i],country,hash)==expected);++counts[owner];
        }
    });
    for(auto& worker:workers)worker.join();
    size_t sum=0;
    for(auto count:counts)sum+=count;
    assert(sum==keys.size()*3);extra_checks+=sum;
}
int main(){run_offset_name_model<Names>();guard_and_growth();concurrent_private_owners();std::cout<<"PASS retained exact metadata-pointer guard/caller-reuse/collision/growth/slab-lifetime/private-owner reference checks "<<extra_checks<<"\n";}
