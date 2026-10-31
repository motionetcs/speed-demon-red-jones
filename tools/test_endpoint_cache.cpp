#ifndef ENDPOINTS_HEADER
#define ENDPOINTS_HEADER "../track-a/endpoint_table.hpp"
#endif
#include ENDPOINTS_HEADER
#include <array>
#include <cassert>
#include <iostream>
#include <set>
#include <string>
#include <thread>
#include <vector>
#include <sys/mman.h>
#include <unistd.h>

uint32_t reference_hash(std::string_view value){
    if(value.size()<4){uint32_t h=2166136261U;for(unsigned char c:value)h=(h^c)*16777619U;return h;}
    auto word=[&](size_t at){uint32_t result=0;for(unsigned j=0;j<4;++j)result|=uint32_t(static_cast<unsigned char>(value[at+j]))<<(8*j);return result;};
    uint32_t h=(word(0)^std::rotl(word((value.size()-4)/2),11)^std::rotl(word(value.size()-4),23)^uint32_t(value.size()))*0x9e3779b1U;return h^(h>>16);
}
int main(){
    for(unsigned byte=0;byte<256;++byte)for(unsigned length=0;length<=128;++length){std::string key(length,char(byte));assert(LocalEndpoints::hash_key(key)==reference_hash(key));}
    size_t page=size_t(sysconf(_SC_PAGESIZE));char* memory=static_cast<char*>(mmap(nullptr,page*2,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANON,-1,0));assert(memory!=MAP_FAILED&&mprotect(memory+page,page,PROT_NONE)==0);
    for(size_t length=0;length<=512;++length){char* start=memory+page-length;for(size_t i=0;i<length;++i)start[i]=char(i*73);std::string_view key(start,length);assert(LocalEndpoints::hash_key(key)==reference_hash(key));}
    munmap(memory,page*2);
    {
        Endpoints shared;LocalEndpoints cache(shared);std::vector<std::string> keys;
        for(unsigned i=0;i<4097;++i)keys.push_back("/limit/"+std::to_string(i));
        for(unsigned i=0;i<4096;++i){assert(cache.intern(keys[i])==i);assert(shared.canonical[i]==keys[i]);}
        for(unsigned i=4096;i>0;--i)assert(cache.intern(keys[i-1])==i-1);
        bool threw=false;try{cache.intern(keys.back());}catch(const std::runtime_error&){threw=true;}assert(threw&&shared.canceled.load());
    }
    {
        Endpoints shared;LocalEndpoints cache(shared);std::vector<std::string> keys;
        for(size_t length:{0U,1U,3U,4U,125U,65535U,65536U,1048576U}){keys.emplace_back(length,'x');for(size_t i=0;i<length;++i)keys.back()[i]=char(i%251);}
        for(unsigned i=0;i<keys.size();++i){assert(cache.intern(keys[i])==i);assert(cache.intern(keys[i])==i);assert(shared.canonical[i]==keys[i]);}
    }
    constexpr unsigned count=701,workers=4;
    std::vector<std::string> keys;keys.reserve(count);
    // All sampled bytes/lengths are identical; only unsampled bytes differ.
    for(unsigned i=0;i<count;++i){std::string key(64,'a');std::string id=std::to_string(i);key.replace(8,id.size(),id);keys.push_back(key);}
    for(auto& key:keys)assert(LocalEndpoints::hash_key(key)==LocalEndpoints::hash_key(keys.front()));
    Endpoints shared;std::array<std::atomic<unsigned>,count> ids;for(auto& id:ids)id.store(UINT32_MAX);std::atomic<bool> mismatch{false};std::vector<std::thread> threads;
    for(unsigned worker=0;worker<workers;++worker)threads.emplace_back([&,worker]{LocalEndpoints cache(shared);for(unsigned i=0;i<5000;++i){unsigned k=(i*7+worker*13)%count;unsigned id=cache.intern(keys[k]);unsigned expected=UINT32_MAX;if(!ids[k].compare_exchange_strong(expected,id)&&expected!=id)mismatch.store(true);if(shared.canonical[id]!=keys[k])mismatch.store(true);}});
    for(auto& thread:threads)thread.join();assert(!mismatch.load()&&shared.used.load()==count);std::set<unsigned> unique;for(auto& id:ids)unique.insert(id.load());assert(unique.size()==count);
    std::cout<<"PASS exact endpoint cache byte/guard-page/eviction/long-key/4096-ID and concurrent canonical-publication models\n";
}
