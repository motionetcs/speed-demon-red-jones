#pragma once
#define SPEED_DEMON_OFFSET_NAMES 1
#include <algorithm>
#include <bit>
#if defined(__SSE2__)
#include <immintrin.h>
#elif defined(__ARM_NEON)
#include <arm_neon.h>
#endif
#include <atomic>
#include <thread>
#include <cstdint>
#include <cstring>
#include <functional>
#include <memory>
#include <new>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

// One owner owns the relocatable arena. Word indices survive every growth.
struct Names {
    struct Group {uint32_t hashes[4]={},indices[4]={};};
    static_assert(sizeof(Group)==32);
    std::vector<Group> entries;std::vector<std::unique_ptr<uint64_t[]>> storage;size_t words,used=0,next=0,remaining=0;
    explicit Names(size_t countries):entries(4096),words((countries+63)/64){}
    static uint64_t hash_key(std::string_view key){uint64_t h=std::hash<std::string_view>{}(key);return h<2?h+2:h;}
    static uint32_t encode_index(size_t block,size_t word){
        if(block>=(size_t(1)<<19)||word>=8192)throw std::runtime_error("name block/word index capacity");
        uint32_t encoded=(static_cast<uint32_t>(block)<<13)|static_cast<uint32_t>(word);
        if(encoded==UINT32_MAX)throw std::runtime_error("name word index capacity");
        return encoded+1;
    }
    uint32_t make(std::string_view value){
        if(value.size()>UINT32_MAX||words>SIZE_MAX-1-(value.size()+7)/8)throw std::runtime_error("name storage overflow");
        size_t extra=1+words+(value.size()+7)/8;
        if(extra>SIZE_MAX/sizeof(uint64_t))throw std::runtime_error("name allocation overflow");
        if(extra>remaining){
            if(storage.size()>=size_t(1)<<19)throw std::runtime_error("name block index capacity");
            size_t capacity=std::max<size_t>(8192,extra);storage.emplace_back(new uint64_t[capacity]);next=0;remaining=capacity;
        }
        // Oversized keys use a dedicated block with a representable zero offset.
        if(next>=8192||next+extra>8192){
            if(next!=0){remaining=0;return make(value);}
        }
        uint32_t index=encode_index(storage.size()-1,next);
        auto* data=storage.back().get()+next;std::fill_n(data,1+words,uint64_t(0));data[0]=value.size();
        if(!value.empty())std::memcpy(reinterpret_cast<char*>(data+1+words),value.data(),value.size());
        next+=extra;remaining=next<8192?8192-next:0;return index;
    }
    uint64_t* at(uint32_t index)const{uint32_t encoded=index-1;return storage[encoded>>13].get()+(encoded&8191);}
    std::string_view bytes(uint32_t index)const{
        auto* data=at(index);return {reinterpret_cast<const char*>(data+1+words),static_cast<size_t>(data[0])};
    }
    static constexpr unsigned lane_bits=
#if defined(__ARM_NEON) && !defined(__SSE2__) && __BYTE_ORDER__==__ORDER_LITTLE_ENDIAN__
        16;
#else
        1;
#endif
    static uint64_t equal_lanes(const uint32_t* p,uint32_t key){
#if defined(__SSE2__)
        auto values=_mm_loadu_si128(reinterpret_cast<const __m128i*>(p));
        return static_cast<unsigned>(_mm_movemask_ps(_mm_castsi128_ps(_mm_cmpeq_epi32(values,_mm_set1_epi32(key)))));
#elif defined(__ARM_NEON) && __BYTE_ORDER__==__ORDER_LITTLE_ENDIAN__
        auto matches=vceqq_u32(vld1q_u32(p),vdupq_n_u32(key));
        return vget_lane_u64(vreinterpret_u64_u16(vmovn_u32(matches)),0);
#else
        uint64_t mask=0;for(unsigned i=0;i<4;++i)mask|=uint64_t(p[i]==key)<<i;return mask;
#endif
    }
    static unsigned lane(uint64_t mask){return std::countr_zero(mask)/lane_bits;}
    static size_t home(uint32_t fingerprint,size_t size){return (fingerprint>>2)&(size-1);}
    void grow(){
        if(entries.size()>SIZE_MAX/2/sizeof(Group))throw std::runtime_error("name table overflow");
        std::vector<Group> larger(entries.size()*2);
        for(const auto& group:entries)for(unsigned j=0;j<4;++j)if(group.indices[j]){
            size_t i=home(group.hashes[j],larger.size());
            for(;;){uint64_t empty=equal_lanes(larger[i].indices,0);
                if(empty){unsigned k=lane(empty);larger[i].hashes[k]=group.hashes[j];larger[i].indices[k]=group.indices[j];break;}
                i=(i+1)&(larger.size()-1);
            }
        }
        entries.swap(larger);
    }
    bool first(std::string_view key,size_t country,uint64_t hash){
        uint32_t fingerprint=static_cast<uint32_t>(hash),selected=0;size_t i=home(fingerprint,entries.size());
        for(;;){
            auto& group=entries[i];uint64_t empty=equal_lanes(group.indices,0);
            uint64_t matches=equal_lanes(group.hashes,fingerprint)&~empty;
            while(matches){unsigned j=lane(matches);
                if(bytes(group.indices[j])==key){selected=group.indices[j];break;}
                matches&=~(((uint64_t(1)<<lane_bits)-1)<<(j*lane_bits));
            }
            if(selected)break;
            if(empty){
                if(used>=entries.size()*7/2){grow();i=home(fingerprint,entries.size());continue;}
                unsigned j=lane(empty);selected=make(key);group.hashes[j]=fingerprint;group.indices[j]=selected;++used;break;
            }
            i=(i+1)&(entries.size()-1);
        }
        auto& bits=at(selected)[1+country/64];uint64_t bit=uint64_t(1)<<(country%64);
        bool fresh=!(bits&bit);bits|=bit;return fresh;
    }

};
struct NameEvent {
    std::string_view key;uint64_t hash;uint16_t country;
    std::string_view value()const{return key;}
};
// One producer and one consumer transfer a vector through release/acquire.
// Every key borrows immutable input; the consumer copies each unique key.
struct NameQueue {
    alignas(64) std::atomic<bool> ready{false};std::vector<NameEvent> rows;
    void send(std::vector<NameEvent>& batch,const std::atomic<bool>& canceled){
        while(ready.load(std::memory_order_acquire)){
            if(canceled.load(std::memory_order_relaxed))throw std::runtime_error("name pipeline canceled");
            std::this_thread::yield();
        }
        if(canceled.load(std::memory_order_relaxed))throw std::runtime_error("name pipeline canceled");
        rows.swap(batch);ready.store(true,std::memory_order_release);
    }
};
