#pragma once
#include <array>
#include <atomic>
#include <memory>

struct Canceled {};
struct Names {
    struct Entry {
        std::atomic<uint64_t> state{0}; // 0 empty, 1 being published, otherwise the full hash.
        uint32_t offset = 0, length = 0;
    };
    size_t capacity, words;
    const char* input;
    std::unique_ptr<Entry[]> entries;
    std::unique_ptr<std::atomic<uint64_t>[]> membership;
    std::atomic<size_t> used{0};
    std::atomic<bool> canceled{false}, too_small{false};
    Names(size_t size, size_t countries, const char* data) : capacity(size), words((countries + 63) / 64),
        input(data),
        entries(std::make_unique<Entry[]>(size)),
        membership(std::make_unique<std::atomic<uint64_t>[]>(size * words)) {}

    static uint64_t hash_key(std::string_view key) {
        uint64_t hash = std::hash<std::string_view>{}(key);
        return hash < 2 ? hash + 2 : hash;
    }
    void prefetch(uint64_t hash) const { __builtin_prefetch(&entries[hash & (capacity - 1)], 0, 1); }
    Entry& intern(std::string_view key, uint64_t hash) {
        if (canceled.load(std::memory_order_relaxed)) throw Canceled{};
        size_t index = hash & (capacity - 1);
        for (;;) {
            Entry& entry = entries[index];
            uint64_t state = entry.state.load(std::memory_order_acquire);
            if (state == 0) {
                if (entry.state.compare_exchange_strong(state, 1, std::memory_order_acq_rel)) {
                    if (key.size() > UINT32_MAX || uint64_t(key.data() - input) >= UINT32_MAX) {
                        canceled.store(true); entry.state.store(0, std::memory_order_release);
                        throw std::runtime_error("CSV name offset exceeds uint32 capacity");
                    }
                    entry.length = static_cast<uint32_t>(key.size());
                    entry.offset = static_cast<uint32_t>(key.data() - input);
                    entry.state.store(hash, std::memory_order_release);
                    if (used.fetch_add(1, std::memory_order_relaxed) >= capacity * 7 / 8) {
                        too_small.store(true); canceled.store(true); throw Canceled{};
                    }
                    return entry;
                }
            }
            while (state == 1) {
                if (canceled.load(std::memory_order_relaxed)) throw Canceled{};
                state = entry.state.load(std::memory_order_acquire);
            }
            if (state == hash) {
                const char* bytes = input + entry.offset;
                if (std::string_view(bytes, entry.length) == key) return entry;
            }
            if (canceled.load(std::memory_order_relaxed)) throw Canceled{};
            index = (index + 1) & (capacity - 1);
        }
    }
    bool first(Entry& entry, size_t country) {
        auto& word = membership[size_t(&entry - entries.get()) * words + country / 64];
        uint64_t bit = uint64_t(1) << (country % 64);
        return (word.fetch_or(bit, std::memory_order_relaxed) & bit) == 0;
    }
};
