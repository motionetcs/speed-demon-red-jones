#ifndef NAMES_HEADER
#error "Supply the exact cooperative candidate names header"
#endif
#include NAMES_HEADER
#include <cassert>
#include <iostream>
#include <string>
#include <vector>

void transport(unsigned workers,size_t batch_size,size_t extra){
    size_t per_edge=batch_size+extra,total=size_t(workers)*workers*per_edge;
    std::vector<std::string> values(total);
    for(size_t i=0;i<total;++i)values[i]="token/"+std::to_string(i);
    auto queues=std::make_unique<NameQueue[]>(size_t(workers)*workers);
    std::vector<std::vector<uint8_t>> seen(workers,std::vector<uint8_t>(size_t(workers)*per_edge));
    std::atomic<bool> canceled{false};std::atomic<unsigned> primed{0};
    auto run=[&](unsigned self){
        std::vector<bool> finished(workers);finished[self]=true;unsigned remaining=workers-1;
        std::vector<size_t> received(workers);std::vector<std::vector<NameEvent>> batches(workers);
        auto event=[&](unsigned target,size_t i){size_t id=(size_t(self)*workers+target)*per_edge+i;return NameEvent{values[id],uint64_t(id),static_cast<uint16_t>(target)};};
        auto pump=[&](){
            bool progress=false;
            for(unsigned source=0;source<workers;++source)if(!finished[source]){
                auto& q=queues[size_t(source)*workers+self];if(!q.ready.load(std::memory_order_acquire))continue;progress=true;
                if(q.rows.empty()){assert(received[source]==per_edge);finished[source]=true;--remaining;}
                else for(const auto& e:q.rows){
                    assert(e.country==self);size_t first=(size_t(source)*workers+self)*per_edge;
                    assert(e.hash>=first&&e.hash<first+per_edge);size_t i=size_t(e.hash)-first;
                    assert(e.value()==values[size_t(e.hash)]);assert(seen[self][size_t(source)*per_edge+i]++==0);++received[source];
                }
                q.rows.clear();q.ready.store(false,std::memory_order_release);
            }
            return progress;
        };
        // Prime EVERY directed edge before any consumer is allowed to run.
        // The barrier then forces cyclic full-buffer sends on the next publish.
        for(unsigned step=1;step<workers;++step){unsigned target=(self+step)%workers;auto& batch=batches[target];batch.reserve(batch_size);for(size_t i=0;i<batch_size;++i)batch.push_back(event(target,i));queues[size_t(self)*workers+target].send(batch,canceled,pump);}
        primed.fetch_add(1,std::memory_order_release);while(primed.load(std::memory_order_acquire)!=workers)std::this_thread::yield();
        for(unsigned step=1;step<workers;++step){
            unsigned target=(self+step)%workers;auto& batch=batches[target];auto& q=queues[size_t(self)*workers+target];
            for(size_t i=batch_size;i<per_edge;++i){batch.push_back(event(target,i));if(batch.size()==batch_size)q.send(batch,canceled,pump);if(i%17==0)std::this_thread::yield();}
            if(!batch.empty())q.send(batch,canceled,pump);q.send(batch,canceled,pump);
        }
        while(remaining)if(!pump())std::this_thread::yield();
    };
    std::vector<std::thread> threads;for(unsigned i=1;i<workers;++i)threads.emplace_back(run,i);run(0);for(auto& t:threads)t.join();
    for(unsigned target=0;target<workers;++target)for(unsigned source=0;source<workers;++source)for(size_t i=0;i<per_edge;++i)assert(seen[target][size_t(source)*per_edge+i]==uint8_t(source!=target));
}
int main(){
    for(unsigned workers=1;workers<=12;++workers){
        for(size_t extra:{size_t(0),size_t(1),size_t(2)})transport(workers,1,extra);
        for(size_t extra:{size_t(0),size_t(1),size_t(63),size_t(64),size_t(65)})transport(workers,64,extra);
        for(size_t extra:{size_t(0),size_t(1),size_t(129)})transport(workers,128,extra);
    }
    for(unsigned mode=0;mode<4;++mode){
        NameQueue q;std::atomic<bool> canceled{mode==0};std::string first="first",second="second";q.rows.push_back(NameEvent{first,1,0});q.ready.store(true);
        std::vector<NameEvent> batch{ NameEvent{second,2,0} };unsigned calls=0;bool threw=false;
        try{q.send(batch,canceled,[&](){++calls;if(mode==3)throw std::runtime_error("owner failure");if(mode==2){q.rows.clear();q.ready.store(false,std::memory_order_release);}canceled.store(true);return mode==2;});}
        catch(const std::runtime_error&){threw=true;}
        assert(threw&&batch.size()==1&&batch[0].value()==second);assert(calls==unsigned(mode!=0));
        assert(q.ready.load()==(mode!=2));if(mode!=2)assert(q.rows.size()==1&&q.rows[0].value()==first);
    }
    NameQueue free;std::atomic<bool> canceled{true};std::string data="data";std::vector<NameEvent> batch{NameEvent{data,3,0}};bool threw=false;
    try{free.send(batch,canceled,[](){assert(false);return false;});}catch(const std::runtime_error&){threw=true;}
    assert(threw&&!free.ready.load()&&free.rows.empty()&&batch.size()==1);
    std::cout<<"PASS cooperative transport independent token identity/exact-once/EOF reference, every1..12 topology, fully primed cyclic queues,1/64/128 batches and partial seams, callback exceptions/cancel before and after space becomes free\n";
}
