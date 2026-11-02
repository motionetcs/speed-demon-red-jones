#pragma once
#include <cstddef>
#include <cstdint>
#include <new>
#include <sys/mman.h>

// Stateless vector storage; completed-hour buffers return directly to the OS.
template<class T> struct MappedAllocator {
    static_assert(alignof(T)<=alignof(std::max_align_t));
    using value_type=T;
    MappedAllocator()=default;
    template<class U> MappedAllocator(const MappedAllocator<U>&) noexcept {}
    T* allocate(size_t n) {
        if(n>SIZE_MAX/sizeof(T))throw std::bad_array_new_length();
        if(!n)return nullptr;
        void* p=mmap(nullptr,n*sizeof(T),PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
        if(p==MAP_FAILED)throw std::bad_alloc();
        return static_cast<T*>(p);
    }
    void deallocate(T* p,size_t n) noexcept {if(p)munmap(p,n*sizeof(T));}
    template<class U> bool operator==(const MappedAllocator<U>&)const noexcept{return true;}
};
