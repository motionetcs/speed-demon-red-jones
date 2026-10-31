#include MAPPED_ALLOCATOR_HEADER
#include <cassert>
#include <cstdio>
#include <memory>
#include <thread>
#include <vector>
#include <unistd.h>

using Values=std::vector<uint32_t,MappedAllocator<uint32_t>>;
static_assert(std::allocator_traits<MappedAllocator<uint32_t>>::is_always_equal::value);
int resident(void* p,size_t bytes,unsigned char* pages){
#ifdef __APPLE__
    return mincore(static_cast<char*>(p),bytes,reinterpret_cast<char*>(pages));
#else
    return mincore(p,bytes,pages);
#endif
}
void lifecycle(size_t count,bool other_thread){
    Values values;
    for(size_t i=0;i<count;++i)values.push_back(uint32_t(i*1000003));
    for(size_t i=0;i<count;++i)assert(values[i]==uint32_t(i*1000003));
    auto* data=values.data();size_t bytes=values.capacity()*sizeof(uint32_t);
    assert(uintptr_t(data)%alignof(uint32_t)==0);
    unsigned char pages[16384];assert((bytes+size_t(sysconf(_SC_PAGESIZE))-1)/size_t(sysconf(_SC_PAGESIZE))<=sizeof(pages));
    assert(resident(data,bytes,pages)==0);
    if(other_thread){std::thread worker([&]{Values().swap(values);});worker.join();}
    else Values().swap(values);
    assert(values.empty()&&values.capacity()==0);
#ifdef __APPLE__
    // Darwin returns status0 for holes; inspect the physical-residency bits.
    assert(resident(data,bytes,pages)==0);
    for(size_t i=0;i<(bytes+size_t(sysconf(_SC_PAGESIZE))-1)/size_t(sysconf(_SC_PAGESIZE));++i)
        assert((pages[i]&MINCORE_INCORE)==0);
#else
    assert(resident(data,bytes,pages)!=0);
#endif
}
int main(){
    for(size_t n:{size_t(1),size_t(1023),size_t(1024),size_t(1025),size_t(100003),size_t(500001)}){
        lifecycle(n,false);lifecycle(n,true);
    }
    bool overflow=false;
    try{MappedAllocator<uint32_t> allocator;allocator.allocate(SIZE_MAX/sizeof(uint32_t)+1);}
    catch(const std::bad_array_new_length&){overflow=true;}
    assert(overflow);
    std::vector<std::thread> workers;
    for(unsigned worker=0;worker<12;++worker)workers.emplace_back([worker]{
        for(unsigned round=0;round<16;++round){Values v(1000+round*79,worker+round);assert(v.front()==worker+round&&v.back()==worker+round);}
    });
    for(auto& worker:workers)worker.join();
    std::puts("PASS mapped vector growth, alignment, overflow, direct OS release and cross-thread destruction");
}
