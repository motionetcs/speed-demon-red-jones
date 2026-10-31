#pragma once
#include <algorithm>
#include <atomic>
#include <cstdint>
#include <cstring>
#include <memory>
#include <functional>
#include <stdexcept>
#include <string_view>
#include <new>
#include <type_traits>
#include <vector>

struct alignas(8) NameKey { uint32_t length, padding; };
static_assert(sizeof(NameKey) == 8 && alignof(std::atomic<uint64_t>) <= alignof(NameKey));
static_assert(std::is_trivially_destructible_v<std::atomic<uint64_t>>);

// One stable allocation holds header, actual country words, then exact name bytes.
// Each arena has one owner; table publication makes completed keys visible.
struct StringArena {
    std::vector<std::unique_ptr<char[]>> blocks;
    char* next = nullptr;
    size_t remaining = 0;
    NameKey* make(std::string_view value, size_t words) {
        if (value.size() > UINT32_MAX || words > (SIZE_MAX - sizeof(NameKey) - value.size() - 7) / sizeof(std::atomic<uint64_t>))
            throw std::runtime_error("name storage size overflow");
        size_t bytes = sizeof(NameKey) + words * sizeof(std::atomic<uint64_t>) + value.size();
        bytes = (bytes + 7) & ~size_t(7);
        if (bytes > remaining) {
            size_t capacity = std::max<size_t>(65536, bytes);
            blocks.emplace_back(new char[capacity]); next = blocks.back().get(); remaining = capacity;
        }
        auto* result = ::new (static_cast<void*>(next)) NameKey{static_cast<uint32_t>(value.size()), 0};
        ::new (static_cast<void*>(next + sizeof(NameKey))) std::atomic<uint64_t>[words]{};
        char* data = next + sizeof(NameKey) + words * sizeof(std::atomic<uint64_t>);
        if (!value.empty()) std::memcpy(data, value.data(), value.size());
        next += bytes; remaining -= bytes; return result;
    }
};
struct Canceled {};
struct Names {
    struct Entry { std::atomic<uint64_t> state{0}; NameKey* key = nullptr; };
    size_t capacity, words;
    std::unique_ptr<Entry[]> entries;
    std::atomic<size_t> used{0};
    std::atomic<bool> canceled{false}, too_small{false};
    Names(size_t size, size_t countries) : capacity(size), words((countries + 63) / 64),
        entries(std::make_unique<Entry[]>(size)) {}
    static uint64_t hash_key(std::string_view key) {
        uint64_t hash = std::hash<std::string_view>{}(key); return hash < 2 ? hash + 2 : hash;
    }
    void prefetch(uint64_t hash) const { __builtin_prefetch(&entries[hash & (capacity - 1)], 0, 1); }
    std::string_view bytes(const NameKey* key) const {
        return {reinterpret_cast<const char*>(key) + sizeof(NameKey) + words * sizeof(std::atomic<uint64_t>), key->length};
    }
    Entry& intern(std::string_view key, StringArena& storage, uint64_t hash) {
        if (canceled.load(std::memory_order_relaxed)) throw Canceled{};
        size_t index = hash & (capacity - 1);
        for (;;) {
            Entry& entry = entries[index]; uint64_t state = entry.state.load(std::memory_order_acquire);
            if (state == 0) {
                if (entry.state.compare_exchange_strong(state, 1, std::memory_order_acq_rel)) {
                    try { entry.key = storage.make(key, words); }
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
            if (state == hash && bytes(entry.key) == key) return entry;
            if (canceled.load(std::memory_order_relaxed)) throw Canceled{};
            index = (index + 1) & (capacity - 1);
        }
    }
    bool first(Entry& entry, size_t country) {
        auto* bits = reinterpret_cast<std::atomic<uint64_t>*>(reinterpret_cast<char*>(entry.key) + sizeof(NameKey));
        uint64_t bit = uint64_t(1) << (country % 64);
        auto& word = bits[country / 64];
        if (word.load(std::memory_order_relaxed) & bit) return false;
        return (word.fetch_or(bit, std::memory_order_relaxed) & bit) == 0;
    }
};
