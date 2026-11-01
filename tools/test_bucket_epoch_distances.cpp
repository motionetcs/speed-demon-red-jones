#include DISTANCE_MAP_HEADER
#include <cassert>
#include <array>
#include <iostream>
#include <random>
#include <unordered_map>

int main(){
    std::mt19937_64 rng(0xE90C4256);
    FastDistances map;map.reset();
    std::unordered_map<uint32_t,uint64_t> ref;
    size_t checks=0;
    auto improve=[&](uint32_t node,uint64_t value){
        auto p=ref.find(node);uint64_t old=p==ref.end()?UINT64_MAX:p->second;
        assert(map.improve(node,value)==(value<old));
        if(value<old)ref[node]=value;
        assert(map.get(node)==(ref.count(node)?ref.at(node):UINT64_MAX));++checks;
    };
    for(unsigned round=0;round<1024;++round){
        std::vector<uint32_t> prior;for(auto [node,value]:ref){(void)value;prior.push_back(node);}
        map.reset();for(auto node:prior){assert(map.get(node)==UINT64_MAX);++checks;}ref.clear();
        for(unsigned i=0;i<64;++i){
            uint32_t node=uint32_t(rng()%2048);
            uint64_t value=i%3?rng()%200000:uint64_t(UINT32_MAX)+rng()%100000;
            improve(node,value);
        }
        for(auto node:prior){assert(map.get(node)==(ref.count(node)?ref.at(node):UINT64_MAX));++checks;}
        for(auto [node,value]:ref){assert(map.get(node)==value);++checks;}
        assert(map.get(UINT32_MAX)==UINT64_MAX);
    }
    map.reset();ref.clear();
    unsigned old_bits=map.bits;
    uint32_t low=(1U<<old_bits)-1;
    for(unsigned i=0;i<32;++i)improve(low+(i<<old_bits),100+i);
    for(unsigned i=0;i<80000;++i)improve((i*0x9e3779b1U)&((1U<<21)-1),(i*37)%100000);
    assert(map.bits>old_bits);
    for(auto [node,value]:ref){assert(map.get(node)==value);++checks;}
    for(uint32_t node:{0U,1U,1023U,2097151U,2097152U,UINT32_MAX}){
        map.reset();ref.clear();uint64_t mask=map.distance_mask();
        for(uint64_t value:std::array<uint64_t,8>{UINT64_MAX-1,(1ULL<<60)+9,uint64_t(UINT32_MAX)+1,uint64_t(UINT32_MAX),mask+1,mask,mask-1,0})improve(node,value);
    }
    for(unsigned bits=0;bits<=20;++bits){
        FastDistances edge;edge.reset();edge.bits=bits;edge.labels=std::vector<uint32_t>(size_t(8)<<bits);edge.stamps.assign(size_t(1)<<bits,0);edge.epoch=FastDistances::epoch_mask;edge.used=0;
        uint32_t node=(1U<<21)-1;uint64_t value=edge.distance_mask()-1;
        assert(edge.improve(node,value)&&edge.get(node)==value);
        assert(edge.labels[edge.slot(node)]==UINT32_MAX);
        size_t start=size_t(node&((1U<<bits)-1))*8;
        for(unsigned lane=0;lane<8;++lane){
            uint32_t key=lane==7?node>>bits:uint32_t(node>>bits)^1U;
            edge.labels[start+lane]=(key<<(11+bits))|uint32_t(1);
        }
        assert(edge.slot(node)==start+7);
        edge.reset();assert(edge.epoch==1&&edge.get(node)==UINT64_MAX);
        for(auto v:edge.stamps)assert(v==0);
        assert(edge.improve(0,0));assert(edge.get(node)==(node==0?0:UINT64_MAX));
    }
    std::cout<<"PASS bucket epoch8"<<": "<<checks<<" independent map checks,1024 resets/wrap, full bucket/growth/promotion, every bits0..20/end allocation, zero/MAX/full64 and wide-node fallback\n";
}
