#pragma once
#include <algorithm>
#include <array>
#include <atomic>
#include <cstdint>
#include <cstring>
#include <functional>
#include <memory>
#include <stdexcept>
#include <string_view>
#include <vector>
#include <utility>

struct SharedCanceled {};
struct KeyArena {
    std::vector<std::unique_ptr<char[]>> blocks;char* next=nullptr;size_t remaining=0;
    const char* copy(std::string_view value){
        if(value.size()>remaining){size_t bytes=std::max<size_t>(65536,value.size());std::unique_ptr<char[]> owned(new char[bytes]);blocks.push_back(std::move(owned));next=blocks.back().get();remaining=bytes;}
        char* result=next;std::memcpy(result,value.data(),value.size());next+=value.size();remaining-=value.size();return result;
    }
};
struct SharedNames {
    //24 payload bytes plus full length and4 atomic words fill one64-byte key.
    struct alignas(64) Key {std::array<uint64_t,3> payload{};size_t length=0;std::array<std::atomic<uint64_t>,4> flags{};};
    static_assert(sizeof(Key)==64&&sizeof(const char*)<=sizeof(std::array<uint64_t,3>));
    static_assert(std::atomic<uint64_t>::is_always_lock_free&&std::atomic<Key*>::is_always_lock_free);
    static constexpr size_t block_size=2048;
    size_t capacity,words,countries;
    std::unique_ptr<std::atomic<uint64_t>[]> slots,spill;
    std::unique_ptr<std::atomic<Key*>[]> published;
    std::vector<std::unique_ptr<Key[]>> blocks;
    std::atomic<size_t> used{0};std::atomic<bool> canceled{false},too_small{false};
    SharedNames(size_t count,size_t groups):capacity(count),words(0),countries(groups){
        if(!count||(count&(count-1))||count>UINT32_MAX-2||count>SIZE_MAX/2/sizeof(std::atomic<uint64_t>)||count>SIZE_MAX/sizeof(Key)||groups>SIZE_MAX-63)
            throw std::runtime_error("shared name table size overflow");
        words=(groups+63)/64;
        if(words>4&&count>SIZE_MAX/(words-4)/sizeof(std::atomic<uint64_t>))throw std::runtime_error("shared country storage overflow");
        slots=std::make_unique<std::atomic<uint64_t>[]>(count*2);
        size_t block_count=count/block_size+bool(count%block_size);blocks.resize(block_count);published=std::make_unique<std::atomic<Key*>[]>(block_count);
        if(words>4)spill=std::make_unique<std::atomic<uint64_t>[]>(count*(words-4));
    }
    static uint64_t hash_key(std::string_view key){uint64_t h=std::hash<std::string_view>{}(key);return h<2?h+2:h;}
    Key& at(size_t id)const{return published[id/block_size].load(std::memory_order_acquire)[id%block_size];}
    std::string_view bytes(size_t id)const{
        const auto& key=at(id);const char* data=reinterpret_cast<const char*>(key.payload.data());
        if(key.length>sizeof(key.payload))std::memcpy(&data,key.payload.data(),sizeof(data));
        return {data,key.length};
    }
    void store(size_t id,std::string_view value,KeyArena& arena){
        size_t block=id/block_size,offset=id%block_size;Key* data;
        if(!offset){blocks[block]=std::make_unique<Key[]>(std::min(block_size,capacity-id));data=blocks[block].get();published[block].store(data,std::memory_order_release);}
        else while(!(data=published[block].load(std::memory_order_acquire))){if(canceled.load(std::memory_order_relaxed))throw SharedCanceled{};}
        auto& key=data[offset];
        if(value.size()<=sizeof(key.payload)){if(!value.empty())std::memcpy(key.payload.data(),value.data(),value.size());}
        else{const char* pointer=arena.copy(value);std::memcpy(key.payload.data(),&pointer,sizeof(pointer));}
        key.length=value.size();
    }
    bool mark(size_t id,size_t country){
        size_t word=country/64;uint64_t bit=uint64_t(1)<<(country%64);
        auto& field=word<4?at(id).flags[word]:spill[id*(words-4)+word-4];
        return !(field.fetch_or(bit,std::memory_order_relaxed)&bit);
    }
    bool first(std::string_view value,size_t country,uint64_t hash,KeyArena& arena){
        if(country>=countries)throw std::runtime_error("country outside shared table");
        if(canceled.load(std::memory_order_relaxed))throw SharedCanceled{};
        const uint64_t fingerprint=hash&0xffffffff00000000ULL;size_t position=hash&(capacity*2-1);
        for(size_t probes=0;probes<capacity*2;++probes){
            auto& slot=slots[position];uint64_t state=slot.load(std::memory_order_acquire);
            if(!state&&slot.compare_exchange_strong(state,1,std::memory_order_acq_rel)){
                size_t id=used.fetch_add(1,std::memory_order_relaxed);
                if(id>=capacity){too_small.store(true,std::memory_order_relaxed);canceled.store(true,std::memory_order_relaxed);slot.store(0,std::memory_order_release);throw SharedCanceled{};}
                try{store(id,value,arena);}catch(...){canceled.store(true,std::memory_order_relaxed);slot.store(0,std::memory_order_release);throw;}
                slot.store(fingerprint|uint64_t(id+2),std::memory_order_release);return mark(id,country);
            }
            while(state==1){if(canceled.load(std::memory_order_relaxed))throw SharedCanceled{};state=slot.load(std::memory_order_acquire);}
            if(state>1&&(state&0xffffffff00000000ULL)==fingerprint){size_t id=uint32_t(state)-2;if(bytes(id)==value)return mark(id,country);}
            if(canceled.load(std::memory_order_relaxed))throw SharedCanceled{};
            position=(position+1)&(capacity*2-1);
        }
        throw std::runtime_error("shared name slots full");
    }
};
