#include "names.hpp"
#include <chrono>
#include <cstddef>
#include <cstdlib>
#include <exception>
#include <iostream>
#include <new>
#include <set>
#include <string>
#include <thread>

#if defined(__SANITIZE_ADDRESS__) || defined(__SANITIZE_THREAD__) || defined(__SANITIZE_UNDEFINED__)
#error Allocation replacement is a separate plain test; run the ordinary shared model with sanitizers instead.
#endif
#if defined(__has_feature)
#if __has_feature(address_sanitizer) || __has_feature(thread_sanitizer) || __has_feature(undefined_behavior_sanitizer)
#error Allocation replacement is a separate plain test; do not suppress instrumentation to compile it.
#endif
#endif
#ifndef __cpp_aligned_new
#error This test requires standard over-aligned allocation support.
#endif

namespace allocation_test {
enum class Mode{off,delay_block,fail_block,fail_second_normal};
thread_local Mode mode=Mode::off;thread_local size_t normal_count=0;thread_local void* first_normal=nullptr;thread_local bool first_normal_freed=false;
struct Gate{std::atomic<bool> entered{false},release{false};} gate;
void* allocate(size_t bytes,size_t alignment,bool aligned){
    if(!aligned&&mode==Mode::fail_second_normal){++normal_count;if(normal_count==2)throw std::bad_alloc();}
    if(aligned&&alignment==alignof(SharedNames::Key)&&(mode==Mode::delay_block||mode==Mode::fail_block)){
        gate.entered.store(true,std::memory_order_release);
        while(!gate.release.load(std::memory_order_acquire))std::this_thread::yield();
        if(mode==Mode::fail_block)throw std::bad_alloc();
    }
    void* result=nullptr;if(!bytes)bytes=1;
    if(aligned){if(posix_memalign(&result,alignment,bytes)!=0)throw std::bad_alloc();}
    else{result=std::malloc(bytes);if(!result)throw std::bad_alloc();}
    if(!aligned&&mode==Mode::fail_second_normal&&normal_count==1)first_normal=result;
    return result;
}
void deallocate(void* pointer)noexcept{if(mode==Mode::fail_second_normal&&pointer==first_normal)first_normal_freed=true;std::free(pointer);}
}
void* operator new(size_t n){return allocation_test::allocate(n,alignof(std::max_align_t),false);}
void* operator new[](size_t n){return allocation_test::allocate(n,alignof(std::max_align_t),false);}
void* operator new(size_t n,std::align_val_t a){return allocation_test::allocate(n,static_cast<size_t>(a),true);}
void* operator new[](size_t n,std::align_val_t a){return allocation_test::allocate(n,static_cast<size_t>(a),true);}
void operator delete(void* p)noexcept{allocation_test::deallocate(p);}
void operator delete[](void* p)noexcept{allocation_test::deallocate(p);}
void operator delete(void* p,size_t)noexcept{allocation_test::deallocate(p);}
void operator delete[](void* p,size_t)noexcept{allocation_test::deallocate(p);}
void operator delete(void* p,std::align_val_t)noexcept{allocation_test::deallocate(p);}
void operator delete[](void* p,std::align_val_t)noexcept{allocation_test::deallocate(p);}
void operator delete(void* p,size_t,std::align_val_t)noexcept{allocation_test::deallocate(p);}
void operator delete[](void* p,size_t,std::align_val_t)noexcept{allocation_test::deallocate(p);}

