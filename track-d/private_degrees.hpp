#pragma once
#include <cstddef>
#include <cstdint>
#include <memory>
#include <new>
#include <sys/mman.h>
#include <unordered_map>
#include <vector>
template<unsigned Bits> struct PrivateDegrees {
    static_assert(Bits==2||Bits==4||Bits==8);
    static constexpr unsigned per_byte=8/Bits,mask=(1U<<Bits)-1;
    struct Drop{size_t bytes;void operator()(uint8_t* p)const noexcept{munmap(p,bytes);}};
    uint32_t nodes;
    std::unique_ptr<uint8_t,Drop> values;
    std::unordered_map<uint32_t,uint32_t> spills;
    explicit PrivateDegrees(uint32_t n):nodes(n),values(nullptr,Drop{(size_t(n)+per_byte-1)/per_byte}){
        if(n){void* p=mmap(nullptr,values.get_deleter().bytes,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);if(p==MAP_FAILED)throw std::bad_alloc();values.reset(static_cast<uint8_t*>(p));}
    }
    void prefetch(uint32_t node)const{__builtin_prefetch(values.get()+node/per_byte,1,1);}
    void add(uint32_t node){
        auto& cell=values.get()[node/per_byte];unsigned shift=(node%per_byte)*Bits,old=(cell>>shift)&mask;
        cell=static_cast<uint8_t>((cell&~(mask<<shift))|(((old+1)&mask)<<shift));
        if(old==mask)spills[node]+=mask+1;
    }
    void accumulate(std::vector<uint32_t>& totals)const{
        size_t full=nodes/per_byte;
        for(size_t i=0;i<full;++i){unsigned cell=values.get()[i];for(unsigned k=0;k<per_byte;++k){totals[i*per_byte+k+1]+=cell&mask;cell>>=Bits;}}
        for(size_t node=full*per_byte;node<nodes;++node)totals[node+1]+=(values.get()[node/per_byte]>>((node%per_byte)*Bits))&mask;
        for(auto [node,count]:spills)totals[size_t(node)+1]+=count;
    }
    void release(){values.reset();decltype(spills)().swap(spills);}
};
