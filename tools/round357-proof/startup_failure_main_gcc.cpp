#include "source/track-c/io.hpp"
#ifndef PARALLEL_HEADER
#define PARALLEL_HEADER "source/track-c/parallel.hpp"
#endif
#include PARALLEL_HEADER
#include <cassert>
#include <cerrno>
#include <cstdlib>
#include <iostream>
#include <new>
#include <system_error>
#include <atomic>
#ifdef TEST_PTHREAD_WRAP
#include <pthread.h>
#endif
extern std::atomic<bool> allocation_armed;
extern std::atomic<size_t> allocation_count,allocation_target,allocation_hits;
#ifdef TEST_PTHREAD_WRAP
static std::atomic<bool> create_armed{false};
static std::atomic<size_t> create_count{0},create_target{0},create_hits{0};
extern "C" int __real_pthread_create(pthread_t*,const pthread_attr_t*,void*(*)(void*),void*);
extern "C" int __wrap_pthread_create(pthread_t* t,const pthread_attr_t* a,void*(*f)(void*),void* v){
    if(create_armed.load()&&create_count.fetch_add(1)==create_target.load()){
        create_armed.store(false);create_hits.fetch_add(1);return EAGAIN;
    }
    return __real_pthread_create(t,a,f,v);
}
#endif
static size_t cases=0;
static void trial(unsigned total,int allocation_fail,int create_fail){
    std::atomic<bool> stopped{false},normal{false};std::atomic<unsigned> active{0};bool threw=false;
    auto worker=[&](unsigned i){active.fetch_add(1);if(i==0)normal.store(true,std::memory_order_release);else while(!stopped.load(std::memory_order_acquire)&&!normal.load(std::memory_order_acquire))std::this_thread::yield();active.fetch_sub(1);};
    auto cancel=[&]()noexcept{stopped.store(true,std::memory_order_release);};
    (void)cancel;
    allocation_count.store(0);allocation_target.store(allocation_fail<0?0:size_t(allocation_fail));allocation_armed.store(allocation_fail>=0);
#ifdef TEST_PTHREAD_WRAP
    create_count.store(0);create_target.store(create_fail<0?0:size_t(create_fail));create_armed.store(create_fail>=0);
#else
    (void)create_fail;
#endif
    try{
#ifdef CONTROL_OLD
        parallel(total,worker);
#else
        parallel(total,worker,cancel);
#endif
    }catch(const std::bad_alloc&){threw=true;}catch(const std::system_error&){threw=true;}
    allocation_armed.store(false);
#ifdef TEST_PTHREAD_WRAP
    create_armed.store(false);
#endif
    assert(active.load()==0);if(threw)assert(stopped.load());else assert(normal.load());++cases;
}
int main(){
#ifdef CONTROL_OLD
    std::cout<<"CONTROL356 exact old parallel startup: forced second pthread creation failure; expected timeout before worker0/cancel"<<std::endl;
    trial(3,-1,1);return 8;
#else
    for(unsigned total:{2U,6U,12U})for(int ordinal=0;ordinal<24;++ordinal)trial(total,ordinal,-1);
    assert(allocation_hits.load()>0);
#ifdef TEST_PTHREAD_WRAP
    for(unsigned total:{2U,6U,12U})for(unsigned ordinal=0;ordinal<total-1;++ordinal)trial(total,-1,int(ordinal));
    assert(create_hits.load()==17);
#endif
    std::cout<<"PASS356 actual parallel allocation/thread startup cancellation before join "<<cases<<" cases allocation_failures="<<allocation_hits.load();
#ifdef TEST_PTHREAD_WRAP
    std::cout<<" pthread_create_failures="<<create_hits.load();
#endif
    std::cout<<"; test-only fault interposition, never production image\n";
#endif
}
