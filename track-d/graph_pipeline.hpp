#pragma once
#include <algorithm>
#include <atomic>
#include <cstdint>
#include <cstring>
#include <memory>
#include <stdexcept>
#include <thread>
#include <vector>
#include "parallel.hpp"
struct GraphEvent { uint32_t u,v,weight; };
static_assert(sizeof(GraphEvent)==12);
struct GraphCanceled {};
struct GraphQueue {
    alignas(64) std::atomic<bool> ready{false};
    std::vector<GraphEvent> rows;
    void send(std::vector<GraphEvent>& batch,const std::atomic<bool>& canceled) {
        while(ready.load(std::memory_order_acquire)) {
            if(canceled.load(std::memory_order_relaxed))throw GraphCanceled{};
            std::this_thread::yield();
        }
        if(canceled.load(std::memory_order_relaxed))throw GraphCanceled{};
        rows.swap(batch);ready.store(true,std::memory_order_release);
    }
};
struct GraphPipeline {
    static constexpr size_t batch_size=512;
    unsigned threads,readers,owners;uint32_t nodes;
    std::vector<const char*> boundaries;
    GraphPipeline(const char* begin,const char* end,unsigned count,uint32_t n):threads(count),nodes(n) {
        readers=count==1?1:std::clamp(count*8/12,1U,count-1);owners=count==1?1:count-readers;
        boundaries.resize(readers+1);boundaries.front()=begin;boundaries.back()=end;
        for(unsigned i=1;i<readers;++i) {
            const char* p=begin+(end-begin)*i/readers;
            if(p>begin&&p[-1]!='\n') { const char* q=static_cast<const char*>(std::memchr(p,'\n',end-p));p=q?q+1:end; }
            boundaries[i]=p;
        }
    }
    unsigned owner(uint32_t node)const {return (node>>12)%owners;}
    template<class Consume> size_t run(Consume consume)const {
        std::vector<size_t> counts(readers);
        if(threads==1) {
            Scanner input{boundaries[0],boundaries[1]};std::vector<GraphEvent> batch;batch.reserve(batch_size);
            while(input.more()) {
                GraphEvent e{input.number(),input.number(),input.number()};
                if(e.u>=nodes||e.v>=nodes)throw std::runtime_error("node outside graph");
                batch.push_back(e);++counts[0];if(batch.size()==batch_size){consume(0,false,batch);consume(0,true,batch);batch.clear();}
            }
            if(!batch.empty()){consume(0,false,batch);consume(0,true,batch);}return counts[0];
        }
        auto queues=std::make_unique<GraphQueue[]>(size_t(readers)*owners*2);
        std::atomic<bool> canceled{false};
        parallel(threads,[&](unsigned worker) {
            try {
                if(worker<readers) {
                    Scanner input{boundaries[worker],boundaries[worker+1]};std::vector<std::vector<GraphEvent>> batches(owners*2);
                    for(auto& b:batches)b.reserve(batch_size);
                    auto send=[&](unsigned who,bool reverse,GraphEvent e) {unsigned channel=who*2+reverse;auto& b=batches[channel];b.push_back(e);if(b.size()==batch_size){queues[size_t(worker)*owners*2+channel].send(b,canceled);b.clear();}};
                    while(input.more()) {
                        GraphEvent e{input.number(),input.number(),input.number()};
                        if(e.u>=nodes||e.v>=nodes)throw std::runtime_error("node outside graph");
                        send(owner(e.u),false,e);send(owner(e.v),true,e);++counts[worker];
                    }
                    for(unsigned who=0;who<owners*2;++who){auto& b=batches[who];auto& q=queues[size_t(worker)*owners*2+who];if(!b.empty()){q.send(b,canceled);b.clear();}q.send(b,canceled);}
                }else {
                    unsigned who=worker-readers,remaining=readers*2;std::vector<bool> done(readers*2);std::vector<GraphEvent> batch;batch.reserve(batch_size);
                    while(remaining) {
                        bool progress=false;
                        for(unsigned reader=0;reader<readers*2;++reader)if(!done[reader]) {
                            auto& q=queues[size_t(reader/2)*owners*2+who*2+reader%2];
                            if(q.ready.load(std::memory_order_acquire)) {
                                batch.swap(q.rows);q.ready.store(false,std::memory_order_release);progress=true;
                                if(batch.empty()){done[reader]=true;--remaining;}else{consume(who,bool(reader%2),batch);batch.clear();}
                            }
                        }
                        if(canceled.load(std::memory_order_relaxed))throw GraphCanceled{};
                        if(!progress)std::this_thread::yield();
                    }
                }
            }catch(const GraphCanceled&){}catch(...){canceled.store(true,std::memory_order_relaxed);throw;}
        });
        size_t count=0;for(size_t c:counts)count+=c;return count;
    }
};
