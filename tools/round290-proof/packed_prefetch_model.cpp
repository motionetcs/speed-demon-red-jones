#ifndef DISTANCE_MAP_HEADER
#define DISTANCE_MAP_HEADER "source/track-d/distance_map.hpp"
#endif
#include DISTANCE_MAP_HEADER
#include <cassert>
#include <array>
#include <iostream>
#include <random>
#include <set>
#include <unordered_map>
#include <vector>

template<class Map> constexpr bool is_packed=requires(Map map){map.bits;map.distance_mask();};
template<class Map> void improve(Map& map,std::unordered_map<uint32_t,uint64_t>& reference,uint32_t node,uint64_t value){
    if constexpr(requires(Map m){m.prefetch(node);})map.prefetch(node);
    auto found=reference.find(node);uint64_t before=found==reference.end()?UINT64_MAX:found->second;bool expected=value<before;assert(map.improve(node,value)==expected);if(expected)reference[node]=value;assert(map.get(node)==reference.at(node));
}
template<class Map> void representation(const Map& map,const std::unordered_map<uint32_t,uint64_t>& reference){
    if constexpr(is_packed<Map>){
        size_t ways=map.labels.size()>>map.bits;std::set<uint32_t> nodes;
        for(auto index:map.touched){assert(index<map.labels.size());uint32_t word=map.labels[index];assert(word);uint32_t node=((word>>(11+map.bits))<<map.bits)|uint32_t(index/ways);uint64_t distance=(word&map.distance_mask())-1;assert(nodes.insert(node).second);assert(reference.at(node)==distance&&map.get(node)==distance);assert(map.wide.get(node)>=distance);}
    }
}
template<class Map> void run_model(){
    Map map;map.reset();std::unordered_map<uint32_t,uint64_t> reference;unsigned bits=10,ways=8;
    if constexpr(is_packed<Map>){bits=map.bits;ways=unsigned(map.labels.size()>>bits);}
    uint32_t low=(1U<<bits)-1;
    for(unsigned i=0;i<ways+8;++i)improve(map,reference,low+(i<<bits),200+i);
    if constexpr(is_packed<Map>)assert(map.wide.used>0);
    for(unsigned i=0;i<60000;++i){uint32_t node=(i*0x9e3779b1U)&((1U<<21)-1);improve(map,reference,node,(i*37)%100000);}
    if constexpr(is_packed<Map>)assert(map.bits>bits);
    for(unsigned i=0;i<ways+8;++i)improve(map,reference,low+(i<<bits),1);
    for(auto [node,distance]:reference)assert(map.get(node)==distance);representation(map,reference);
    if constexpr(is_packed<Map>){
        Map tail;tail.reset();std::unordered_map<uint32_t,uint64_t> expected;unsigned width=unsigned(tail.labels.size()>>tail.bits);uint32_t end=(1U<<tail.bits)-1;
        for(unsigned i=0;i<width-1;++i)improve(tail,expected,end+(i<<tail.bits),0);
        improve(tail,expected,(1U<<21)-1,tail.distance_mask()-1);
        assert(tail.labels.back()==UINT32_MAX);representation(tail,expected);
    }
    for(uint32_t node:{0U,1U,1023U,1048575U,1048576U,2097151U,2097152U,2097153U,UINT32_MAX-1,UINT32_MAX}){
        map.reset();reference.clear();uint64_t mask=1U<<21;if constexpr(is_packed<Map>)mask=map.distance_mask();
        for(uint64_t value:std::array<uint64_t,8>{(1ULL<<60)+9,uint64_t(UINT32_MAX)+1,uint64_t(UINT32_MAX),mask+1,mask,mask-1,uint64_t(65536),uint64_t(0)})improve(map,reference,node,value);
        representation(map,reference);
    }
    if constexpr(is_packed<Map>){
        // A consistent maximum-width table state exercises31-bit shifts without
        // requiring millions of preceding inserts just to reach that state.
        Map high;high.bits=20;high.labels.assign(size_t(8)<<20,0);high.reset();std::unordered_map<uint32_t,uint64_t> expected;
        improve(high,expected,0,0);improve(high,expected,1U<<20,high.distance_mask()-1);
        improve(high,expected,(1U<<21)-1,uint64_t(high.distance_mask())+1);
        improve(high,expected,(1U<<21)-1,1);representation(high,expected);
    }
    std::mt19937_64 random(0x75d219ac);
    for(unsigned round=0;round<6;++round){
        map.reset();reference.clear();assert(map.get(UINT32_MAX)==UINT64_MAX&&map.get(0)==UINT64_MAX);
        for(unsigned i=0;i<20000;++i){uint32_t node=i%3?uint32_t(random()&((1U<<21)-1)):uint32_t(random()%2000);if(i%31==0)node=uint32_t(random());uint64_t value=i%7?random()%200000:(uint64_t(UINT32_MAX)+random()%10000000);improve(map,reference,node,value);if(i%4096==0)representation(map,reference);}
        for(auto [node,distance]:reference)assert(map.get(node)==distance);representation(map,reference);
        map.reset();for(auto [node,distance]:reference)assert(map.get(node)==UINT64_MAX);
    }
}
int main(){
#ifdef REQUIRE_PACKED_LABELS
    static_assert(is_packed<FastDistances>);
#endif
    for(unsigned bits:{0U,1U,10U,20U}){FastDistances m;m.bits=bits;m.labels.assign(size_t(8)<<bits,0);for(uint32_t node:{0U,1U,1023U,2097151U,2097152U,UINT32_MAX}){if(node<FastDistances::node_limit)assert(size_t(node&((1U<<bits)-1))*8<m.labels.size());m.prefetch(node);}m.reset();m.prefetch(0);}
    run_model<FastDistances>();std::cout<<"PASS exact distance reference, packed-key reconstruction, full-bucket fallback, grow/promotion/reset, boundary words/nodes and64-bit labels\n";
}
