#pragma once
#include <array>
#include <bit>
#include <cstdint>
#include <type_traits>
#include <utility>
#include <vector>

// Monotone distance keys; node IDs do not participate in bucket ordering.
template<class Item> struct DistanceQueue {
    static constexpr bool packed = std::is_same_v<Item, uint64_t>;
    std::array<std::vector<Item>, packed ? 33 : 65> buckets;
    uint64_t last = 0;
    size_t count = 0;
    static uint64_t key(Item item) {
        if constexpr (packed) return item >> 32;
        else return item.first;
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
    uint64_t minimum() { prepare(); return last; }
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
    Item pop() {
        --count;
        if (small.empty()) return wide.pop();
        uint64_t item = small.pop(); return {item >> 32, uint32_t(item)};
    }
};
