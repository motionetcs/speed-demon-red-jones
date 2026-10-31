#pragma once
#include <cstdint>
#include <array>
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

// Private compact labels keep ordinary searches in cache. Large distances and
// the UINT32_MAX node key have an exact 64-bit fallback.
struct FastDistances {
    std::vector<uint64_t> labels = std::vector<uint64_t>(4096);
    std::vector<uint32_t> touched;
    Distances wide;
    std::array<uint64_t, 1024> seen{};
    static uint32_t filter_bit(uint32_t node) { return (node * 0x9e3779b1U) >> 16; }
    uint64_t maybe_get(uint32_t node) const {
        uint32_t bit = filter_bit(node);
        return (seen[bit / 64] & (uint64_t(1) << (bit % 64))) ? get(node) : UINT64_MAX;
    }
    size_t slot(uint32_t node) const {
        size_t index = (node * 0x9e3779b1U) & (labels.size() - 1);
        while (labels[index] && uint32_t(labels[index] >> 32) != node + 1) index = (index + 1) & (labels.size() - 1);
        return index;
    }
    void reset() { for (uint32_t index : touched) labels[index] = 0; touched.clear(); wide.reset(); seen.fill(0); }
    uint64_t get(uint32_t node) const {
        if (node == UINT32_MAX || touched.empty()) return wide.get(node);
        uint64_t label = labels[slot(node)];
        return label ? uint32_t(label) : wide.get(node);
    }
    bool improve(uint32_t node, uint64_t distance) {
        uint32_t bit = filter_bit(node); seen[bit / 64] |= uint64_t(1) << (bit % 64);
        if (node == UINT32_MAX) return wide.improve(node, distance);
        size_t index = slot(node);
        uint64_t previous = labels[index] ? uint32_t(labels[index]) : wide.get(node);
        if (distance >= previous) return false;
        if (distance > UINT32_MAX) return wide.improve(node, distance);
        if (!labels[index]) {
            if (touched.size() * 2 >= labels.size()) {
                auto old = std::move(labels); labels.assign(old.size() * 2, 0);
                for (auto& used : touched) {
                    uint64_t item = old[used]; used = static_cast<uint32_t>(slot(uint32_t(item >> 32) - 1)); labels[used] = item;
                }
                index = slot(node);
            }
            touched.push_back(static_cast<uint32_t>(index));
        }
        labels[index] = uint64_t(node + 1) << 32 | distance;
        return true;
    }
};
