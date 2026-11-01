#pragma once
#include <cstdint>
#include <bit>
#include <stdexcept>
#if defined(__SSE2__)
#include <immintrin.h>
#elif defined(__ARM_NEON)
#include <arm_neon.h>
#endif
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

// A bucket supplies a node's low bits; its packed tag stores every remaining
// bit of a21-bit node ID. Low distance bits store distance+1 (zero means empty).
// Nodes/ranges that do not fit, and full buckets, use the exact64-bit map.
#ifndef PACKED_BITS
#define PACKED_BITS 10
#endif
struct FastDistances {
    static_assert(PACKED_BITS>=0 && PACKED_BITS<=20);
    unsigned bits=PACKED_BITS;
    std::vector<uint32_t> labels=std::vector<uint32_t>(size_t(8)<<PACKED_BITS);
    std::vector<uint32_t> touched;
    Distances wide;
    static constexpr uint32_t node_limit=1U<<21;
    uint32_t distance_mask()const{return (uint32_t(1)<<(11+bits))-1;}
    size_t slot(uint32_t node)const{
        size_t start=size_t(node&((1U<<bits)-1))*8;
        unsigned shift=11+bits;uint32_t key=node>>bits;
        for(unsigned block=0;block<8;block+=4){
#if defined(__SSE2__)
            auto values=_mm_loadu_si128(reinterpret_cast<const __m128i*>(&labels[start+block]));
            auto tags=_mm_srl_epi32(values,_mm_cvtsi32_si128(shift));
            auto matches=_mm_or_si128(_mm_cmpeq_epi32(tags,_mm_set1_epi32(key)),_mm_cmpeq_epi32(values,_mm_setzero_si128()));
            unsigned mask=static_cast<unsigned>(_mm_movemask_ps(_mm_castsi128_ps(matches)));
            if(mask)return start+block+std::countr_zero(mask);
#elif defined(__ARM_NEON) && __BYTE_ORDER__==__ORDER_LITTLE_ENDIAN__
            auto values=vld1q_u32(&labels[start+block]);auto tags=vshlq_u32(values,vdupq_n_s32(-int(shift)));
            auto matches=vorrq_u32(vceqq_u32(tags,vdupq_n_u32(key)),vceqq_u32(values,vdupq_n_u32(0)));
            uint64_t mask=vget_lane_u64(vreinterpret_u64_u16(vmovn_u32(matches)),0);
            if(mask)return start+block+std::countr_zero(mask)/16;
#else
            for(unsigned i=0;i<4;++i){auto v=labels[start+block+i];if(!v||(v>>shift)==key)return start+block+i;}
#endif
        }
        return labels.size();
    }
    void prefetch(uint32_t node)const{
        if(node<node_limit)__builtin_prefetch(&labels[size_t(node&((1U<<bits)-1))*8],0,1);
    }
    void grow(){
        unsigned old_bits=bits,old_shift=11+bits;uint32_t old_mask=distance_mask();
        auto previous=std::move(labels);++bits;labels.assign(previous.size()*2,0);
        for(auto& index:touched){
            uint32_t value=previous[index];uint32_t node=((value>>old_shift)<<old_bits)|(index>>3);
            size_t next=slot(node);if(next==labels.size())throw std::logic_error("packed rehash overflow");
            index=static_cast<uint32_t>(next);labels[next]=((node>>bits)<<(11+bits))|(value&old_mask);
        }
    }
    void reset(){for(uint32_t index:touched)labels[index]=0;touched.clear();wide.reset();}
    uint64_t get(uint32_t node)const{
        if(node>=node_limit||touched.empty())return wide.get(node);
        size_t index=slot(node);uint32_t value=index<labels.size()?labels[index]:0;
        return value?uint64_t((value&distance_mask())-1):wide.get(node);
    }
    bool improve(uint32_t node,uint64_t distance){
        if(node>=node_limit)return wide.improve(node,distance);
        if(touched.size()*2>=labels.size()&&bits<20)grow();
        size_t index=slot(node);
        if(index==labels.size())return wide.improve(node,distance);
        uint32_t value=labels[index];uint64_t previous=value?uint64_t((value&distance_mask())-1):wide.get(node);
        if(distance>=previous)return false;
        if(distance>=distance_mask())return wide.improve(node,distance);
        if(!value)touched.push_back(static_cast<uint32_t>(index));
        labels[index]=((node>>bits)<<(11+bits))|static_cast<uint32_t>(distance+1);return true;
    }
};
