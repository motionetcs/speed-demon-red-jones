#include <atomic>
#include <cstdlib>
#include <new>
std::atomic<bool> allocation_armed{false};
std::atomic<size_t> allocation_count{0},allocation_target{0},allocation_hits{0};
void* operator new(size_t n){
    if(allocation_armed.load(std::memory_order_relaxed)&&allocation_count.fetch_add(1)==allocation_target.load()){
        allocation_armed.store(false);allocation_hits.fetch_add(1);throw std::bad_alloc();
    }
    if(void* p=std::malloc(n?n:1))return p;
    throw std::bad_alloc();
}
void* operator new[](size_t n){return ::operator new(n);}
void operator delete(void* p)noexcept{std::free(p);}
void operator delete[](void* p)noexcept{std::free(p);}
void operator delete(void* p,size_t)noexcept{std::free(p);}
void operator delete[](void* p,size_t)noexcept{std::free(p);}
