#include "../track-c/names.hpp"
#include <array>
#include <cassert>
#include <iostream>
#include <set>
#include <string>
#include <thread>
#include <tuple>

int main() {
    for (size_t words : {1U,4U,5U,275U}) {
        StringArena arena;
        std::vector<std::pair<NameKey*,std::string>> saved;
        for (size_t size : {0U,1U,7U,8U,63U,64U,65535U,65536U,65537U,1048576U}) {
            std::string value(size, 'x'); for (size_t i=0;i<size;++i) value[i]=char(i%251);
            NameKey* key=arena.make(value,words); assert(key->length==size);
            assert(reinterpret_cast<uintptr_t>(key)%alignof(NameKey)==0);
            auto* bits=reinterpret_cast<std::atomic<uint64_t>*>(reinterpret_cast<char*>(key)+sizeof(NameKey));
            for(size_t i=0;i<words;++i){assert(bits[i].load()==0);bits[i].store(UINT64_MAX-i);}
            saved.emplace_back(key,std::move(value));
        }
        for(unsigned i=0;i<10000;++i)arena.make(std::to_string(i),words);
        for(const auto& [key,value]:saved) {
            const char* bytes=reinterpret_cast<const char*>(key)+sizeof(NameKey)+words*sizeof(std::atomic<uint64_t>);
            assert(std::string_view(bytes,key->length)==value);
        }
        bool threw=false;try{arena.make("x",SIZE_MAX);}catch(const std::runtime_error&){threw=true;}assert(threw);
    }
    for(size_t countries : {1U,64U,65U,241U,300U,17576U}) {
        Names names(128,countries);StringArena arena;std::vector<Names::Entry*> entries;
        for(unsigned i=0;i<60;++i){std::string key=i ? "collision/"+std::to_string(i):"";auto& entry=names.intern(key,arena,42);entries.push_back(&entry);assert(names.bytes(entry.key)==key);assert(names.first(entry,countries-1));assert(!names.first(entry,countries-1));}
        for(unsigned i=0;i<60;++i){std::string key=i ? "collision/"+std::to_string(i):"";assert(&names.intern(key,arena,42)==entries[i]);}
        assert(names.used.load()==60);
    }
    constexpr unsigned workers=4,updates=10000,key_count=1000,countries=300;
    Names names(2048,countries);std::array<StringArena,workers> arenas;
    std::vector<std::string> keys;for(unsigned i=0;i<key_count;++i)keys.push_back("name/"+std::to_string(i));
    keys[0]="";keys[1]=std::string("a\0b",3);keys[2]="UTF-8 \xe5\x90\x8d";keys[3]=std::string(65537,'z');
    std::set<std::pair<unsigned,unsigned>> expected;
    for(unsigned w=0;w<workers;++w)for(unsigned i=0;i<updates;++i)expected.emplace((i*7+w*13)%key_count,(i*17+w*31)%countries);
    std::array<std::atomic<unsigned>,countries> counts{};std::vector<std::thread> threads;
    for(unsigned w=0;w<workers;++w)threads.emplace_back([&,w]{for(unsigned i=0;i<updates;++i){unsigned key=(i*7+w*13)%key_count,country=(i*17+w*31)%countries;uint64_t hash=key%10 ? Names::hash_key(keys[key]):42;auto& entry=names.intern(keys[key],arenas[w],hash);if(names.first(entry,country))counts[country].fetch_add(1,std::memory_order_relaxed);}});
    for(auto& thread:threads)thread.join();std::array<unsigned,countries> reference{};for(auto [key,country]:expected)++reference[country];
    for(unsigned c=0;c<countries;++c)assert(counts[c].load()==reference[c]);assert(names.used.load()==key_count);
    std::cout<<"PASS stable name blocks, large/empty/NUL/UTF-8 keys, deliberate collisions, country-word boundaries, parallel std::set model\n";
}
