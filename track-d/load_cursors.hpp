#pragma once
#include <algorithm>
#include <atomic>
#include <cstdint>
#include <cstddef>
#include <unordered_map>
#include <vector>

static_assert(std::atomic_ref<uint8_t>::required_alignment <= alignof(uint8_t));
static_assert(std::atomic_ref<uint16_t>::required_alignment <= alignof(uint16_t));

struct DegreeBytes {
    using Spills = std::unordered_map<uint32_t,uint32_t>;
    std::vector<uint8_t> values;
    explicit DegreeBytes(std::size_t nodes) : values(nodes) {}
    void add(uint32_t node, Spills& spills) {
        // Every wrap has exactly one observer; its private spill restores256.
        if (std::atomic_ref(values[node]).fetch_add(1,std::memory_order_relaxed)==UINT8_MAX) spills[node]+=256;
    }
    void release() { std::vector<uint8_t>().swap(values); }
};
struct SharedCursor {
    static constexpr unsigned shift=12, block_size=1U<<shift;
    std::vector<uint32_t> base, wide_index;
    std::vector<uint16_t> small;
    std::vector<uint32_t> wide;
    std::size_t wide_blocks=0;
    explicit SharedCursor(const std::vector<uint32_t>& starts) {
        std::size_t nodes=starts.size()-1, blocks=(nodes+block_size-1)/block_size;
        base.resize(blocks);wide_index.resize(blocks,UINT32_MAX);
        for(std::size_t block=0;block<blocks;++block) {
            std::size_t begin=block*block_size,end=std::min(nodes,begin+block_size);base[block]=starts[begin];
            if(starts[end]-starts[begin]>UINT16_MAX)wide_index[block]=static_cast<uint32_t>(wide_blocks++);
        }
        small.resize(nodes);wide.resize(wide_blocks*block_size);
        for(std::size_t node=0;node<nodes;++node) {
            std::size_t block=node>>shift;uint32_t index=wide_index[block];
            if(index==UINT32_MAX)small[node]=static_cast<uint16_t>(starts[node]-base[block]);
            else wide[std::size_t(index)*block_size+(node&(block_size-1))]=starts[node];
        }
    }
    template<bool HasWide> uint32_t take(uint32_t node) {
        std::size_t block=node>>shift;
        if constexpr(HasWide) {
            uint32_t index=wide_index[block];
            if(index!=UINT32_MAX)return std::atomic_ref(wide[std::size_t(index)*block_size+(node&(block_size-1))]).fetch_add(1,std::memory_order_relaxed);
        }
        return base[block]+std::atomic_ref(small[node]).fetch_add(1,std::memory_order_relaxed);
    }
    template<bool HasWide> void prefetch(uint32_t node) const {
        if constexpr (HasWide) {
            uint32_t index = wide_index[node >> shift];
            if (index != UINT32_MAX) { __builtin_prefetch(&wide[size_t(index) * block_size + (node & (block_size - 1))], 1, 1); return; }
        }
        __builtin_prefetch(&small[node], 1, 1);
    }
    uint32_t take(uint32_t node) {return wide_blocks ? take<true>(node):take<false>(node);}
    void release(){std::vector<uint16_t>().swap(small);std::vector<uint32_t>().swap(wide);}
};
