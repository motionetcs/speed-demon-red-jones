#pragma once
#include <algorithm>
#include <bit>
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
    struct Entry { NameKey* key = nullptr; };
    static constexpr uint64_t ones = 0x0101010101010101ULL, highs = 0x8080808080808080ULL;
    size_t capacity, words;
    std::unique_ptr<Entry[]> entries;
    std::unique_ptr<std::atomic<uint64_t>[]> controls;
    std::atomic<size_t> used{0};
    std::atomic<bool> canceled{false}, too_small{false};
    Names(size_t size, size_t countries) : capacity(size), words((countries + 63) / 64),
        entries(std::make_unique<Entry[]>(size)), controls(new std::atomic<uint64_t>[size / 8]{}) {
        if (size < 8 || (size & (size - 1))) throw std::runtime_error("invalid name capacity");
    }
    static uint64_t matches(uint64_t word, uint8_t tag) {
        uint64_t x = word ^ (uint64_t(tag) * ones);
        return (x - ones) & ~x & highs;
    }
    static uint64_t hash_key(std::string_view key) {
        uint64_t hash = std::hash<std::string_view>{}(key); return hash < 2 ? hash + 2 : hash;
    }
    void prefetch(uint64_t hash) const {
        size_t group = (hash & (capacity - 1)) / 8;
        __builtin_prefetch(&controls[group], 0, 1); __builtin_prefetch(&entries[group * 8], 0, 1);
    }
    std::string_view bytes(const NameKey* key) const {
        return {reinterpret_cast<const char*>(key) + sizeof(NameKey) + words * sizeof(std::atomic<uint64_t>), key->length};
    }
    Entry& intern(std::string_view key, StringArena& storage, uint64_t hash) {
        size_t group = (hash & (capacity - 1)) / 8;
        uint8_t tag = static_cast<uint8_t>(hash >> 56) | 2; // 0 empty, 1 writing; every other byte is published.
        for (size_t probes = 0; probes < capacity / 8; ++probes) {
            for (;;) {
                if (canceled.load(std::memory_order_relaxed)) throw Canceled{};
                uint64_t word = controls[group].load(std::memory_order_acquire);
                while (matches(word, 1)) {
                    if (canceled.load(std::memory_order_relaxed)) throw Canceled{};
                    word = controls[group].load(std::memory_order_acquire);
                }
                uint64_t candidates = matches(word, tag);
                while (candidates) {
                    size_t index = group * 8 + std::countr_zero(candidates) / 8;
                    if (bytes(entries[index].key) == key) return entries[index];
                    candidates &= candidates - 1;
                }
                uint64_t empty = matches(word, 0);
                if (!empty) break;
                unsigned shift = std::countr_zero(empty) / 8 * 8;
                uint64_t expected = word;
                if (!controls[group].compare_exchange_strong(expected, word | (uint64_t(1) << shift), std::memory_order_acq_rel)) continue;
                Entry& entry = entries[group * 8 + shift / 8];
                try { entry.key = storage.make(key, words); }
                catch (...) { canceled.store(true); controls[group].store(word, std::memory_order_release); throw; }
                // A group has at most one writer; every other writer waits for byte1 to clear.
                controls[group].store(word | (uint64_t(tag) << shift), std::memory_order_release);
                if (used.fetch_add(1, std::memory_order_relaxed) >= capacity * 7 / 8) {
                    too_small.store(true); canceled.store(true); throw Canceled{};
                }
                return entry;
            }
            group = (group + 1) & (capacity / 8 - 1);
        }
        too_small.store(true); canceled.store(true); throw Canceled{};
    }
    bool first(Entry& entry, size_t country) {
        auto* bits = reinterpret_cast<std::atomic<uint64_t>*>(reinterpret_cast<char*>(entry.key) + sizeof(NameKey));
        uint64_t bit = uint64_t(1) << (country % 64);
        return (bits[country / 64].fetch_or(bit, std::memory_order_relaxed) & bit) == 0;
    }
};
