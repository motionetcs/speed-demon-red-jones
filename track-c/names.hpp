#pragma once
#include <array>
#include <atomic>
#include <deque>
#include <memory>

struct Canceled {};
struct Names {
    struct Entry {
        std::atomic<uint64_t> state{0}; // 0 empty, 1 being published, otherwise the full hash.
        std::string_view key;
        std::array<std::atomic<uint64_t>, 4> bits{};
    };
    size_t capacity, extra_words;
    std::unique_ptr<Entry[]> entries;
    std::unique_ptr<std::atomic<uint64_t>[]> extra;
    std::atomic<size_t> used{0};
    std::atomic<bool> canceled{false}, too_small{false};
    Names(size_t size, size_t countries) : capacity(size), extra_words(countries > 256 ? (countries - 256 + 63) / 64 : 0),
        entries(std::make_unique<Entry[]>(size)), extra(std::make_unique<std::atomic<uint64_t>[]>(size * extra_words)) {}

    Entry& intern(std::string_view key, std::deque<std::string>& storage) {
        if (canceled.load(std::memory_order_relaxed)) throw Canceled{};
        uint64_t hash = std::hash<std::string_view>{}(key);
        if (hash < 2) hash += 2;
        size_t index = hash & (capacity - 1);
        for (;;) {
            Entry& entry = entries[index];
            uint64_t state = entry.state.load(std::memory_order_acquire);
            if (state == 0) {
                if (entry.state.compare_exchange_strong(state, 1, std::memory_order_acq_rel)) {
                    try { storage.emplace_back(key); entry.key = storage.back(); }
                    catch (...) { canceled.store(true); entry.state.store(0, std::memory_order_release); throw; }
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
            if (state == hash && entry.key == key) return entry;
            if (canceled.load(std::memory_order_relaxed)) throw Canceled{};
            index = (index + 1) & (capacity - 1);
        }
    }
    bool first(Entry& entry, size_t country) {
        auto& word = country < 256 ? entry.bits[country / 64]
            : extra[size_t(&entry - entries.get()) * extra_words + (country - 256) / 64];
        uint64_t bit = uint64_t(1) << (country % 64);
        return (word.fetch_or(bit, std::memory_order_relaxed) & bit) == 0;
    }
};