namespace {
size_t checks=0;
void require(bool good,const char* message){if(!good)throw std::runtime_error(message);++checks;}
template<class Predicate>bool wait_for(Predicate predicate){
    auto limit=std::chrono::steady_clock::now()+std::chrono::seconds(5);
    while(!predicate()){if(std::chrono::steady_clock::now()>=limit)return false;std::this_thread::yield();}return true;
}
struct Outcome{bool fresh=false,canceled=false,bad_alloc=false;std::exception_ptr error;};
void delayed_block(bool fail){
    using allocation_test::Mode;constexpr size_t workers=12,different=6;
    std::vector<KeyArena> arenas(workers);SharedNames names(2048,257);std::vector<std::string> keys;
    for(size_t i=0;i<=different;++i)keys.push_back("gate-key/"+std::to_string(i));
    std::vector<Outcome> outcomes(workers);std::vector<std::thread> threads;threads.reserve(workers);
    std::atomic<size_t> started{0},finished{0};allocation_test::gate.entered.store(false);allocation_test::gate.release.store(false);
    auto body=[&](size_t worker){
        if(worker==0)allocation_test::mode=fail?Mode::fail_block:Mode::delay_block;
        started.fetch_add(1,std::memory_order_relaxed);size_t key=worker<=different?worker:0;
        uint64_t hash=(uint64_t(key+1)<<32)|key;
        try{outcomes[worker].fresh=names.first(keys[key],0,hash,arenas[worker]);}
        catch(const SharedCanceled&){outcomes[worker].canceled=true;}
        catch(const std::bad_alloc&){names.canceled.store(true,std::memory_order_relaxed);outcomes[worker].bad_alloc=true;}
        catch(...){names.canceled.store(true,std::memory_order_relaxed);outcomes[worker].error=std::current_exception();}
        allocation_test::mode=Mode::off;finished.fetch_add(1,std::memory_order_relaxed);
    };
    threads.emplace_back(body,0);
    if(!wait_for([&]{return allocation_test::gate.entered.load(std::memory_order_acquire);})){names.canceled.store(true);allocation_test::gate.release.store(true);threads[0].join();throw std::runtime_error("aligned block allocation hook not observed");}
    try{for(size_t worker=1;worker<workers;++worker)threads.emplace_back(body,worker);}
    catch(...){names.canceled.store(true);allocation_test::gate.release.store(true);for(auto& thread:threads)thread.join();throw;}
    bool reserved=wait_for([&]{return started.load()>=workers&&names.used.load()>=different+1;});
    bool unpublished=names.published[0].load(std::memory_order_acquire)==nullptr;
    bool none_finished=finished.load()==0;
    if(!reserved)names.canceled.store(true);
    allocation_test::gate.release.store(true,std::memory_order_release);for(auto& thread:threads)thread.join();
    require(reserved&&unpublished&&none_finished,"delayed-owner precondition failed");
    for(const auto& outcome:outcomes)if(outcome.error)std::rethrow_exception(outcome.error);
    if(fail){
        require(outcomes[0].bad_alloc,"block owner did not report forced allocation failure");
        for(size_t worker=1;worker<workers;++worker)require(outcomes[worker].canceled&&!outcomes[worker].bad_alloc,"peer did not exit via cancellation");
        require(names.canceled.load()&&!names.too_small.load(),"block failure cancellation cause mismatch");
        require(names.published[0].load()==nullptr,"failed allocation published a block");
        for(size_t i=0;i<names.capacity*2;++i)require(names.slots[i].load()<=1,"failed block exposed a ready key");
    }else{
        size_t fresh=0;for(const auto& outcome:outcomes){require(!outcome.canceled&&!outcome.bad_alloc,"successful delayed block canceled");fresh+=outcome.fresh;}
        require(fresh==different+1&&names.used.load()==different+1,"delayed block fresh totals mismatch");
        for(size_t key=0;key<=different;++key)require(!names.first(keys[key],0,(uint64_t(key+1)<<32)|key,arenas[0]),"delayed key replay became fresh");
    }
}
void arena_vector_failure(){
    using allocation_test::Mode;KeyArena arena;const std::string key(80,'v');
    allocation_test::normal_count=0;allocation_test::first_normal=nullptr;allocation_test::first_normal_freed=false;allocation_test::mode=Mode::fail_second_normal;
    bool failed=false;
    try{static_cast<void>(arena.copy(key));}catch(const std::bad_alloc&){failed=true;}catch(...){allocation_test::mode=Mode::off;throw;}
    const size_t calls=allocation_test::normal_count;const bool owned=allocation_test::first_normal!=nullptr;const bool freed=allocation_test::first_normal_freed;allocation_test::mode=Mode::off;
    require(failed&&calls==2&&owned,"arena allocation sequence precondition changed");require(freed,"character array leaked when vector insertion failed");require(arena.blocks.empty(),"failed vector insertion retained an invalid block");
    const char* copy=arena.copy(key);require(std::string_view(copy,key.size())==key,"arena unusable after failed insertion");
}
}
int main(){try{delayed_block(false);delayed_block(true);arena_vector_failure();std::cout<<"PASS shared allocation/block-delay/cancel/arena-RAII model "<<checks<<" checks\n";}catch(const std::exception& error){allocation_test::mode=allocation_test::Mode::off;allocation_test::gate.release.store(true);std::cerr<<"FAIL shared allocation model: "<<error.what()<<'\n';return 1;}}
