#pragma once
#include <cstddef>
#include <cstdint>
#include <utility>
#include <vector>

struct __attribute__((packed)) WideEdge { uint32_t to; uint16_t weight; };
static_assert(sizeof(WideEdge) == 6);

// Select the representation once from the graph header, then specialize the
// hot loops. Destinations beyond21 bits retain the exact six-byte layout.
struct EdgeStore {
    static constexpr uint32_t node_bits = 21, node_mask = (1U << node_bits) - 1;
    static constexpr uint32_t small_limit = (1U << (32 - node_bits)) - 1;
    bool compact;
    uint32_t weight_limit;
    std::vector<uint32_t> small;
    std::vector<WideEdge> wide;
    EdgeStore(std::size_t count, uint32_t nodes) : compact(nodes <= node_mask + 1),
        weight_limit(compact ? small_limit : UINT16_MAX) {
        if (compact) small.resize(count); else wide.resize(count);
    }
    template<bool Compact> void set(uint32_t index, uint32_t node, uint32_t tag) {
        if constexpr (Compact) small[index] = node | tag << node_bits;
        else wide[index] = WideEdge{node, static_cast<uint16_t>(tag)};
    }
    template<bool Compact> std::pair<uint32_t, uint32_t> get(uint32_t index) const {
        if constexpr (Compact) { uint32_t value = small[index]; return {value & node_mask, value >> node_bits}; }
        else { uint32_t node = wide[index].to, tag = wide[index].weight; return {node, tag}; }
    }
    void set(uint32_t index, uint32_t node, uint32_t tag) {
        if (compact) set<true>(index,node,tag); else set<false>(index,node,tag);
    }
    std::pair<uint32_t,uint32_t> get(uint32_t index) const { return compact ? get<true>(index) : get<false>(index); }
    template<bool Compact> void prefetch(uint32_t index) const {
        if constexpr (Compact) __builtin_prefetch(&small[index], 0, 1);
        else __builtin_prefetch(&wide[index], 0, 1);
    }
};
