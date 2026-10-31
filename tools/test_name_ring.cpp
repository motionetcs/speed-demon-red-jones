#ifndef NAMES_HEADER
#error Explicit ring candidate header required
#endif
#include NAMES_HEADER
#include <cassert>
#include <iostream>
#include <string>
#include <thread>
#include <vector>

std::vector<std::string> keys;
NameEvent event(unsigned reader,unsigned owner,uint32_t ordinal){
    uint64_t token=(uint64_t(reader)<<40)|(uint64_t(owner)<<32)|ordinal;
    return {keys[token%keys.size()],token,static_cast<uint16_t>(token%17577)};
}
void inspect(const NameEvent& got,unsigned reader,unsigned owner,uint32_t ordinal){
    auto expected=event(reader,owner,ordinal);
    assert(got.hash==expected.hash&&got.country==expected.country&&got.value()==expected.value());
}
void transport(unsigned readers,unsigned owners,uint64_t beginning){
    auto queues=std::make_unique<NameQueue[]>(size_t(readers)*owners);
    std::atomic<bool> canceled{false};
    // Valid empty internal sequence state near wrap; never a board counter.
    for(unsigned r=0;r<readers;++r)for(unsigned o=0;o<owners;++o){
        auto& q=queues[size_t(r)*owners+o];q.published.store(beginning);q.consumed.store(beginning);
        assert(!q.receive());
        for(size_t k=0;k<NameQueue::capacity;++k){std::vector<NameEvent> batch{event(r,o,static_cast<uint32_t>(k))};q.send(batch,canceled);assert(batch.empty());}
        assert(q.published.load()-q.consumed.load()==NameQueue::capacity);
    }
    constexpr uint32_t batches=48;
    constexpr size_t sizes[]={1,63,64,65,127,128,129,255,256,257,511,512,513,1025};
    uint32_t total=static_cast<uint32_t>(NameQueue::capacity);
    for(uint32_t k=0;k<batches;++k)total+=static_cast<uint32_t>(sizes[k%std::size(sizes)]);
    std::vector<std::thread> threads;
    for(unsigned r=0;r<readers;++r)threads.emplace_back([&,r]{
        std::vector<std::vector<NameEvent>> batch(owners);
        uint32_t ordinal=static_cast<uint32_t>(NameQueue::capacity);
        for(uint32_t k=0;k<batches;++k){
            size_t count=sizes[k%std::size(sizes)];
            for(unsigned o=0;o<owners;++o){
                for(size_t i=0;i<count;++i)batch[o].push_back(event(r,o,ordinal+static_cast<uint32_t>(i)));
                queues[size_t(r)*owners+o].send(batch[o],canceled);assert(batch[o].empty());
            }
            ordinal+=static_cast<uint32_t>(count);
        }
        assert(ordinal==total);
        for(unsigned o=0;o<owners;++o)queues[size_t(r)*owners+o].send(batch[o],canceled);
    });
    for(unsigned o=0;o<owners;++o)threads.emplace_back([&,o]{
        std::vector<uint32_t> next(readers);std::vector<bool> finished(readers);unsigned remaining=readers;
        while(remaining){
            bool progress=false;
            for(unsigned r=0;r<readers;++r){
                if(finished[r])continue;auto& q=queues[size_t(r)*owners+o];auto* rows=q.receive();if(!rows)continue;
                progress=true;
                if(rows->empty()){assert(next[r]==total);finished[r]=true;--remaining;}
                else for(const auto& e:*rows)inspect(e,r,o,next[r]++);
                q.release();
            }
            if(!progress)std::this_thread::yield();
        }
    });
    for(auto& t:threads)t.join();
    for(size_t i=0;i<size_t(readers)*owners;++i){auto& q=queues[i];assert(q.published.load()==q.consumed.load()&&!q.receive());}
}
void cancellation(bool full){
    NameQueue q;std::atomic<bool> canceled{false};
    if(full)for(size_t k=0;k<NameQueue::capacity;++k){std::vector<NameEvent> b{event(0,0,static_cast<uint32_t>(k))};q.send(b,canceled);}
    auto before=q.published.load();canceled.store(true);std::vector<NameEvent> batch{event(0,0,100)};
    bool threw=false;try{q.send(batch,canceled);}catch(const std::runtime_error&){threw=true;}
    assert(threw&&batch.size()==1&&q.published.load()==before);
}
int main(){
    static_assert(NameQueue::capacity>0&&(NameQueue::capacity&(NameQueue::capacity-1))==0);
    for(unsigned i=0;i<257;++i){std::string key(i%97,char(i));key.append("\0UTF8\xe5\x90\x8d",8);keys.push_back(std::move(key));}
    for(unsigned t=2;t<=12;++t){unsigned r=std::clamp(t*8/12,1U,t-1);for(uint64_t start:{uint64_t(0),UINT64_MAX-5})transport(r,t-r,start);}
    transport(1,11,UINT64_MAX-7);transport(11,1,UINT64_MAX-3);
    cancellation(false);cancellation(true);
    std::cout<<"PASS SPSC ring capacity="<<NameQueue::capacity<<": fully primed channels, every2..12-worker role topology,1/11 and11/1, exact ordered tokens/key bytes/countries, varied/partial batches, FIFO EOF, empty/full cancellation and internal uint64 sequence wrap\n";
}
