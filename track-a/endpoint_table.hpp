#pragma once
#include <atomic>
#include <functional>
#if defined(__SSE4_2__)
#include <nmmintrin.h>
#endif
#include <cstdint>
#include <cstring>
#include <memory>
#include <stdexcept>
#include <string_view>

struct Endpoints {
    static constexpr size_t capacity = 8192;
    static constexpr uint64_t hash_mask = 0xffffffffffff0000ULL;
    struct Entry { std::atomic<uint64_t> state{0}; std::string_view value; };
    std::unique_ptr<Entry[]> entries = std::make_unique<Entry[]>(capacity);
    std::atomic<uint32_t> used{0};
    std::atomic<bool> canceled{false};
    static uint64_t hash_key(std::string_view key) {
#if defined(__SSE4_2__)
        uint64_t hash=key.size();const char* p=key.data();size_t remaining=key.size();
        while(remaining>=8){uint64_t word;std::memcpy(&word,p,8);hash=_mm_crc32_u64(hash,word);p+=8;remaining-=8;}
        if(remaining){uint64_t tail=0;std::memcpy(&tail,p,remaining);hash=_mm_crc32_u64(hash,tail);}
        return hash*0x9e3779b97f4a7c15ULL;
#else
        return std::hash<std::string_view>{}(key);
#endif
    }
    uint16_t intern(std::string_view value, uint64_t hash) {
        if (canceled.load(std::memory_order_relaxed)) throw std::runtime_error("endpoint limit exceeded");
        size_t slot = hash & (capacity - 1);
        for (size_t probes = 0; probes < capacity; ++probes) {
            auto& entry = entries[slot]; auto state = entry.state.load(std::memory_order_acquire);
            if (!state && entry.state.compare_exchange_strong(state, 1, std::memory_order_acq_rel)) {
                auto id = used.fetch_add(1, std::memory_order_relaxed);
                if (id >= 4096) { canceled.store(true); entry.state.store(0, std::memory_order_release); throw std::runtime_error("endpoint limit exceeded"); }
                entry.value = value; entry.state.store((hash & hash_mask) | (id + 2), std::memory_order_release); return static_cast<uint16_t>(id);
            }
            while (state == 1) state = entry.state.load(std::memory_order_acquire);
            if (state > 1 && (state & hash_mask) == (hash & hash_mask) && entry.value == value) return static_cast<uint16_t>((state & 65535) - 2);
            slot = (slot + 1) & (capacity - 1);
        }
        throw std::runtime_error("endpoint table exceeds capacity");
    }
};
