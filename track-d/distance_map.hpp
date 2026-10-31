#pragma once
#include <cstdint>
#include <atomic>
#include <utility>
#include <vector>

struct Distances {
    struct Label { uint32_t node = 0, epoch = 0; uint64_t distance = 0; };
    std::vector<Label> labels = std::vector<Label>(4096);
    uint32_t epoch = 0;
    size_t used = 0;
    static size_t hash(uint32_t node) {
        node ^= node >> 16; node *= 0x7feb352dU;
        node ^= node >> 15; node *= 0x846ca68bU;
        return node ^ (node >> 16);
    }
    void reset() {
        if (++epoch == 0) {
            for (auto& label : labels) label.epoch = 0;
            epoch = 1;
        }
        used = 0;
    }
    size_t slot(uint32_t node) const {
        size_t index = hash(node) & (labels.size() - 1);
        while (labels[index].epoch == epoch && labels[index].node != node)
            index = (index + 1) & (labels.size() - 1);
        return index;
    }
    uint64_t get(uint32_t node) const {
        if (!used) return UINT64_MAX;
        const auto& label = labels[slot(node)];
        return label.epoch == epoch ? label.distance : UINT64_MAX;
    }
    bool improve(uint32_t node, uint64_t distance) {
        if (used * 2 >= labels.size()) {
            auto previous = std::move(labels);
            labels.resize(previous.size() * 2);
            for (const auto& label : previous) if (label.epoch == epoch) labels[slot(label.node)] = label;
        }
        auto& label = labels[slot(node)];
        if (label.epoch == epoch && label.distance <= distance) return false;
        used += label.epoch != epoch;
        label = Label{node, epoch, distance};
        return true;
    }
};

// A query owns its primary cells until release. Overlap and 64-bit distances use
// the private exact table; no worker can replace another active query's label.
struct SharedDistances {
    std::atomic<uint64_t>* primary;
    uint64_t token = 0;
    Distances fallback;
    std::vector<uint32_t> claimed;
    explicit SharedDistances(std::atomic<uint64_t>* cells) : primary(cells) {}
    ~SharedDistances() { release(); }
    void release() {
        for (uint32_t node : claimed) primary[node].store(0, std::memory_order_release);
        claimed.clear();
    }
    void reset(size_t query) { release(); fallback.reset(); token = uint64_t(query + 1) << 32; }
    uint64_t get(uint32_t node) const {
        uint64_t cell = primary[node].load(std::memory_order_relaxed);
        return (cell & 0xffffffff00000000ULL) == token ? uint32_t(cell) : fallback.get(node);
    }
    bool improve(uint32_t node, uint64_t distance) {
        uint64_t cell = primary[node].load(std::memory_order_relaxed);
        bool owned = (cell & 0xffffffff00000000ULL) == token;
        uint64_t previous = owned ? uint32_t(cell) : fallback.get(node);
        if (distance >= previous) return false;
        if (distance < UINT32_MAX) {
            if (owned) { primary[node].store(token | distance, std::memory_order_relaxed); return true; }
            if (cell == 0) {
                claimed.push_back(node);
                if (primary[node].compare_exchange_strong(cell, token | distance, std::memory_order_relaxed)) return true;
                claimed.pop_back();
            }
        }
        return fallback.improve(node, distance);
    }
};
