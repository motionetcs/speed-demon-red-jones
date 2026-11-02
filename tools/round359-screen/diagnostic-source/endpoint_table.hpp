#pragma once
#include <atomic>
#include <array>
#include <bit>
#include <cstring>
#include <functional>
#include <vector>
#include <cstdint>
#include <memory>
#include <stdexcept>
#include <string_view>

struct Endpoints {
    static constexpr size_t capacity = 8192;
    static constexpr uint64_t hash_mask = 0xffffffffffff0000ULL;
    struct Entry { std::atomic<uint64_t> state{0}; std::string_view value; };
    std::unique_ptr<Entry[]> entries = std::make_unique<Entry[]>(capacity);
    std::array<std::string_view,4096> canonical{};
    std::atomic<uint32_t> used{0};
    std::atomic<bool> canceled{false};
    uint16_t intern(std::string_view value, uint64_t hash) {
        if (canceled.load(std::memory_order_relaxed)) throw std::runtime_error("endpoint limit exceeded");
        size_t slot = hash & (capacity - 1);
        for (size_t probes = 0; probes < capacity; ++probes) {
            auto& entry = entries[slot]; auto state = entry.state.load(std::memory_order_acquire);
            if (!state && entry.state.compare_exchange_strong(state, 1, std::memory_order_acq_rel)) {
                auto id = used.fetch_add(1, std::memory_order_relaxed);
                if (id >= 4096) { canceled.store(true); entry.state.store(0, std::memory_order_release); throw std::runtime_error("endpoint limit exceeded"); }
                canonical[id]=value; entry.value = value; entry.state.store((hash & hash_mask) | (id + 2), std::memory_order_release); return static_cast<uint16_t>(id);
            }
            while (state == 1) state = entry.state.load(std::memory_order_acquire);
            if (state > 1 && (state & hash_mask) == (hash & hash_mask) && entry.value == value) return static_cast<uint16_t>((state & 65535) - 2);
            slot = (slot + 1) & (capacity - 1);
        }
        throw std::runtime_error("endpoint table exceeds capacity");
    }
};

struct alignas(64) CacheCounters {uint64_t calls=0;uint64_t first_hits=0;uint64_t second_hits=0;uint64_t short_misses=0;uint64_t long_fallbacks=0;uint64_t empty_misses=0;uint64_t conflict_misses=0;uint64_t relocation_steps=0;uint64_t dropped_entries=0;};
struct DirectEndpoints {
    struct Slot{const char* data=nullptr;uint32_t hash=0;uint16_t length=0,id=UINT16_MAX;};
    CacheCounters& stats;Endpoints& shared;std::vector<Slot> slots=std::vector<Slot>(4096);
    explicit DirectEndpoints(Endpoints& table,CacheCounters& counters):stats(counters),shared(table){}
    static uint32_t hash_key(std::string_view v){
        if(v.size()<4){uint32_t h=2166136261U;for(unsigned char c:v)h=(h^c)*16777619U;return h;}
        uint32_t a,b,c;std::memcpy(&a,v.data(),4);std::memcpy(&b,v.data()+(v.size()-4)/2,4);std::memcpy(&c,v.data()+v.size()-4,4);
        uint32_t h=(a^std::rotl(b,11)^std::rotl(c,23)^uint32_t(v.size()))*0x9e3779b1U;return h^(h>>16);
    }

    uint16_t intern(std::string_view value){
        ++stats.calls;
        if(value.size()>UINT16_MAX){++stats.long_fallbacks;return shared.intern(value,std::hash<std::string_view>{}(value));}
        uint32_t hash=hash_key(value);size_t i=hash&(slots.size()-1);
        const auto& cached=slots[i];
        if(cached.id!=UINT16_MAX&&cached.hash==hash&&cached.length==value.size()&&(value.empty()||std::memcmp(cached.data,value.data(),value.size())==0)){++stats.first_hits;return cached.id;}
        ++stats.short_misses;if(cached.id==UINT16_MAX)++stats.empty_misses;else ++stats.conflict_misses;
        uint16_t id=shared.intern(value,std::hash<std::string_view>{}(value));
        slots[i]={shared.canonical[id].data(),hash,static_cast<uint16_t>(value.size()),id};return id;
    }
};

struct CuckooEndpoints {
    struct Slot{const char* data=nullptr;uint32_t hash=0;uint16_t length=0,id=UINT16_MAX;};
    CacheCounters& stats;Endpoints& shared;std::vector<Slot> slots=std::vector<Slot>(4096);
    explicit CuckooEndpoints(Endpoints& table,CacheCounters& counters):stats(counters),shared(table){}
    static uint32_t hash_key(std::string_view v){
        if(v.size()<4){uint32_t h=2166136261U;for(unsigned char c:v)h=(h^c)*16777619U;return h;}
        uint32_t a,b,c;std::memcpy(&a,v.data(),4);std::memcpy(&b,v.data()+(v.size()-4)/2,4);std::memcpy(&c,v.data()+v.size()-4,4);
        uint32_t h=(a^std::rotl(b,11)^std::rotl(c,23)^uint32_t(v.size()))*0x9e3779b1U;return h^(h>>16);
    }

    static size_t second(uint32_t hash){
        size_t first=hash&4095,other=(hash>>12)&4095;
        return other==first?(other^1):other;
    }
    static bool matches(const Slot& cached,std::string_view value,uint32_t hash){
        return cached.id!=UINT16_MAX&&cached.hash==hash&&cached.length==value.size()&&(value.empty()||std::memcmp(cached.data,value.data(),value.size())==0);
    }
    uint16_t intern(std::string_view value){
        ++stats.calls;
        if(value.size()>UINT16_MAX){++stats.long_fallbacks;return shared.intern(value,std::hash<std::string_view>{}(value));}
        uint32_t hash=hash_key(value);size_t first=hash&4095;
        if(matches(slots[first],value,hash)){++stats.first_hits;return slots[first].id;}
        size_t other=second(hash);
        if(matches(slots[other],value,hash)){++stats.second_hits;return slots[other].id;}
        ++stats.short_misses;if(slots[first].id==UINT16_MAX||slots[other].id==UINT16_MAX)++stats.empty_misses;else ++stats.conflict_misses;
        uint16_t id=shared.intern(value,std::hash<std::string_view>{}(value));
        Slot pending{shared.canonical[id].data(),hash,static_cast<uint16_t>(value.size()),id};
        if(slots[first].id==UINT16_MAX){slots[first]=pending;return id;}
        if(slots[other].id==UINT16_MAX){slots[other]=pending;return id;}
        size_t current=first;
        for(unsigned step=0;step<8;++step){
            ++stats.relocation_steps;
            Slot evicted=slots[current];slots[current]=pending;pending=evicted;
            if(pending.id==UINT16_MAX)break;
            size_t primary=pending.hash&4095;
            current=current==primary?second(pending.hash):primary;
        }
        if(pending.id!=UINT16_MAX)++stats.dropped_entries;
        return id;
    }
};
static_assert(sizeof(CuckooEndpoints::Slot)==16);

static_assert(sizeof(DirectEndpoints::Slot)==16);
struct CompareEndpoints {
    DirectEndpoints direct;CuckooEndpoints cuckoo;
    CompareEndpoints(Endpoints& table,std::array<CacheCounters,2>& counters):direct(table,counters[0]),cuckoo(table,counters[1]){}
    uint16_t intern(std::string_view value){
        uint16_t id=direct.intern(value);
        if(cuckoo.intern(value)!=id)throw std::runtime_error("diagnostic cache ID disagreement");
        return id;
    }
};
