#pragma once
#define SPEED_DEMON_OFFSET_NAMES 1
#include <algorithm>
#include <atomic>
#include <thread>
#include <cstdint>
#include <cstring>
#include <functional>
#include "name_hash.hpp"
#include <memory>
#include <new>
#include <stdexcept>
#include <string>
#include <string_view>
#include <vector>

// One owner owns the relocatable arena. Word indices survive every growth.
struct Names {
    struct Entry {uint32_t hash=0,index=0;};
    std::vector<Entry> entries;std::vector<std::unique_ptr<uint64_t[]>> storage;size_t words,used=0,next=0,remaining=0;
    explicit Names(size_t countries):entries(16384),words((countries+63)/64){}
    static uint64_t hash_key(std::string_view key){return whole_name_hash(key);}
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
    void grow(){
        if(entries.size()>SIZE_MAX/2/sizeof(Entry))throw std::runtime_error("name table overflow");
        std::vector<Entry> larger(entries.size()*2);
        for(auto e:entries)if(e.index){size_t i=e.hash&(larger.size()-1);while(larger[i].index)i=(i+1)&(larger.size()-1);larger[i]=e;}
        entries.swap(larger);
    }
    bool first(std::string_view key,size_t country,uint64_t hash){
        uint32_t fingerprint=static_cast<uint32_t>(hash);size_t i=fingerprint&(entries.size()-1);
        for(;;){
            auto& e=entries[i];
            if(!e.index){
                if(used>=entries.size()*7/8){grow();i=fingerprint&(entries.size()-1);continue;}
                uint32_t index=make(key);e={fingerprint,index};++used;break;
            }
            if(e.hash==fingerprint&&bytes(e.index)==key)break;
            i=(i+1)&(entries.size()-1);
        }
        auto& bits=at(entries[i].index)[1+country/64];uint64_t bit=uint64_t(1)<<(country%64);
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
