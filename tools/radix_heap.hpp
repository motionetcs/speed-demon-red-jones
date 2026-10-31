#pragma once
#include <array>
#include <bit>
#include <cstdint>
#include <utility>
#include <vector>

// Dijkstra only inserts distances at least as large as the last popped key.
// Redistributing by the highest changed bit gives a monotone integer queue.
struct RadixHeap {
    using Item = std::pair<uint64_t, uint32_t>;
    std::array<std::vector<Item>, 65> buckets;
    uint64_t last = 0;
    size_t count = 0;
    bool empty() const { return count == 0; }
    void clear() {
        for (auto& bucket : buckets) bucket.clear();
        last = 0; count = 0;
    }
    void push(Item item) {
        buckets[std::bit_width(item.first ^ last)].push_back(item);
        ++count;
    }
    Item pop() {
        if (buckets[0].empty()) {
            size_t index = 1;
            while (buckets[index].empty()) ++index;
            last = UINT64_MAX;
            for (const Item& item : buckets[index]) if (item.first < last) last = item.first;
            for (const Item& item : buckets[index])
                buckets[std::bit_width(item.first ^ last)].push_back(item);
            buckets[index].clear();
        }
        Item item = buckets[0].back();
        buckets[0].pop_back(); --count;
        return item;
    }
};
