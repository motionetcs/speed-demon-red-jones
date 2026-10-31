#pragma once
#include <algorithm>
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

struct alignas(8) NameKey { uint32_t length, padding; };
struct StringArena {
    std::vector<std::unique_ptr<char[]>> blocks;
    char* next=nullptr;size_t remaining=0;
    NameKey* make(std::string_view value,size_t words){
        if(value.size()>UINT32_MAX||words>(SIZE_MAX-sizeof(NameKey)-value.size()-7)/sizeof(uint64_t))throw std::runtime_error("name storage overflow");
        size_t bytes=(sizeof(NameKey)+words*sizeof(uint64_t)+value.size()+7)&~size_t(7);
        if(bytes>remaining){size_t capacity=std::max<size_t>(65536,bytes);blocks.emplace_back(new char[capacity]);next=blocks.back().get();remaining=capacity;}
        auto* key=::new(static_cast<void*>(next))NameKey{static_cast<uint32_t>(value.size()),0};
        ::new(static_cast<void*>(next+sizeof(NameKey)))uint64_t[words]{};
        if(!value.empty())std::memcpy(next+sizeof(NameKey)+words*sizeof(uint64_t),value.data(),value.size());
        next+=bytes;remaining-=bytes;return key;
    }
};
// One owner mutates this exact table and its per-name membership words.
struct Names {
    struct Entry{uint64_t hash=0;NameKey* key=nullptr;};
    std::vector<Entry> entries;size_t words,used=0;StringArena storage;
    explicit Names(size_t countries):entries(16384),words((countries+63)/64){}
    static uint64_t hash_key(std::string_view key){uint64_t h=std::hash<std::string_view>{}(key);return h<2?h+2:h;}
    std::string_view bytes(const NameKey* key)const{return {reinterpret_cast<const char*>(key)+sizeof(NameKey)+words*sizeof(uint64_t),key->length};}
    void grow(){
        if(entries.size()>SIZE_MAX/2/sizeof(Entry))throw std::runtime_error("name table overflow");
        std::vector<Entry> larger(entries.size()*2);
        for(auto e:entries)if(e.hash){size_t i=e.hash&(larger.size()-1);while(larger[i].hash)i=(i+1)&(larger.size()-1);larger[i]=e;}
        entries.swap(larger);
    }
    bool first(std::string_view key,size_t country,uint64_t hash){
        size_t i=hash&(entries.size()-1);
        for(;;){
            auto& e=entries[i];
            if(!e.hash){
                if(used>=entries.size()*7/8){grow();i=hash&(entries.size()-1);continue;}
                auto* stored=storage.make(key,words);e.key=stored;e.hash=hash;++used;break;
            }
            if(e.hash==hash&&bytes(e.key)==key)break;
            i=(i+1)&(entries.size()-1);
        }
        auto* bits=reinterpret_cast<uint64_t*>(reinterpret_cast<char*>(entries[i].key)+sizeof(NameKey));
        uint64_t bit=uint64_t(1)<<(country%64);bool fresh=!(bits[country/64]&bit);bits[country/64]|=bit;return fresh;
    }
};
struct NameEvent {
    std::string_view key;uint64_t hash;uint16_t country;
    std::string_view value()const{return key;}
};
// One producer and one consumer transfer a vector through release/acquire.
// Every key borrows immutable input; the consumer copies each unique key.
inline void name_pause(unsigned& spins){
    if(++spins==128){spins=0;std::this_thread::yield();return;}
#if defined(__x86_64__) || defined(__i386__)
    __builtin_ia32_pause();
#elif defined(__aarch64__)
    __asm__ volatile("yield");
#else
    std::atomic_signal_fence(std::memory_order_seq_cst);
#endif
}
struct NameQueue {
    alignas(64) std::atomic<bool> ready{false};std::vector<NameEvent> rows;
    void send(std::vector<NameEvent>& batch,const std::atomic<bool>& canceled){
        unsigned spins=0;
        while(ready.load(std::memory_order_acquire)){
            if(canceled.load(std::memory_order_relaxed))throw std::runtime_error("name pipeline canceled");
            name_pause(spins);
        }
        if(canceled.load(std::memory_order_relaxed))throw std::runtime_error("name pipeline canceled");
        rows.swap(batch);ready.store(true,std::memory_order_release);
    }
};
