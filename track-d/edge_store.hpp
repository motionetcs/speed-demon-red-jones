#pragma once
#include <algorithm>
#include <bit>
#include <cstdint>
#include <cstddef>
#include <utility>
#include <vector>

struct __attribute__((packed)) WideEdge { uint32_t to; uint16_t weight; };
static_assert(sizeof(WideEdge) == 6);

// A single32-bit word holds a destination and a small weight when node IDs fit.
// The sentinel redirects to the exact full-weight side table; large node spaces
// retain the original six-byte representation instead of truncating IDs.
struct EdgeStore {
    uint32_t node_bits, node_mask, weight_limit;
    bool compact;
    std::vector<uint32_t> small;
    std::vector<WideEdge> wide;
    EdgeStore(std::size_t count, uint32_t nodes) : node_bits(std::max<unsigned>(1, std::bit_width(nodes ? nodes - 1 : 0))),
        node_mask(node_bits == 32 ? UINT32_MAX : (uint32_t(1) << node_bits) - 1),
        weight_limit(node_bits <= 24 ? (uint32_t(1) << (32 - node_bits)) - 1 : UINT16_MAX),
        compact(node_bits <= 24) {
        if (compact) small.resize(count); else wide.resize(count);
    }
    void set(uint32_t index, uint32_t node, uint32_t weight) {
        if (compact) small[index] = node | weight << node_bits;
        else wide[index] = WideEdge{node, static_cast<uint16_t>(weight)};
    }
    std::pair<uint32_t, uint32_t> get(uint32_t index) const {
        if (compact) { uint32_t value = small[index]; return {value & node_mask, value >> node_bits}; }
        uint32_t node = wide[index].to, weight = wide[index].weight;
        return {node, weight};
    }
    void prefetch(uint32_t index) const {
        if (compact) __builtin_prefetch(&small[index], 0, 1);
        else __builtin_prefetch(&wide[index], 0, 1);
    }
};
