#ifndef NAMES_HEADER
#error Explicit multi-producer candidate header required
#endif
#include NAMES_HEADER
#include <cassert>
#include <iostream>
#include <string>
#include <thread>
#include <vector>

std::vector<std::string> keys;
NameEvent token(unsigned reader,unsigned owner,uint32_t ordinal){uint64_t id=(uint64_t(reader)<<40)|(uint64_t(owner)<<32)|ordinal;return {keys[id%keys.size()],id,static_cast<uint16_t>(id%17577)};}
constexpr size_t sizes[]={1,63,64,65,127,128,129,255,256,257,511,512,513,1025};
void transport(unsigned readers,unsigned owners,uint64_t beginning){
    auto queues=std::make_unique<NameQueue[]>(owners);std::atomic<bool> canceled{false};
    for(unsigned o=0;o<owners;++o){auto& q=queues[o];q.published.store(beginning);q.consumed.store(beginning);assert(!q.receive());for(size_t k=0;k<NameQueue::capacity;++k){std::vector<NameEvent> v{token(0,o,static_cast<uint32_t>(k))};q.send(v,canceled);assert(v.empty());}}
    constexpr unsigned rounds=48;std::vector<uint32_t> total(readers);
    for(unsigned r=0;r<readers;++r){total[r]=r?0:static_cast<uint32_t>(NameQueue::capacity);for(unsigned k=0;k<rounds;++k)total[r]+=static_cast<uint32_t>(sizes[(k+r)%std::size(sizes)]);}
    std::vector<std::thread> threads;
    for(unsigned r=0;r<readers;++r)threads.emplace_back([&,r]{
        uint32_t ordinal=r?0:static_cast<uint32_t>(NameQueue::capacity);std::vector<std::vector<NameEvent>> batches(owners);
        for(unsigned k=0;k<rounds;++k){size_t count=sizes[(k+r)%std::size(sizes)];for(unsigned o=0;o<owners;++o){for(size_t j=0;j<count;++j)batches[o].push_back(token(r,o,ordinal+static_cast<uint32_t>(j)));queues[o].send(batches[o],canceled);assert(batches[o].empty());}ordinal+=static_cast<uint32_t>(count);}
        assert(ordinal==total[r]);for(unsigned o=0;o<owners;++o)queues[o].send(batches[o],canceled);
    });
    for(unsigned o=0;o<owners;++o)threads.emplace_back([&,o]{
        std::vector<uint32_t> next(readers);unsigned remaining=readers;
        while(remaining){auto& q=queues[o];auto* rows=q.receive();if(!rows){std::this_thread::yield();continue;}if(rows->empty())--remaining;else for(const auto& e:*rows){unsigned r=static_cast<unsigned>(e.hash>>40);assert(r<readers);auto expected=token(r,o,next[r]++);assert(e.hash==expected.hash&&e.country==expected.country&&e.value()==expected.value());}q.release();}
        assert(next==total);
    });
    for(auto& t:threads)t.join();for(unsigned o=0;o<owners;++o)assert(queues[o].published.load()==queues[o].consumed.load()&&!queues[o].receive());
}
void cancellation(bool full,bool locked){
    NameQueue q;std::atomic<bool> canceled{false},started{false};
    if(full)for(size_t i=0;i<NameQueue::capacity;++i){std::vector<NameEvent> batch{token(0,0,static_cast<uint32_t>(i))};q.send(batch,canceled);}
    auto before=q.published.load();if(locked)q.producers.lock();std::vector<std::thread> workers;
    for(unsigned r=0;r<8;++r)workers.emplace_back([&,r]{std::vector<NameEvent> batch{token(r,0,100)};started.store(true,std::memory_order_release);bool threw=false;try{q.send(batch,canceled);}catch(const std::runtime_error&){threw=true;}assert(threw&&batch.size()==1);});
    while(!started.load(std::memory_order_acquire))std::this_thread::yield();canceled.store(true);
    for(auto& t:workers)t.join();if(locked)q.producers.unlock();assert(q.published.load()==before);
}
int main(){
    for(unsigned i=0;i<257;++i){std::string key(i%97,char(i));key.append("\0UTF8\xe5\x90\x8d",8);keys.push_back(std::move(key));}
    for(unsigned t=2;t<=12;++t){unsigned readers=std::clamp(t*8/12,1U,t-1);for(uint64_t start:{uint64_t(0),UINT64_MAX-5})transport(readers,t-readers,start);}
    transport(11,1,UINT64_MAX-7);transport(1,11,UINT64_MAX-3);
    // A full queue or held publication mutex prevents successful sends;
    // cancellation must still wake every waiting producer normally.
    cancellation(true,false);cancellation(false,true);cancellation(true,true);
    std::cout<<"PASS pooled multi-producer exact-once key/token/country and per-producer FIFO, all EOFs after all data, fully primed capacity/internal uint64 wrap, every2..12 role split and1/11+11/1, full/locked cancellation\n";
}
