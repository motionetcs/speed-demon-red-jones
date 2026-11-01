#include DISTANCE_MAP_HEADER
#include <array>
#include <cassert>
#include <iostream>
#include <thread>

struct alignas(128) LargeAlignment { uint64_t value=0; };

int main(){
    size_t checks=0;
    for(size_t size:std::array<size_t,18>{0,1,2,7,8,15,16,17,31,32,63,64,65,511,512,4095,4096,65537}){
        FastDistances::PackedWords first(size);
        if(first.data())assert(reinterpret_cast<uintptr_t>(first.data())%64==0);
        for(size_t i=0;i<size;++i){assert(first[i]==0);first[i]=static_cast<uint32_t>(i*0x9e3779b1U);++checks;}
        auto copied=first;assert(copied==first);
        if(copied.data())assert(reinterpret_cast<uintptr_t>(copied.data())%64==0);
        auto moved=std::move(first);assert(moved==copied);
        first=moved;assert(first==copied);first.swap(moved);
        first.resize(size*2+17);assert(reinterpret_cast<uintptr_t>(first.data())%64==0);
        for(size_t i=0;i<size;++i){assert(first[i]==copied[i]);++checks;}
        for(size_t i=size;i<first.size();++i){assert(first[i]==0);++checks;}
    }
    CacheLineAllocator<uint32_t> allocator;bool overflow=false;
    try{auto pointer=allocator.allocate(SIZE_MAX/sizeof(uint32_t)+1);allocator.deallocate(pointer,0);}catch(const std::bad_array_new_length&){overflow=true;}
    assert(overflow);
    std::vector<LargeAlignment,CacheLineAllocator<LargeAlignment>> large(19);
    assert(reinterpret_cast<uintptr_t>(large.data())%128==0);
    for(const auto& item:large)assert(item.value==0);
    for(unsigned bits=0;bits<=20;++bits){
        FastDistances map;map.bits=bits;map.labels.assign(size_t(8)<<bits,0);map.reset();
        assert(reinterpret_cast<uintptr_t>(map.labels.data())%64==0);
        uint32_t last=(1U<<21)-1;
        assert(map.improve(last,map.distance_mask()-1));assert(map.labels[map.slot(last)]==UINT32_MAX);
        assert(map.get(last)==map.distance_mask()-1);map.reset();assert(map.get(last)==UINT64_MAX);++checks;
    }
    std::array<std::thread,12> workers;
    for(size_t worker=0;worker<workers.size();++worker)workers[worker]=std::thread([worker]{
        for(unsigned round=0;round<8;++round){FastDistances map;map.reset();
            for(uint32_t i=0;i<12000;++i){uint32_t node=(i*0x9e3779b1U)&((1U<<21)-1);assert(map.improve(node,i+worker));assert(map.get(node)==i+worker);}
            assert(reinterpret_cast<uintptr_t>(map.labels.data())%64==0);
            map.reset();for(uint32_t i=0;i<12000;++i)assert(map.get((i*0x9e3779b1U)&((1U<<21)-1))==UINT64_MAX);
        }
    });
    for(auto& worker:workers)worker.join();
    std::cout<<"PASS aligned labels: "<<checks<<" zero/value/copy/move/resize checks; overflow exception,128alignment, everybits0..20/boundaryword,12threads/96lifetimes/1152000inserts+reads+resetabsence\n";
}
