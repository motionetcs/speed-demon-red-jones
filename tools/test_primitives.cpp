#ifdef DECIMAL_HEADER
#include DECIMAL_HEADER
#else
#include "../track-a/decimal.hpp"
#endif
#ifdef COMPACT_QUEUE_HEADER
#include COMPACT_QUEUE_HEADER
#else
#include "../track-d/radix_heap.hpp"
#endif
#include <cassert>
#include <charconv>
#include <cstring>
#include <iostream>
#include <random>
#include <set>
#include <unordered_map>
#include "../track-d/distance_map.hpp"
#include <string>
#include <sys/mman.h>
#include <unistd.h>

#ifndef RADIX_BATCH_BUCKET_BITS
#define RADIX_BATCH_BUCKET_BITS 0
#endif
uint64_t band(uint64_t distance) { return distance >> RADIX_BATCH_BUCKET_BITS; }
void number_case(const std::string& text) {
    uint64_t expected = 0;
    auto reference = std::from_chars(text.data(), text.data() + text.size(), expected);
    const char* p = text.data();
    uint64_t actual = decimal_digits(p, text.data() + text.size());
    assert(actual == expected && p == reference.ptr);
}
int main() {
    std::mt19937_64 random(0x167ced90);
    for (unsigned n = 0; n < 10000; ++n) number_case(std::to_string(n) + ",");
    for (unsigned i = 0; i < 100000; ++i) number_case(std::to_string(random()) + "\n");
    for (unsigned position = 0; position < 8; ++position) for (unsigned byte = 0; byte < 256; ++byte) {
        std::string s = "90817263"; s[position] = char(byte); s.push_back(';'); number_case(s);
    }
    size_t page = static_cast<size_t>(sysconf(_SC_PAGESIZE));
    char* guard = static_cast<char*>(mmap(nullptr, page * 2, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANON, -1, 0));
    assert(guard != MAP_FAILED && mprotect(guard + page, page, PROT_NONE) == 0);
    for (size_t length = 0; length <= 24; ++length) {
        std::string text = std::to_string(random()); text.resize(length, ';');
        char* start = guard + page - text.size(); std::memcpy(start, text.data(), text.size());
        uint64_t expected = 0; auto reference = std::from_chars(start, guard + page, expected);
        const char* p = start; assert(decimal_digits(p, guard + page) == expected && p == reference.ptr);
    }
    munmap(guard, page * 2);
    for (unsigned trial = 0; trial < 20; ++trial) {
        RadixHeap queue; std::multiset<RadixHeap::Item> expected;
        uint64_t last = trial % 2 ? uint64_t(UINT32_MAX) - 30 : 0;
        for (unsigned i = 0; i < 12000; ++i) {
            if (expected.empty() || random() % 3) {
                uint64_t distance = last + random() % 10000;
                RadixHeap::Item item{distance, uint32_t(random())}; queue.push(item); expected.insert(item);
            } else {
                assert(queue.minimum() == (band(expected.begin()->first) << RADIX_BATCH_BUCKET_BITS));
#if RADIX_BATCH_BUCKET_BITS > 0
                if (i % 2) {
                    RadixHeap::Item work[8]; uint64_t first_band = band(expected.begin()->first);
                    size_t count = queue.pop_batch(work, 8); assert(count && count <= 8);
                    for (size_t k = 0; k < count; ++k) {
                        assert(band(work[k].first) == first_band);
                        auto found = expected.find(work[k]); assert(found != expected.end()); expected.erase(found);
                        last = std::max(last, work[k].first);
                    }
                } else
#endif
                {
                    auto item = queue.pop(); assert(band(item.first) == band(expected.begin()->first));
                    auto found = expected.find(item); assert(found != expected.end()); expected.erase(found); last = item.first;
                }
            }
            assert(queue.count == expected.size() && queue.empty() == expected.empty());
            // Peeking rebases radix buckets; mirror Dijkstra by peeking immediately before extraction.
        }
        while (!expected.empty()) { auto item = queue.pop(); assert(band(item.first) == band(expected.begin()->first)); expected.erase(expected.find(item)); }
        queue.clear(); queue.push({UINT64_MAX, UINT32_MAX}); assert(queue.pop() == RadixHeap::Item(UINT64_MAX, UINT32_MAX));
    }
    FastDistances labels;
    for (unsigned trial = 0; trial < 6; ++trial) {
        labels.reset(); std::unordered_map<uint32_t, uint64_t> reference;
        for (unsigned i = 0; i < 150000; ++i) {
            uint32_t node = random() % 45000;
            if (i % 997 == 0) node = UINT32_MAX;
            uint64_t distance = random() % (uint64_t(UINT32_MAX) + 100000);
            auto found = reference.find(node);
            bool expected = found == reference.end() || distance < found->second;
            assert(labels.improve(node, distance) == expected);
            if (expected) reference[node] = distance;
            assert(labels.get(node) == reference.at(node));
        }
        for (const auto& [node, distance] : reference) assert(labels.get(node) == distance);
        labels.reset(); assert(labels.get(123) == UINT64_MAX);
        assert(labels.improve(123, uint64_t(UINT32_MAX) + 5));
        assert(labels.improve(123, 7)); assert(labels.get(123) == 7);
        assert(!labels.improve(123, uint64_t(UINT32_MAX) + 2));
    }
    std::cout << "PASS decimal reference/byte/guard-page checks and compact/wide queue/label model checks\n";
}
