#include NAMES_HEADER
#include <cassert>
#include <iostream>
#include <string>
#include <thread>
#include <vector>

std::vector<std::string> keys;
NameEvent token(unsigned reader,unsigned owner,uint32_t ordinal) {
    uint64_t id=(uint64_t(reader)<<40)|(uint64_t(owner)<<32)|ordinal;
    return {keys[id%keys.size()],id,static_cast<uint16_t>(id%17577)};
}
void transport(unsigned readers,unsigned owners) {
    auto queues=std::make_unique<NameQueue[]>(size_t(readers)*owners);
    std::atomic<bool> canceled{false};
    for(unsigned r=0;r<readers;++r)for(unsigned o=0;o<owners;++o) {
        std::vector<NameEvent> batch{token(r,o,0)};
        queues[size_t(r)*owners+o].send(batch,canceled);
        assert(batch.empty());
    }
    constexpr size_t sizes[]={1,63,64,65,127,128,129,255,256,257,511,512,513,1025};
    uint32_t total=1;
    for(size_t n:sizes)total+=static_cast<uint32_t>(n);
    std::vector<std::thread> threads;
    for(unsigned r=0;r<readers;++r)threads.emplace_back([&,r] {
        std::vector<std::vector<NameEvent>> batches(owners);
        uint32_t ordinal=1;
        for(size_t count:sizes) {
            for(unsigned o=0;o<owners;++o) {
                auto& batch=batches[o];
                for(size_t i=0;i<count;++i)batch.push_back(token(r,o,ordinal+static_cast<uint32_t>(i)));
                queues[size_t(r)*owners+o].send(batch,canceled);
                assert(batch.empty());
            }
            ordinal+=static_cast<uint32_t>(count);
        }
        assert(ordinal==total);
        for(unsigned o=0;o<owners;++o)queues[size_t(r)*owners+o].send(batches[o],canceled);
    });
    for(unsigned o=0;o<owners;++o)threads.emplace_back([&,o] {
        std::vector<uint32_t> next(readers);
        std::vector<bool> finished(readers);
        unsigned remaining=readers;
        while(remaining) {
            bool progress=false;
            for(unsigned r=0;r<readers;++r) {
                if(finished[r])continue;
                auto& queue=queues[size_t(r)*owners+o];
                if(!queue.ready.load(std::memory_order_acquire))continue;
                progress=true;
                if(queue.rows.empty()) {assert(next[r]==total);finished[r]=true;--remaining;}
                else for(const auto& item:queue.rows) {
                    auto expected=token(r,o,next[r]++);
                    assert(item.hash==expected.hash&&item.country==expected.country&&item.value()==expected.value());
                }
                queue.rows.clear();queue.ready.store(false,std::memory_order_release);
            }
            if(!progress)std::this_thread::yield();
        }
    });
    for(auto& t:threads)t.join();
    for(size_t i=0;i<size_t(readers)*owners;++i)assert(!queues[i].ready.load()&&queues[i].rows.empty());
}
void cancellation(bool full) {
    NameQueue queue;
    std::atomic<bool> canceled{false},started{false};
    if(full) {std::vector<NameEvent> batch{token(0,0,0)};queue.send(batch,canceled);}
    else canceled.store(true);
    std::thread producer([&] {
        std::vector<NameEvent> batch{token(0,0,1)};
        started.store(true,std::memory_order_release);
        bool threw=false;
        try {queue.send(batch,canceled);}catch(const std::runtime_error&) {threw=true;}
        assert(threw&&batch.size()==1&&batch.front().hash==token(0,0,1).hash);
    });
    while(!started.load(std::memory_order_acquire))std::this_thread::yield();
    canceled.store(true,std::memory_order_relaxed);producer.join();
    assert(queue.ready.load()==full);
    if(full)assert(queue.rows.size()==1&&queue.rows.front().hash==token(0,0,0).hash);
}
int main() {
    for(unsigned i=0;i<257;++i) {std::string key(i%97,char(i));key.append("\0UTF8\xe5\x90\x8d",8);keys.push_back(std::move(key));}
    keys.emplace_back(1<<20,'x');
    for(unsigned threads=2;threads<=12;++threads) {
        unsigned readers=std::clamp(threads*7/12,1U,threads-1);
        transport(readers,threads-readers);
    }
    transport(1,11);transport(11,1);
    cancellation(false);cancellation(true);
    std::cout<<"PASS exact production vector SPSC: new7-based all2..12 roles,1/11,11/1, fully primed channels, exact ordered full-hash/country/binary key tokens, partial511/512/513/1025 batches, FIFO EOF and empty/full cancellation\n";
}
