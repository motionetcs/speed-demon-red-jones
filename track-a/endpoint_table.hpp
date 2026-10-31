#pragma once
#include <atomic>
#include <cstdint>
#include <memory>
#include <stdexcept>
#include <string_view>

struct Endpoints {
    static constexpr size_t capacity = 32768;
    static constexpr uint64_t hash_mask = 0xffffffffffff0000ULL;
    struct Entry { std::atomic<uint64_t> state{0}; std::string_view value; };
    std::unique_ptr<Entry[]> entries = std::make_unique<Entry[]>(capacity);
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
                entry.value = value; entry.state.store((hash & hash_mask) | (id + 2), std::memory_order_release); return static_cast<uint16_t>(id);
            }
            while (state == 1) state = entry.state.load(std::memory_order_acquire);
            if (state > 1 && (state & hash_mask) == (hash & hash_mask) && entry.value == value) return static_cast<uint16_t>((state & 65535) - 2);
            slot = (slot + 1) & (capacity - 1);
        }
        throw std::runtime_error("endpoint table exceeds capacity");
    }
};
