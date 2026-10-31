#ifndef NAMES_HEADER
#define NAMES_HEADER "../track-c/names.hpp"
#endif
#include NAMES_HEADER
#include <array>
#include <cassert>
#include <iostream>
#include <set>
#include <string>
#include <thread>
#include <tuple>

template<class Table> NameKey* intern_key(Table& table, std::string_view key, StringArena& arena, uint64_t hash) {
    auto&& result=table.intern(key,arena,hash);
    if constexpr(std::is_pointer_v<std::remove_reference_t<decltype(result)>>)return result;
    else return result.key;
}
template<class Table> bool first_key(Table& table, NameKey* key, size_t country) {
    if constexpr(requires{table.first(key,country);})return table.first(key,country);
    else {typename Table::Entry entry;entry.key=key;return table.first(entry,country);}
}

int main() {
    for (size_t words : {1U,4U,5U,275U}) {
        StringArena arena; Names view(128,words*64);
        std::vector<std::pair<NameKey*,std::string>> saved;
        for (size_t size : {0U,1U,7U,8U,63U,64U,65535U,65536U,65537U,1048576U}) {
            std::string value(size, 'x'); for (size_t i=0;i<size;++i) value[i]=char(i%251);
            NameKey* key=arena.make(value,words); assert(key->length==size);
            assert(reinterpret_cast<uintptr_t>(key)%alignof(NameKey)==0);
            for(size_t i=0;i<words*64;++i){assert(first_key(view,key,i));assert(!first_key(view,key,i));}
            saved.emplace_back(key,std::move(value));
        }
        for(unsigned i=0;i<10000;++i)arena.make(std::to_string(i),words);
        for(const auto& [key,value]:saved) {
            assert(view.bytes(key)==value);
            for(size_t i=0;i<words*64;++i)assert(!first_key(view,key,i));
        }
        bool threw=false;try{arena.make("x",SIZE_MAX);}catch(const std::runtime_error&){threw=true;}assert(threw);
    }
    for(size_t countries : {1U,64U,65U,241U,300U,17576U}) {
        Names names(128,countries);StringArena arena;std::vector<NameKey*> entries;
        for(unsigned i=0;i<60;++i){std::string key=i ? "collision/"+std::to_string(i):"";auto* entry=intern_key(names,key,arena,42);entries.push_back(entry);assert(names.bytes(entry)==key);assert(first_key(names,entry,countries-1));assert(!first_key(names,entry,countries-1));}
        for(unsigned i=0;i<60;++i){std::string key=i ? "collision/"+std::to_string(i):"";assert(intern_key(names,key,arena,42)==entries[i]);}
        assert(names.used.load()==60);
    }
    constexpr unsigned workers=4,updates=10000,key_count=1000,countries=300;
    Names names(2048,countries);std::array<StringArena,workers> arenas;
    std::vector<std::string> keys;for(unsigned i=0;i<key_count;++i)keys.push_back("name/"+std::to_string(i));
    keys[0]="";keys[1]=std::string("a\0b",3);keys[2]="UTF-8 \xe5\x90\x8d";keys[3]=std::string(65537,'z');
    std::set<std::pair<unsigned,unsigned>> expected;
    for(unsigned w=0;w<workers;++w)for(unsigned i=0;i<updates;++i)expected.emplace((i*7+w*13)%key_count,(i*17+w*31)%countries);
    std::array<std::atomic<unsigned>,countries> counts{};std::vector<std::thread> threads;
    for(unsigned w=0;w<workers;++w)threads.emplace_back([&,w]{for(unsigned i=0;i<updates;++i){unsigned key=(i*7+w*13)%key_count,country=(i*17+w*31)%countries;uint64_t hash=key%10 ? Names::hash_key(keys[key]):42;auto* entry=intern_key(names,keys[key],arenas[w],hash);if(first_key(names,entry,country))counts[country].fetch_add(1,std::memory_order_relaxed);}});
    for(auto& thread:threads)thread.join();std::array<unsigned,countries> reference{};for(auto [key,country]:expected)++reference[country];
    for(unsigned c=0;c<countries;++c)assert(counts[c].load()==reference[c]);assert(names.used.load()==key_count);
    std::cout<<"PASS stable name blocks, large/empty/NUL/UTF-8 keys, deliberate collisions, country-word boundaries, parallel std::set model\n";
}
