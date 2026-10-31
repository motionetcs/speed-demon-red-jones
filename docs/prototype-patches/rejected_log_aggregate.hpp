#pragma once
#include <array>
#include <atomic>
#include <cstdint>
#include <functional>
#include <memory>
#include <stdexcept>
#include <string_view>
#include <unordered_map>
#include <vector>

struct RetryEndpoints {};
struct Endpoints {
    struct Entry { std::atomic<uint64_t> state{0}; uint32_t id=0; };
    size_t capacity;
    std::unique_ptr<Entry[]> entries;
    std::vector<std::string_view> paths;
    std::atomic<uint32_t> used{0};
    std::atomic<bool> canceled{false},too_small{false};
    static size_t checked(size_t count){if(!count || (count&(count-1)) || count>UINT32_MAX)throw std::runtime_error("invalid endpoint capacity");return count;}
    explicit Endpoints(size_t count) : capacity(checked(count)),entries(std::make_unique<Entry[]>(capacity*2)),paths(capacity) {}
    static uint64_t hash_key(std::string_view key){uint64_t h=std::hash<std::string_view>{}(key);return h<2 ? h+2:h;}
    void prefetch(uint64_t hash)const{__builtin_prefetch(&entries[hash&(capacity*2-1)],0,1);}
    uint32_t intern(std::string_view key,uint64_t hash) {
        if(canceled.load(std::memory_order_relaxed))throw RetryEndpoints{};
        size_t index=hash&(capacity*2-1);
        for(;;) {
            Entry& entry=entries[index];uint64_t state=entry.state.load(std::memory_order_acquire);
            if(state==0 && entry.state.compare_exchange_strong(state,1,std::memory_order_acq_rel)) {
                uint32_t id=used.fetch_add(1,std::memory_order_relaxed);
                if(id>=capacity){too_small.store(true);canceled.store(true);entry.state.store(0,std::memory_order_release);throw RetryEndpoints{};}
                paths[id]=key;entry.id=id;entry.state.store(hash,std::memory_order_release);return id;
            }
            while(state==1){if(canceled.load(std::memory_order_relaxed))throw RetryEndpoints{};state=entry.state.load(std::memory_order_acquire);}
            if(state==hash && paths[entry.id]==key)return entry.id;
            if(canceled.load(std::memory_order_relaxed))throw RetryEndpoints{};
            index=(index+1)&(capacity*2-1);
        }
    }
    uint32_t lookup(std::string_view key,uint64_t hash)const {
        size_t index=hash&(capacity*2-1);
        for(;;){const Entry& entry=entries[index];uint64_t state=entry.state.load(std::memory_order_relaxed);
            if(state==hash && paths[entry.id]==key)return entry.id;
            if(state==0)throw std::runtime_error("endpoint missing in second pass");
            index=(index+1)&(capacity*2-1);
        }
    }
};
struct Pair16 {uint16_t count,errors;};
union CountCell {Pair16 counts;uint32_t cursor;CountCell():counts{} {}};
static_assert(sizeof(CountCell)==4);
struct WideCounts {uint64_t count=0,errors=0;};
struct CountChunk {
    std::vector<CountCell> cells;
    std::unordered_map<size_t,WideCounts> spills;
    std::array<std::string_view,72> labels{};
    explicit CountChunk(size_t groups):cells(groups){}
    void add(size_t group,bool error){auto& count=cells[group].counts;if(++count.count==0)spills[group].count+=65536;if(error && ++count.errors==0)spills[group].errors+=65536;}
    WideCounts total(size_t group)const {
        WideCounts value{cells[group].counts.count,cells[group].counts.errors};
        if(!spills.empty())if(auto i=spills.find(group);i!=spills.end()){value.count+=i->second.count;value.errors+=i->second.errors;}
        return value;
    }
};
