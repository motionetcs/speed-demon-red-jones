#include "names.hpp"
#include <cassert>
#include <chrono>
#include <exception>
#include <iostream>
#include <limits>
#include <map>
#include <set>
#include <string>
#include <thread>
#include <utility>
#include <sys/mman.h>
#include <unistd.h>

#ifdef NDEBUG
#error Independent model checks require assertions enabled.
#endif

namespace {
size_t checks=0, completed_calls=0;
void require(bool good,const char* message){if(!good)throw std::runtime_error(message);++checks;}
struct KeySpec{std::string value;uint64_t hash;};
struct Job{size_t key,country;};
using Reference=std::set<std::pair<std::string,size_t>>;
struct Result{std::vector<size_t> fresh;size_t attempted=0,completed=0;bool canceled=false;std::exception_ptr error;};

uint64_t chosen_hash(const std::string& key,size_t index,unsigned mode){
    if(mode==0)return 0;
    if(mode==1)return 1;
    if(mode==2)return UINT64_MAX;
    if(mode==3)return UINT64_C(0x98abcdef00000000)|uint64_t(index*7);
    if(mode==4)return (uint64_t(index+1)<<32)|3;
    return SharedNames::hash_key(key);
}
std::vector<KeySpec> make_keys(size_t count,unsigned mode){
    const size_t lengths[]={23,24,25,31,63,127};std::vector<KeySpec> keys;keys.reserve(count);
    for(size_t i=0;i<count;++i){
        std::string value="key/"+std::to_string(i)+"|";value.push_back(char(0));value.push_back(static_cast<char>(255));
        value.resize(lengths[i%6],static_cast<char>((i*37+11)%256));
        uint64_t hash=chosen_hash(value,i,mode);keys.push_back({std::move(value),hash});
    }
    return keys;
}
std::vector<std::vector<Job>> make_jobs(const std::vector<KeySpec>& keys,size_t workers,size_t countries){
    std::vector<std::vector<Job>> jobs(workers);if(keys.empty())return jobs;
    std::vector<size_t> seams;
    for(size_t country:std::vector<size_t>{0,1,62,63,64,65,127,128,191,192,254,255,256,257,countries-1}){
        if(country<countries&&std::find(seams.begin(),seams.end(),country)==seams.end())seams.push_back(country);
    }
    for(size_t i=0;i<keys.size();++i){jobs[i%workers].push_back({i,0});jobs[i%workers].push_back({i,countries-1});}
    for(size_t worker=0;worker<workers;++worker)for(size_t i=0;i<128;++i){
        Job job{(i*17+worker*13)%keys.size(),seams[(i+worker)%seams.size()]};
        jobs[worker].push_back(job);jobs[worker].push_back(job);
    }
    return jobs;
}
Reference reference_for(const std::vector<KeySpec>& keys,const std::vector<std::vector<Job>>& jobs){
    std::map<std::string,uint64_t> hashes;Reference reference;
    for(const auto& key:keys){auto found=hashes.emplace(key.value,key.hash);require(found.second||found.first->second==key.hash,"equal model keys need equal hashes");}
    for(const auto& worker:jobs)for(const auto& job:worker)reference.emplace(keys.at(job.key).value,job.country);
    return reference;
}
std::vector<Result> execute(SharedNames& table,std::vector<KeyArena>& arenas,const std::vector<KeySpec>& keys,const std::vector<std::vector<Job>>& jobs){
    std::vector<Result> results(jobs.size());for(auto& row:results)row.fresh.resize(table.countries);
    std::atomic<bool> go{false};std::vector<std::thread> threads;threads.reserve(jobs.size());
    try{
        for(size_t worker=0;worker<jobs.size();++worker)threads.emplace_back([&,worker]{
            while(!go.load(std::memory_order_acquire))std::this_thread::yield();
            auto& result=results[worker];
            try{
                for(const auto& job:jobs[worker]){
                    ++result.attempted;const auto& key=keys[job.key];
                    bool fresh=table.first(key.value,job.country,key.hash,arenas[worker]);
                    if(fresh)++result.fresh[job.country];
                    ++result.completed;
                }
            }catch(const SharedCanceled&){result.canceled=true;}
            catch(...){table.canceled.store(true,std::memory_order_relaxed);result.error=std::current_exception();}
        });
    }catch(...){table.canceled.store(true,std::memory_order_relaxed);go.store(true,std::memory_order_release);for(auto& thread:threads)thread.join();throw;}
    go.store(true,std::memory_order_release);for(auto& thread:threads)thread.join();
    for(const auto& result:results)if(result.error)std::rethrow_exception(result.error);
    return results;
}
void snapshot(SharedNames& table,const Reference& reference){
    std::map<std::string,std::vector<uint64_t>> expected;
    for(const auto& item:reference){auto& bits=expected[item.first];if(bits.empty())bits.resize(table.words);bits[item.second/64]|=uint64_t(1)<<(item.second%64);}
    const size_t used=table.used.load(std::memory_order_relaxed);require(used==expected.size(),"unique key count mismatch");
    std::set<std::string> seen;
    for(size_t id=0;id<used;++id){
        require(table.published[id/SharedNames::block_size].load(std::memory_order_acquire)!=nullptr,"ready id has no block");
        auto view=table.bytes(id);std::string key(view.data(),view.size());auto found=expected.find(key);
        require(found!=expected.end()&&seen.insert(key).second,"unknown or duplicate stored full key");
        const auto& stored=table.at(id);require(reinterpret_cast<uintptr_t>(&stored)%64==0,"key alignment mismatch");
        for(size_t word=0;word<std::max<size_t>(4,table.words);++word){
            uint64_t actual=word<4?stored.flags[word].load(std::memory_order_relaxed):table.spill[id*(table.words-4)+word-4].load(std::memory_order_relaxed);
            uint64_t wanted=word<table.words?found->second[word]:0;require(actual==wanted,"country word differs from independent set");
        }
    }
    size_t occupied=0;
    for(size_t i=0;i<table.capacity*2;++i){uint64_t state=table.slots[i].load(std::memory_order_acquire);require(state!=1,"pending slot after successful join");if(state>1){require(size_t(uint32_t(state)-2)<used,"published index outside used prefix");++occupied;}}
    require(occupied==used,"published slot/key count mismatch");
    const size_t blocks=(used+SharedNames::block_size-1)/SharedNames::block_size;
    for(size_t i=0;i<table.blocks.size();++i)require(bool(table.published[i].load(std::memory_order_acquire))==(i<blocks),"lazy publication prefix mismatch");
}
void run_normal(size_t capacity,size_t countries,size_t key_count,size_t workers,unsigned mode){
    auto keys=make_keys(key_count,mode);auto jobs=make_jobs(keys,workers,countries);auto reference=reference_for(keys,jobs);
    std::vector<KeyArena> arenas(workers);SharedNames table(capacity,countries);
    for(size_t i=0;i<table.blocks.size();++i)require(table.published[i].load()==nullptr,"nonzero initial block pointer");
    auto results=execute(table,arenas,keys,jobs);std::vector<size_t> actual(countries),expected(countries);
    for(const auto& item:reference)++expected[item.second];
    for(size_t worker=0;worker<workers;++worker){
        require(!results[worker].canceled&&results[worker].completed==jobs[worker].size(),"normal worker did not complete");
        completed_calls+=results[worker].completed;
        for(size_t country=0;country<countries;++country)actual[country]+=results[worker].fresh[country];
    }
    require(actual==expected,"exactly-once country fresh totals mismatch");require(!table.canceled.load()&&!table.too_small.load(),"normal table canceled");snapshot(table,reference);
    for(const auto& worker:jobs)for(const auto& job:worker)require(!table.first(keys[job.key].value,job.country,keys[job.key].hash,arenas[0]),"replay of an existing pair became fresh");
}
void capacity_and_discard(){
    auto keys=make_keys(97,4);auto jobs=make_jobs(keys,12,257);
    {
        std::vector<KeyArena> arenas(12);SharedNames small(8,257);auto partial=execute(small,arenas,keys,jobs);
        require(small.too_small.load()&&small.canceled.load(),"capacity pressure did not cancel");
        for(size_t i=0;i<small.capacity*2;++i){uint64_t state=small.slots[i].load();if(state>1)require(size_t(uint32_t(state)-2)<small.capacity,"canceled attempt published invalid id");}
        size_t canceled=0;for(const auto& row:partial)canceled+=row.canceled;require(canceled!=0,"no capacity cancellation observed");
    }
    // A fresh attempt deliberately does not add any partial attempt counters.
    run_normal(128,257,97,12,4);
}
void all_country_words(){
    for(size_t countries:std::vector<size_t>{1,2,63,64,65,127,128,129,255,256,257,1024,17577}){
        std::vector<KeyArena> arenas(1);SharedNames table(8,countries);Reference reference;
        const std::string keys[]={"",std::string(80,'L')};
        for(const auto& key:keys)for(size_t country=0;country<countries;++country){bool expected=reference.emplace(key,country).second;require(table.first(key,country,UINT64_MAX,arenas[0])==expected,"all-country first result mismatch");}
        for(const auto& key:keys)for(size_t country=0;country<countries;++country)require(!table.first(key,country,UINT64_MAX,arenas[0]),"all-country repeat mismatch");
        snapshot(table,reference);
    }
}
struct GuardBuffer{
    char* allocation=nullptr;char* start=nullptr;size_t bytes=0;
    explicit GuardBuffer(size_t length){
        long value=sysconf(_SC_PAGESIZE);require(value>0,"page size unavailable");size_t page=static_cast<size_t>(value);
        size_t usable=std::max(page,((length+page-1)/page)*page);bytes=usable+2*page;
        allocation=static_cast<char*>(mmap(nullptr,bytes,PROT_NONE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0));
        if(allocation==static_cast<char*>(MAP_FAILED)){allocation=nullptr;throw std::runtime_error("guard mmap failed");}
        if(mprotect(allocation+page,usable,PROT_READ|PROT_WRITE)!=0){munmap(allocation,bytes);allocation=nullptr;throw std::runtime_error("guard mprotect failed");}
        start=allocation+page+usable-length;
    }
    void release(){require(munmap(allocation,bytes)==0,"guard munmap failed");allocation=nullptr;}
    ~GuardBuffer(){if(allocation)munmap(allocation,bytes);}
};
void guarded_owned_keys(){
    const size_t lengths[]={0,1,3,4,7,8,15,16,23,24,25,31,32,63,64,127,128,255,256,4095,4096,65534,65535,65536,size_t(1)<<20};
    std::vector<KeyArena> arenas(1);SharedNames table(64,257);Reference reference;std::vector<KeySpec> saved;
    const size_t countries[]={0,1,63,64,127,128,255,256};
    for(size_t length:lengths){
        GuardBuffer input(length);for(size_t i=0;i<length;++i)input.start[i]=static_cast<char>((i*73+length*11)%256);
        std::string key(input.start,length);uint64_t hash=SharedNames::hash_key(key);
        for(size_t country:countries){bool expected=reference.emplace(key,country).second;require(table.first(std::string_view(input.start,length),country,hash,arenas[0])==expected,"guard key insertion mismatch");}
        if(length)std::memset(input.start,0x5a,length);
        input.release();saved.push_back({std::move(key),hash});
        for(size_t country:countries)require(!table.first(saved.back().value,country,hash,arenas[0]),"stored key borrowed caller memory");
    }
    for(const auto& key:saved)for(size_t country:countries)require(!table.first(key.value,country,key.hash,arenas[0]),"long arena pointer changed after growth");
    require(arenas[0].blocks.size()>=2,"arena growth boundary not reached");snapshot(table,reference);
}
template<class Function>void expect_throw(Function function){bool threw=false;try{function();}catch(const std::exception&){threw=true;}require(threw,"invalid argument did not throw");}
void invalid_bounds(){
    expect_throw([]{SharedNames table(0,1);});expect_throw([]{SharedNames table(3,1);});
    expect_throw([]{SharedNames table(1,SIZE_MAX);});
    if(sizeof(size_t)>=8)expect_throw([]{SharedNames table(size_t(UINT64_C(1)<<32),1);});
    expect_throw([]{SharedNames table(16,SIZE_MAX-63);});
    KeyArena arena;SharedNames table(8,257);expect_throw([&]{table.first("invalid-country",257,0,arena);});require(table.used.load()==0,"invalid country reserved an id");
}
}
int main(){
    try{
        invalid_bounds();run_normal(16,1,0,12,5);
        for(size_t workers=1;workers<=12;++workers)run_normal(128,257,31,workers,5);
        for(unsigned mode=0;mode<5;++mode)for(size_t workers:std::vector<size_t>{1,6,12})run_normal(256,257,97,workers,mode);
        run_normal(128,17577,31,12,4);run_normal(1,1,1,12,0);run_normal(32,257,32,12,2);
        for(size_t key_count:std::vector<size_t>{2047,2048,2049})run_normal(4096,257,key_count,12,5);
        run_normal(4096,257,4096,12,5);run_normal(8192,257,4097,12,5);
        all_country_words();guarded_owned_keys();capacity_and_discard();
        std::cout<<"PASS shared index independent-set/publication/ownership/country/block/cancel model "<<checks<<" checks, "<<completed_calls<<" concurrent calls\n";
    }catch(const std::exception& error){std::cerr<<"FAIL shared index model: "<<error.what()<<'\n';return 1;}
}
