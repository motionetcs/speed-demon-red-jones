#ifndef PRIVATE_DEGREES_HEADER
#error Explicit private degree candidate header required
#endif
#include PRIVATE_DEGREES_HEADER
#include <cassert>
#include <iostream>
#include <random>
#include <thread>
#include <unistd.h>

void released(uint8_t* address,size_t bytes){
    unsigned char state[16384];size_t pages=(bytes+size_t(sysconf(_SC_PAGESIZE))-1)/size_t(sysconf(_SC_PAGESIZE));assert(pages<=sizeof(state));
#ifdef __APPLE__
    assert(mincore(reinterpret_cast<char*>(address),bytes,reinterpret_cast<char*>(state))==0);for(size_t i=0;i<pages;++i)assert((state[i]&MINCORE_INCORE)==0);
#else
    assert(mincore(address,bytes,state)!=0);
#endif
}
template<unsigned Bits> void model(){
    for(uint32_t n:{0U,1U,2U,3U,4U,5U,15U,16U,17U,4095U,4096U,4097U,65535U,65536U,65537U}){
        PrivateDegrees<Bits> d(n);std::vector<uint32_t> expected(size_t(n)+1),actual(size_t(n)+1);
        if(n){for(uint32_t step=0;step<20000;++step){uint32_t node=static_cast<uint32_t>((uint64_t(step)*47+step/3)%n);d.prefetch(node);d.add(node);++expected[size_t(node)+1];}for(unsigned k=0;k<180000;++k){d.add(n-1);++expected[n];}}
        d.accumulate(actual);assert(actual==expected);
        if(n){auto* data=d.values.get();size_t bytes=d.values.get_deleter().bytes;d.release();assert(!d.values&&d.spills.empty());released(data,bytes);}else d.release();
    }
    for(unsigned workers=1;workers<=12;++workers){
        constexpr uint32_t n=4097;std::vector<PrivateDegrees<Bits>> local;local.reserve(workers);for(unsigned w=0;w<workers;++w)local.emplace_back(n);
        std::vector<std::vector<uint32_t>> reference(workers,std::vector<uint32_t>(n));std::vector<std::thread> threads;
        for(unsigned w=0;w<workers;++w)threads.emplace_back([&,w]{std::mt19937 rng(0x152000+w);for(unsigned k=0;k<50000;++k){uint32_t node=k%7?static_cast<uint32_t>(rng()%n):4096;local[w].add(node);++reference[w][node];}});
        for(auto& t:threads)t.join();std::vector<uint32_t> actual(n+1),expected(n+1);
        for(unsigned w=0;w<workers;++w){local[w].accumulate(actual);for(size_t node=0;node<n;++node)expected[node+1]+=reference[w][node];local[w].release();}
        assert(actual==expected);for(size_t i=1;i<=n;++i){actual[i]+=actual[i-1];expected[i]+=expected[i-1];}assert(actual==expected&&actual.back()==workers*50000U);
    }
    PrivateDegrees<Bits> limit(1);limit.values.get()[0]=static_cast<uint8_t>(PrivateDegrees<Bits>::mask);limit.spills[0]=UINT32_MAX-PrivateDegrees<Bits>::mask;std::vector<uint32_t> totals(2);limit.accumulate(totals);assert(totals[0]==0&&totals[1]==UINT32_MAX);limit.release();
    PrivateDegrees<Bits> moving(4097);for(unsigned i=0;i<65537;++i)moving.add(4096);auto* data=moving.values.get();size_t bytes=moving.values.get_deleter().bytes;
    std::thread other([owned=std::move(moving),data,bytes]()mutable{std::vector<uint32_t> count(4098);owned.accumulate(count);assert(count[4097]==65537);owned.release();released(data,bytes);});other.join();assert(!moving.values);
}
int main(){model<2>();model<4>();model<8>();std::cout<<"PASS private2/4/8 packed neighbors/partial blocks/exact wraps/spills/180000-degree/UINT32 endpoint, every1..12 private-owner reduction/prefix, mapped RAII release/move/cross-thread lifetime\n";}
