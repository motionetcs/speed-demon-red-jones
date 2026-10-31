#ifdef LOADER_HEADER
#include LOADER_HEADER
#else
#include "../track-d/load_cursors.hpp"
#endif
#include <array>
#include <cassert>
#include <iostream>
#include <random>
#include <thread>

void check(std::vector<uint32_t> expected,bool force_wide=false) {
    constexpr unsigned workers=4;std::vector<uint32_t> events;
    for(uint32_t node=0;node<expected.size();++node)for(uint32_t i=0;i<expected[node];++i)events.push_back(node);
    std::mt19937 random(0x4ca7);std::shuffle(events.begin(),events.end(),random);
    DegreeBytes counts(expected.size());std::array<DegreeBytes::Spills,workers> spills;std::vector<std::thread> threads;
    for(unsigned w=0;w<workers;++w)threads.emplace_back([&,w]{for(size_t i=w;i<events.size();i+=workers)counts.add(events[i],spills[w]);});
    for(auto& thread:threads)thread.join();
    std::vector<uint32_t> starts(expected.size()+1);
    for(uint32_t node=0;node<expected.size();++node) {
        uint32_t actual=counts.values[node];for(const auto& spill:spills)if(auto i=spill.find(node);i!=spill.end())actual+=i->second;
        assert(actual==expected[node]);starts[node+1]=starts[node]+expected[node];
    }
    SharedCursor cursor(starts);std::vector<std::atomic<uint8_t>> claimed(events.size());threads.clear();
    for(unsigned w=0;w<workers;++w)threads.emplace_back([&,w]{for(size_t i=w;i<events.size();i+=workers){uint32_t node=events[i],slot=force_wide ? cursor.take<true>(node):cursor.take(node);assert(slot>=starts[node]&&slot<starts[node+1]);assert(claimed[slot].fetch_add(1)==0);}});
    for(auto& thread:threads)thread.join();for(const auto& flag:claimed)assert(flag.load()==1);
}
int main() {
    check({0,0,0,0});check({65535,0,0,0});check({65535,0,0,0},true);check({65536,0,0,0});
    std::vector<uint32_t> degrees(17000);for(size_t i=0;i<degrees.size();++i)degrees[i]=i%6;
    degrees[0]+=70000;degrees.back()+=100000;check(degrees);
    SharedCursor high(std::vector<uint32_t>{0,UINT32_MAX-5,UINT32_MAX});
    for(uint32_t i=0;i<5;++i)assert(high.take(1)==UINT32_MAX-5+i);
    std::cout<<"PASS concurrent byte-degree wraps, exact CSR slot ownership, mixed narrow/wide blocks,65535/65536 and uint32 boundaries\n";
}
