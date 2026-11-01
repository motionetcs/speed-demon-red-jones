#include <array>
#include <algorithm>
#include <cassert>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <stdexcept>
#include <vector>
#include <sys/mman.h>
#include <unistd.h>
#ifdef MODEL_FORCE_SCALAR
#undef __ARM_NEON
#undef __SSE2__
#endif
#include NAMES_HEADER
#include "offset_model.hpp"
#include "index_model.hpp"
#include "route_model.hpp"
uint64_t scalar_mask(const uint32_t* p,uint32_t key){uint64_t mask=0;for(unsigned i=0;i<4;++i)if(p[i]==key)mask|=((uint64_t(1)<<Names::lane_bits)-1)<<(i*Names::lane_bits);return mask;}
void lane_model(){
    uint64_t checks=0;std::array<uint32_t,12> values{};
    for(uint32_t key:{0U,1U,2U,42U,0x80000000U,UINT32_MAX})for(unsigned shift=0;shift<8;++shift)for(unsigned code=0;code<625;++code){
        unsigned n=code;for(unsigned i=0;i<4;++i){unsigned d=n%5;n/=5;values[shift+i]=d==0?key:d==1?0:d==2?UINT32_MAX:d==3?key^0x80000000U:key+1;}
        auto* p=values.data()+shift;uint64_t expected=scalar_mask(p,key),actual=Names::equal_lanes(p,key);assert(actual==expected);
        uint64_t remaining=actual;for(unsigned i=0;i<4;++i)if(p[i]==key){assert(Names::lane(remaining)==i);remaining&=~(((uint64_t(1)<<Names::lane_bits)-1)<<(i*Names::lane_bits));}assert(!remaining);++checks;
    }
    long page=sysconf(_SC_PAGESIZE);assert(page>0);void* memory=mmap(nullptr,size_t(page)*2,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);assert(memory!=MAP_FAILED);assert(mprotect(static_cast<char*>(memory)+page,page,PROT_NONE)==0);
    auto* tail=reinterpret_cast<uint32_t*>(static_cast<char*>(memory)+page-16);for(unsigned bits=0;bits<16;++bits){for(unsigned i=0;i<4;++i)tail[i]=(bits&(1U<<i))?0:UINT32_MAX;assert(Names::equal_lanes(tail,0)==scalar_mask(tail,0));assert(Names::equal_lanes(tail,UINT32_MAX)==scalar_mask(tail,UINT32_MAX));checks+=2;}assert(munmap(memory,size_t(page)*2)==0);
    std::cout<<"PASS group4 lane/empty/full32 masks,first-lane/removal,unaligned groups,guarded16B loads "<<checks<<" checks\n";
}
void group_model(){
    for(uint32_t fp:{0U,1U,2U,3U,42U,UINT32_MAX-3,UINT32_MAX}){
        Names table(257);std::set<std::pair<std::string,size_t>> reference;
        for(unsigned pass=0;pass<3;++pass)for(unsigned i=0;i<257;++i){auto text=key(i);uint64_t hash=(uint64_t(i+1)<<32)|fp;size_t c=(i+pass/2)%257;assert(table.first(text,c,hash)==reference.emplace(text,c).second);}
        // Equal home at the final group forces full groups,wrap and exact full-key collisions.
        for(unsigned i=0;i<513;++i){auto text=key(i+10000);uint64_t hash=(uint64_t(i+1)<<32)|(uint32_t(4095*4)+(fp&3));assert(table.first(text,256,hash));}
        for(unsigned repeat=0;repeat<3;++repeat){table.grow();for(const auto& value:reference){unsigned i=0;while(key(i)!=value.first)++i;uint64_t hash=(uint64_t(i+1)<<32)|fp;assert(!table.first(value.first,value.second,hash));}}
        for(const auto& group:table.entries){bool empty=false;for(unsigned i=0;i<4;++i){if(!group.indices[i])empty=true;else assert(!empty);}}
        assert(table.used==770);
    }
    std::cout<<"PASS group4 forced full-fingerprint0/1/MAX collisions,final-group wrap,dense-prefix,growth/reference membership\n";
}
int main(){lane_model();group_model();run_offset_name_model<Names>();run_index_model();run_route_model();}
