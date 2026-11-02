#include "source/track-c/io.hpp"
#include "source/track-c/names.hpp"
#include "source/track-c/parallel.hpp"
#include <cassert>
#include <chrono>
#include <future>
#include <iostream>
#include <limits>
#include <string>
#include <vector>
static_assert(std::__platform_wait_uses_type<uint32_t>);
static_assert(!std::__platform_wait_uses_type<uint64_t>);
static size_t checks=0;
static void verify(bool value){assert(value);++checks;}
static void done(std::future<void>& future){verify(future.wait_for(std::chrono::seconds(3))==std::future_status::ready);future.get();}
static NameEvent event(unsigned reader,unsigned seq,const std::vector<std::string>& keys){return {keys[(reader+seq)%keys.size()],(uint64_t(reader)<<48)|seq,static_cast<uint16_t>(seq%17577)};}
static bool equal(const NameEvent&a,const NameEvent&b){return a.key==b.key&&a.hash==b.hash&&a.country==b.country;}
static void transfer(unsigned total,size_t capacity,const std::vector<std::string>& keys){
    unsigned readers=std::clamp(total*8/12,1U,total-1),owners=total-readers;auto queues=std::make_unique<NameQueue[]>(size_t(readers)*owners);auto wakes=std::make_unique<NameWake[]>(owners);std::atomic<bool> canceled{false};
#include "cancel_body.inc"
    for(unsigned owner=0;owner<owners;++owner)wakes[owner].epoch.store(UINT32_MAX-3,std::memory_order_relaxed);
    size_t count=capacity*7+17;std::vector<std::vector<NameEvent>> expected(size_t(readers)*owners);std::vector<size_t> consumed(size_t(readers)*owners);
    for(unsigned reader=0;reader<readers;++reader)for(unsigned seq=0;seq<count;++seq){auto e=event(reader,seq,keys);expected[size_t(reader)*owners+e.hash%owners].push_back(e);}
    parallel(total,[&](unsigned worker){try{
        if(worker<readers){
            std::vector<std::vector<NameEvent>> batches(owners);for(auto& b:batches)b.reserve(capacity);
            for(unsigned seq=0;seq<count;++seq){auto e=event(worker,seq,keys);unsigned owner=e.hash%owners;auto& batch=batches[owner];batch.push_back(e);if(batch.size()==capacity)queues[size_t(worker)*owners+owner].send(batch,canceled,wakes[owner]);}
            for(unsigned owner=0;owner<owners;++owner){auto& batch=batches[owner];auto& q=queues[size_t(worker)*owners+owner];if(!batch.empty())q.send(batch,canceled,wakes[owner]);q.send(batch,canceled,wakes[owner]);}
        }else{
            unsigned owner=worker-readers;std::array<bool,12> finished{};unsigned remaining=readers;
            while(remaining){
                uint32_t stamp=wakes[owner].epoch.load(std::memory_order_acquire);if(canceled.load(std::memory_order_acquire))throw std::runtime_error("canceled model");bool progress=false;
                for(unsigned reader=0;reader<readers;++reader){
                    if(finished[reader])continue;
                    auto& q=queues[size_t(reader)*owners+owner];unsigned state=q.state.load(std::memory_order_acquire);if(state==2)throw std::runtime_error("canceled model");if(state!=1)continue;progress=true;
                    if(q.rows.empty()){finished[reader]=true;--remaining;}else for(const auto& e:q.rows){size_t k=size_t(reader)*owners+owner;assert(consumed[k]<expected[k].size()&&equal(e,expected[k][consumed[k]]));++consumed[k];}
                    q.rows.clear();q.retire();
                }
                if(!progress&&remaining)wakes[owner].epoch.wait(stamp,std::memory_order_acquire);
            }
        }
    }catch(...){cancel_pipeline();throw;}},cancel_pipeline);
    for(size_t i=0;i<consumed.size();++i){verify(consumed[i]==expected[i].size());verify(queues[i].state.load()==0);verify(queues[i].rows.empty());}verify(!canceled.load());
}
static void transitions(const std::vector<std::string>& keys){
    unsigned readers=1,owners=1;auto queues=std::make_unique<NameQueue[]>(1);auto wakes=std::make_unique<NameWake[]>(1);std::atomic<bool> canceled{false};
#include "cancel_body.inc"
    auto& q=queues[0];auto& wake=wakes[0];std::vector<NameEvent> first{event(0,1,keys)},second{event(0,2,keys)};q.send(first,canceled,wake);verify(q.state.load()==1&&q.rows.size()==1);
    std::promise<void> entered;auto ready=entered.get_future();auto producer=std::async(std::launch::async,[&]{entered.set_value();q.send(second,canceled,wake);});ready.get();verify(producer.wait_for(std::chrono::milliseconds(5))==std::future_status::timeout);verify(equal(q.rows[0],event(0,1,keys)));q.rows.clear();q.retire();done(producer);verify(q.state.load()==1&&equal(q.rows[0],event(0,2,keys)));q.rows.clear();q.retire();
    std::vector<NameEvent> third{event(0,3,keys)},fourth{event(0,4,keys)};q.send(third,canceled,wake);std::promise<void> blocked;auto blocked_ready=blocked.get_future();auto canceled_sender=std::async(std::launch::async,[&]{blocked.set_value();bool threw=false;try{q.send(fourth,canceled,wake);}catch(const std::runtime_error&){threw=true;}assert(threw);});blocked_ready.get();verify(canceled_sender.wait_for(std::chrono::milliseconds(5))==std::future_status::timeout);cancel_pipeline();done(canceled_sender);verify(q.state.load()==2&&equal(q.rows[0],event(0,3,keys)));q.rows.clear();q.retire();verify(q.state.load()==2);unsigned empty=0;verify(!q.state.compare_exchange_strong(empty,1));verify(empty==2&&q.state.load()==2);bool threw=false;try{q.send(fourth,canceled,wake);}catch(const std::runtime_error&){threw=true;}verify(threw&&q.state.load()==2);
}
static void active_cancel(const std::vector<std::string>& keys){
    unsigned readers=1,owners=1;auto queues=std::make_unique<NameQueue[]>(1);auto wakes=std::make_unique<NameWake[]>(1);std::atomic<bool> canceled{false};
#include "cancel_body.inc"
    auto& q=queues[0];std::vector<NameEvent> batch;for(unsigned i=0;i<512;++i)batch.push_back(event(0,i,keys));q.send(batch,canceled,wakes[0]);std::promise<void> inside,release;auto inside_ready=inside.get_future();auto released=release.get_future();auto consumer=std::async(std::launch::async,[&]{assert(q.state.load(std::memory_order_acquire)==1);inside.set_value();released.get();for(unsigned i=0;i<512;++i)assert(equal(q.rows[i],event(0,i,keys)));q.rows.clear();q.retire();});inside_ready.get();std::array<std::thread,4> cancelers;for(auto& thread:cancelers)thread=std::thread([&]{cancel_pipeline();});for(auto& thread:cancelers)thread.join();bool threw=false;try{q.send(batch,canceled,wakes[0]);}catch(const std::runtime_error&){threw=true;}verify(threw&&q.state.load()==2);release.set_value();done(consumer);verify(q.state.load()==2&&q.rows.empty());
}
static void wake_cases(const std::vector<std::string>& keys){
    for(uint32_t initial:{uint32_t(0),UINT32_MAX-1,UINT32_MAX}){
        NameQueue q;NameWake wake;std::atomic<bool> canceled{false};wake.epoch.store(initial);uint32_t stamp=wake.epoch.load(std::memory_order_acquire);std::vector<NameEvent> batch{event(0,5,keys)};q.send(batch,canceled,wake);auto owner=std::async(std::launch::async,[&]{wake.epoch.wait(stamp,std::memory_order_acquire);assert(q.state.load(std::memory_order_acquire)==1);assert(equal(q.rows[0],event(0,5,keys)));q.rows.clear();q.retire();});done(owner);verify(wake.epoch.load()==initial+1&&q.state.load()==0);
    }
    for(bool before:{false,true}){
        unsigned readers=1,owners=1;auto queues=std::make_unique<NameQueue[]>(1);auto wakes=std::make_unique<NameWake[]>(1);std::atomic<bool> canceled{false};
#include "cancel_body.inc"
        if(before)cancel_pipeline();
        std::promise<void> armed;auto started=armed.get_future();auto owner=std::async(std::launch::async,[&]{uint32_t stamp=wakes[0].epoch.load(std::memory_order_acquire);armed.set_value();if(!canceled.load(std::memory_order_acquire))wakes[0].epoch.wait(stamp,std::memory_order_acquire);assert(canceled.load(std::memory_order_acquire));assert(queues[0].state.load(std::memory_order_acquire)==2);});started.get();if(!before)cancel_pipeline();done(owner);verify(queues[0].state.load()==2);
    }
}
static void race_cases(const std::vector<std::string>& keys){
    for(unsigned trial=0;trial<350;++trial){
        unsigned readers=1,owners=1;auto queues=std::make_unique<NameQueue[]>(1);auto wakes=std::make_unique<NameWake[]>(1);std::atomic<bool> canceled{false};
#include "cancel_body.inc"
        std::atomic<bool> start{false};auto producer=std::async(std::launch::async,[&]{while(!start.load(std::memory_order_acquire))std::this_thread::yield();std::vector<NameEvent> batch{event(0,trial,keys)};try{queues[0].send(batch,canceled,wakes[0]);}catch(const std::runtime_error&){};});start.store(true,std::memory_order_release);if(trial&1)std::this_thread::yield();cancel_pipeline();done(producer);verify(queues[0].state.load()==2);queues[0].retire();verify(queues[0].state.load()==2);
    }
}
int main(){
    std::vector<std::string> keys{"",std::string("a\0b",3),"line\nnext","a\"\"b","trailing ","UTF8 \xe5\x90\x8d",std::string(1<<20,'q')};for(unsigned i=0;i<251;++i)keys.push_back("key/"+std::to_string(i));
    for(unsigned total=2;total<=12;++total)for(size_t capacity:{size_t(1),size_t(7),size_t(511),size_t(512)})transfer(total,capacity,keys);
    transitions(keys);active_cancel(keys);wake_cases(keys);race_cases(keys);
    std::cout<<"PASS357 actual queue/owner epoch/extracted cancellation, ordered batch EOF/all2..12 roles, blocked producer, sticky terminal CAS, active consumer, simultaneous cancel, before/after stamp, uint64 wrap seam and actual send/cancel races "<<checks<<" checks\n";
}
