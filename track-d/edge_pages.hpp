#pragma once
#include <cstddef>
#include <cstdint>
#include <new>
#include <sys/mman.h>

// Each adjacency allocation owns its anonymous pages; advice is optional.
template<class T> struct EdgePages {
    static_assert(alignof(T)<=alignof(std::max_align_t));
    using value_type=T;
    EdgePages()=default;
    template<class U> EdgePages(const EdgePages<U>&) noexcept {}
    T* allocate(size_t n){
        if(n>SIZE_MAX/sizeof(T))throw std::bad_array_new_length();
        if(!n)return nullptr;size_t bytes=n*sizeof(T);
        void* p=mmap(nullptr,bytes,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
        if(p==MAP_FAILED)throw std::bad_alloc();
#if defined(__linux__) && defined(MADV_HUGEPAGE)
        if(bytes>=2*1024*1024)(void)madvise(p,bytes,MADV_HUGEPAGE);
#endif
        return static_cast<T*>(p);
    }
    void deallocate(T* p,size_t n) noexcept{if(p)munmap(p,n*sizeof(T));}
    template<class U> bool operator==(const EdgePages<U>&)const noexcept{return true;}
};
