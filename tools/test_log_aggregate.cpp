#include "../track-a/aggregate.hpp"
#include <cassert>
#include <iostream>
#include <map>
#include <string>
#include <thread>

int main() {
    CountChunk chunk(3);std::array<WideCounts,3> expected{};
    for(unsigned i=0;i<300000;++i){size_t group=i%3;bool error=i%5==0;chunk.add(group,error);++expected[group].count;expected[group].errors+=error;}
    for(unsigned i=0;i<100000;++i){chunk.add(0,true);++expected[0].count;++expected[0].errors;}
    uint32_t prefix=0;for(size_t group=0;group<3;++group){auto actual=chunk.total(group);assert(actual.count==expected[group].count&&actual.errors==expected[group].errors);chunk.cells[group].cursor=prefix;prefix+=actual.count;}
    std::vector<uint8_t> claimed(prefix);uint32_t begin=0;
    for(size_t group=0;group<3;++group){for(uint64_t i=0;i<expected[group].count;++i){uint32_t slot=chunk.cells[group].cursor++;assert(slot==begin+i);assert(claimed[slot]++==0);}begin+=expected[group].count;}
    for(uint8_t flag:claimed)assert(flag==1);
    for(size_t bad:{0U,3U}){bool threw=false;try{Endpoints invalid(bad);}catch(const std::runtime_error&){threw=true;}assert(threw);}
    Endpoints small(2);small.intern("a",42);small.intern("b",42);bool retry=false;try{small.intern("c",42);}catch(const RetryEndpoints&){retry=true;}assert(retry&&small.too_small.load()&&small.canceled.load());
    constexpr unsigned workers=4,updates=10000,key_count=1000;constexpr size_t capacity=2048;
    Endpoints endpoints(capacity);std::vector<std::string> keys;for(unsigned i=0;i<key_count;++i)keys.push_back("/endpoint/"+std::to_string(i));
    std::map<std::pair<unsigned,unsigned>,WideCounts> reference;
    for(unsigned w=0;w<workers;++w)for(unsigned i=0;i<updates;++i){auto& value=reference[{(i+w)%72,(i*7+w*13)%key_count}];++value.count;value.errors+=i%3==0;}
    std::vector<CountChunk> chunks;for(unsigned w=0;w<workers;++w)chunks.emplace_back(72*capacity);std::vector<std::thread> threads;
    for(unsigned w=0;w<workers;++w)threads.emplace_back([&,w]{for(unsigned i=0;i<updates;++i){unsigned key=(i*7+w*13)%key_count,hour=(i+w)%72;uint64_t hash=key%10 ? Endpoints::hash_key(keys[key]):42;uint32_t id=endpoints.intern(keys[key],hash);chunks[w].add(hour*capacity+id,i%3==0);}});
    for(auto& thread:threads)thread.join();assert(endpoints.used.load()==key_count);std::vector<bool> ids(key_count);
    for(unsigned key=0;key<key_count;++key){uint64_t hash=key%10 ? Endpoints::hash_key(keys[key]):42;uint32_t id=endpoints.lookup(keys[key],hash);assert(id<key_count&&!ids[id]&&endpoints.paths[id]==keys[key]);ids[id]=true;
        for(unsigned hour=0;hour<72;++hour){WideCounts actual;for(const auto& local:chunks){auto value=local.total(hour*capacity+id);actual.count+=value.count;actual.errors+=value.errors;}auto r=reference.find({hour,key});WideCounts value=r==reference.end()?WideCounts{}:r->second;assert(actual.count==value.count&&actual.errors==value.errors);}
    }
    std::cout<<"PASS exact wide count/error spills, reused cursor slot claims, endpoint retries/full collisions and four-thread std::map model\n";
}
