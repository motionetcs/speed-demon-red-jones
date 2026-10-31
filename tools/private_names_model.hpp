#pragma once
#include <cassert>
#include <iostream>
#include <random>
#include <set>
#include <string>
#include <utility>
#include <vector>

template<class Table> void run_private_name_model(){
    std::mt19937 random(0x7a61b23);
    for(size_t countries:{1U,64U,65U,241U,257U,17577U}){
        Table names(countries);std::set<std::pair<std::string,size_t>> reference;
        std::vector<std::string> keys{"",std::string("a\0b",3),"UTF-8 \xe5\x90\x8d","trailing ","a\"\"b"};
        for(unsigned i=0;i<350;++i)keys.push_back("collision/"+std::to_string(i));
        for(unsigned i=0;i<18000;++i){size_t k=random()%keys.size(),country=random()%countries;bool expected=reference.emplace(keys[k],country).second;assert(names.first(keys[k],country,42)==expected);}
        for(auto& [key,country]:reference)assert(!names.first(key,country,42));
        assert(names.used==keys.size());
    }
    Table growing(257);std::vector<std::string> keys;
    for(unsigned i=0;i<60000;++i){keys.push_back("growth/"+std::to_string(i));auto& key=keys.back();assert(growing.first(key,i%257,Table::hash_key(key)));}
    assert(growing.used==60000&&growing.entries.size()>16384);
    for(unsigned i=0;i<keys.size();++i){auto& key=keys[i];assert(!growing.first(key,i%257,Table::hash_key(key)));assert(growing.first(key,(i+1)%257,Table::hash_key(key)));}
    // Routing to four owners fixes the low two hash bits. Exercise every
    // owner across table growth; full keys still decide colliding entries.
    for(uint64_t owner=0;owner<4;++owner){
        Table routed(257);
        for(unsigned pass=0;pass<2;++pass)for(unsigned i=0;i<30000;++i){
            std::string key="routed/"+std::to_string(i);
            uint64_t hash=((Table::hash_key(key)|4)&~uint64_t(3))|owner;
            assert(routed.first(key,i%257,hash)==(pass==0));
        }
        assert(routed.used==30000&&routed.entries.size()>16384);
    }
    for(size_t length:{0U,1U,7U,8U,63U,64U,65535U,65536U,65537U,1048576U}){
        std::string key(length,'x');for(size_t i=0;i<length;++i)key[i]=char(i%251);uint64_t hash=Table::hash_key(key);
        assert(growing.first(key,256,hash));assert(!growing.first(key,256,hash));
        for(unsigned i=0;i<257;++i)growing.first(key,i,hash);
        for(unsigned i=0;i<257;++i)assert(!growing.first(key,i,hash));
    }
    StringArena arena;bool threw=false;try{arena.make("x",SIZE_MAX);}catch(const std::runtime_error&){threw=true;}assert(threw);
    std::cout<<"PASS private exact-name std::set/collision/country/growth/stable-block/long-NUL-UTF8-key models\n";
}
