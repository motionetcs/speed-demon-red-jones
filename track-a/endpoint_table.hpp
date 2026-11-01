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

// A private parsing hint never replaces full byte equality or the delimiter.
template<size_t Slots> struct EndpointSpanCache {
    static_assert(Slots&&!(Slots&(Slots-1)));
    struct Hint{const char* data=nullptr;uint16_t size=0,id=UINT16_MAX;};
    Endpoints& shared;std::array<Hint,Slots> hints{};
    explicit EndpointSpanCache(Endpoints& s):shared(s){}
    uint16_t read(const char*& p,const char* end){
        const char* start=p;Hint* hint=nullptr;
        if(end-start>=16){
            uint64_t a,b;std::memcpy(&a,start,8);std::memcpy(&b,start+8,8);
            uint64_t h=(a^std::rotl(b,23))*0x9e3779b97f4a7c15ULL;h^=h>>32;
            hint=&hints[h&(Slots-1)];
            if(hint->id!=UINT16_MAX&&size_t(end-start)>hint->size&&start[hint->size]==' '&&std::memcmp(start,hint->data,hint->size)==0){p=start+hint->size;return hint->id;}
        }
        const char* separator=static_cast<const char*>(std::memchr(start,' ',size_t(end-start)));
        if(!separator)throw std::runtime_error("missing endpoint/status");
        std::string_view value(start,size_t(separator-start));uint16_t id=shared.intern(value,std::hash<std::string_view>{}(value));
        if(hint&&value.size()>=16&&value.size()<=UINT16_MAX)*hint={shared.canonical[id].data(),uint16_t(value.size()),id};
        p=separator;return id;
    }
};
