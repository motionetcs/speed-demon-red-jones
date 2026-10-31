#pragma once
#define RADIX_BATCH_BUCKET_BITS 6
#include <array>
#include <bit>
#include <cstdint>
#include <type_traits>
#include <utility>
#include <vector>

// Band keys are monotone; entries retain their full distance for exact relaxation.
// minimum() returns the band lower bound, so the bidirectional stop remains conservative.
template<class Item> struct DistanceQueue {
    static constexpr bool packed = std::is_same_v<Item, uint64_t>;
    std::array<std::vector<Item>, packed ? 33 : 65> buckets;
    uint64_t last = 0;
    size_t count = 0;
    static uint64_t key(Item item) {
        if constexpr (packed) return (item >> 32) >> RADIX_BATCH_BUCKET_BITS;
        else return item.first >> RADIX_BATCH_BUCKET_BITS;
    }
    bool empty() const { return count == 0; }
    void clear() { for (auto& bucket : buckets) bucket.clear(); last = 0; count = 0; }
    void push(Item item) { buckets[std::bit_width(key(item) ^ last)].push_back(item); ++count; }
    void prepare() {
        if (buckets[0].empty()) {
            size_t index = 1;
            while (buckets[index].empty()) ++index;
            last = UINT64_MAX;
            for (Item item : buckets[index]) if (key(item) < last) last = key(item);
            for (Item item : buckets[index]) buckets[std::bit_width(key(item) ^ last)].push_back(item);
            buckets[index].clear();
        }
    }
    uint64_t minimum() { prepare(); return last << RADIX_BATCH_BUCKET_BITS; }
    Item pop() { prepare(); Item item = buckets[0].back(); buckets[0].pop_back(); --count; return item; }
};

struct RadixHeap {
    using Item = std::pair<uint64_t, uint32_t>;
    DistanceQueue<uint64_t> small;
    DistanceQueue<Item> wide;
    size_t count = 0;
    bool empty() const { return count == 0; }
    void clear() { small.clear(); wide.clear(); count = 0; }
    void push(Item item) {
        if (item.first <= UINT32_MAX) small.push(item.first << 32 | item.second);
        else wide.push(item);
        ++count;
    }
    uint64_t minimum() { return small.empty() ? wide.minimum() : small.minimum(); }
    size_t pop_batch(Item* output, size_t limit) {
        size_t size = 0;
        if (!small.empty()) {
            small.prepare();
            while (size < limit && !small.buckets[0].empty()) {
                uint64_t item = small.buckets[0].back(); small.buckets[0].pop_back(); --small.count;
                output[size++] = {item >> 32, uint32_t(item)};
            }
        } else {
            wide.prepare();
            while (size < limit && !wide.buckets[0].empty()) {
                output[size++] = wide.buckets[0].back(); wide.buckets[0].pop_back(); --wide.count;
            }
        }
        count -= size; return size;
    }
    Item pop() {
        --count;
        if (small.empty()) return wide.pop();
        uint64_t item = small.pop(); return {item >> 32, uint32_t(item)};
    }
};
