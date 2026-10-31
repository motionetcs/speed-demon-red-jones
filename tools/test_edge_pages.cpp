#include <sys/mman.h>
#if defined(__linux__)
static constexpr int huge_advice=MADV_HUGEPAGE;
#endif
#if defined(TEST_ADVICE_ABSENT)
#undef MADV_HUGEPAGE
#endif
#include EDGE_PAGES_HEADER
#include <atomic>
#include <cassert>
#include <cerrno>
#include <iostream>
#include <memory>
#include <thread>
#include <type_traits>
#include <vector>
#include <unistd.h>

#if defined(TEST_WRAP_SYSCALLS)
static std::atomic<bool> fail_map{false},deny_advice{false};
static std::atomic<size_t> maps{0},unmaps{0},advice_calls{0},advice_failures{0};
static std::atomic<size_t> last_map_bytes{0},last_advice_bytes{0};
static std::atomic<uintptr_t> last_map_address{0},last_advice_address{0};
extern "C" void* __real_mmap(void*,size_t,int,int,int,off_t);
extern "C" int __real_munmap(void*,size_t);
extern "C" int __real_madvise(void*,size_t,int);
extern "C" void* __wrap_mmap(void* p,size_t n,int prot,int flags,int fd,off_t off){
    if(fail_map.load()){errno=ENOMEM;return MAP_FAILED;}
    assert(p==nullptr&&prot==(PROT_READ|PROT_WRITE)&&flags==(MAP_PRIVATE|MAP_ANONYMOUS)&&fd==-1&&off==0);
    void* result=__real_mmap(p,n,prot,flags,fd,off);if(result!=MAP_FAILED){++maps;last_map_bytes=n;last_map_address=reinterpret_cast<uintptr_t>(result);}return result;
}
extern "C" int __wrap_munmap(void* p,size_t n){int result=__real_munmap(p,n);assert(result==0);++unmaps;return result;}
extern "C" int __wrap_madvise(void* p,size_t n,int advice){
    assert(advice==huge_advice&&n>=2*1024*1024&&reinterpret_cast<uintptr_t>(p)%size_t(sysconf(_SC_PAGESIZE))==0);
    assert(reinterpret_cast<uintptr_t>(p)==last_map_address.load()&&n==last_map_bytes.load());
    ++advice_calls;last_advice_bytes=n;last_advice_address=reinterpret_cast<uintptr_t>(p);
    if(deny_advice.load()){++advice_failures;errno=EINVAL;return -1;}return __real_madvise(p,n,advice);
}
#endif
struct __attribute__((packed)) Wide {uint32_t to;uint16_t tag;};
static_assert(sizeof(Wide)==6);
template<class T> T value(size_t i){if constexpr(std::is_same_v<T,uint32_t>)return uint32_t(i*1000003);else return Wide{uint32_t(i*1000003),uint16_t(i*73)};}
template<class T> bool same(T item,size_t i){if constexpr(std::is_same_v<T,uint32_t>)return item==uint32_t(i*1000003);else {uint32_t to=item.to;uint16_t tag=item.tag;return to==uint32_t(i*1000003)&&tag==uint16_t(i*73);}}
static void released(void* p,size_t bytes){
    unsigned char state[16384];size_t pages=(bytes+size_t(sysconf(_SC_PAGESIZE))-1)/size_t(sysconf(_SC_PAGESIZE));assert(pages<=sizeof(state));
#ifdef __APPLE__
    assert(mincore(static_cast<char*>(p),bytes,reinterpret_cast<char*>(state))==0);for(size_t i=0;i<pages;++i)assert((state[i]&MINCORE_INCORE)==0);
#else
    assert(mincore(p,bytes,state)!=0);
#endif
}
template<class T> void lifecycle(size_t n){
    using Values=std::vector<T,EdgePages<T>>;static_assert(std::allocator_traits<EdgePages<T>>::is_always_equal::value);
#if defined(TEST_WRAP_SYSCALLS)
    size_t before=advice_calls.load();
#endif
    Values values(n);for(size_t i=0;i<n;++i)values[i]=value<T>(i);for(size_t i=0;i<n;++i)assert(same(values[i],i));
    if(!n)return;auto* data=values.data();size_t bytes=values.capacity()*sizeof(T);assert(reinterpret_cast<uintptr_t>(data)%size_t(sysconf(_SC_PAGESIZE))==0);
#if defined(TEST_WRAP_SYSCALLS)
#if defined(MADV_HUGEPAGE)
    assert(advice_calls.load()==before+(bytes>=2*1024*1024));if(bytes>=2*1024*1024){assert(last_advice_address==reinterpret_cast<uintptr_t>(data)&&last_advice_bytes==bytes);}
#else
    assert(advice_calls.load()==before);
#endif
#endif
    // Move allocator ownership, then release on another joined thread.
    Values moved=std::move(values);assert(values.empty());std::thread other([&]{for(size_t i=0;i<n;++i)assert(same(moved[i],i));Values().swap(moved);});other.join();assert(moved.empty());released(data,bytes);
}
int main(){
    EdgePages<uint32_t> allocator;assert(allocator.allocate(0)==nullptr);allocator.deallocate(nullptr,0);
    bool overflow=false;try{allocator.allocate(SIZE_MAX/sizeof(uint32_t)+1);}catch(const std::bad_array_new_length&){overflow=true;}assert(overflow);
    for(bool denied:{false,true}){
#if defined(TEST_WRAP_SYSCALLS)
        deny_advice=denied;
#else
        (void)denied;
#endif
        for(size_t n:{0U,1U,1023U,1024U,1025U,4095U,4096U,4097U,349525U,349526U,524287U,524288U,524289U,1048577U}){lifecycle<uint32_t>(n);lifecycle<Wide>(n);}
    }
#if defined(TEST_WRAP_SYSCALLS)
    deny_advice=false;fail_map=true;bool failed=false;try{allocator.allocate(16);}catch(const std::bad_alloc&){failed=true;}assert(failed);fail_map=false;
    {std::vector<uint32_t,EdgePages<uint32_t>> held(1024,42);fail_map=true;failed=false;try{held.reserve(8192);}catch(const std::bad_alloc&){failed=true;}assert(failed&&held.size()==1024&&held.front()==42&&held.back()==42);fail_map=false;}
#endif
    {std::vector<uint32_t,EdgePages<uint32_t>> growing;for(size_t i=0;i<100003;++i)growing.push_back(uint32_t(i));for(size_t i=0;i<growing.size();++i)assert(growing[i]==i);}
    std::vector<std::thread> workers;for(unsigned w=0;w<12;++w)workers.emplace_back([w]{for(unsigned k=0;k<32;++k){std::vector<uint32_t,EdgePages<uint32_t>> v(4097+k,w+k);assert(v.front()==w+k&&v.back()==w+k);}});for(auto& t:workers)t.join();
#if defined(TEST_WRAP_SYSCALLS)
    assert(maps==unmaps);
#if defined(MADV_HUGEPAGE)
    assert(advice_calls>0&&advice_failures>0);
#else
    assert(advice_calls==0);
#endif
    std::cout<<"observed test-only maps="<<maps<<" unmaps="<<unmaps<<" optional_advice="<<advice_calls<<" simulated_advice_errors="<<advice_failures<<"\n";
#endif
    std::cout<<"PASS exact compact/wide allocator values/growth/alignment/overflow, normal mmap failure and vector preservation, owned direct release/move/cross-thread lifetime, optional advice/simulated failure/feature-absence branches\n";
}
