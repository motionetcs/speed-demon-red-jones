#pragma once
#include <cassert>
#include <cstdint>
#include <iostream>
#include <random>
#include <set>
#include <string>
#include <utility>
#include <vector>

template<class Table> void run_offset_name_model(){
    static_assert(sizeof(typename Table::Entry)==8);
    for(size_t block:{size_t(0),size_t(1),size_t(127),(size_t(1)<<19)-1})for(size_t word=0;word<8192;++word){
        uint64_t encoded=(uint64_t(block)<<13)|word;
        if(encoded==UINT32_MAX)continue;
        auto index=Table::encode_index(block,word);assert(index==encoded+1);
        assert(((index-1)>>13)==block&&((index-1)&8191)==word);
    }
    for(auto pair:std::vector<std::pair<size_t,size_t>>{{size_t(1)<<19,0},{0,8192},{(size_t(1)<<19)-1,8191},{SIZE_MAX,SIZE_MAX}}){
        bool threw=false;try{Table::encode_index(pair.first,pair.second);}catch(const std::runtime_error&){threw=true;}assert(threw);
    }
    std::mt19937_64 random(0x127c0fa);
    for(size_t countries:{1U,64U,65U,241U,257U,17577U}){
        Table names(countries);std::set<std::pair<std::string,size_t>> reference;
        std::vector<std::string> keys{"",std::string("a\0b",3),"UTF-8 \xe5\x90\x8d","trailing ","a\"\"b"};
        for(unsigned i=0;i<350;++i)keys.push_back("collision/"+std::to_string(i));
        for(unsigned i=0;i<18000;++i){size_t k=random()%keys.size(),country=random()%countries;bool expected=reference.emplace(keys[k],country).second;assert(names.first(keys[k],country,42)==expected);}
        for(const auto& value:reference)assert(!names.first(value.first,value.second,42));
        for(size_t country=0;country<countries;++country){std::string key="every-country";bool expected=reference.emplace(key,country).second;assert(names.first(key,country,42)==expected);assert(!names.first(key,country,42));}
    }
    for(uint32_t low:{0U,1U,2U,42U,0xdeadbeefU,UINT32_MAX}){
        Table names(257);std::set<std::pair<std::string,size_t>> reference;
        for(unsigned pass=0;pass<3;++pass)for(unsigned i=0;i<700;++i){
            std::string key="low32/"+std::to_string(i);uint64_t hash=(uint64_t(i+1)<<32)|low;size_t country=(i+pass/2)%257;
            bool expected=reference.emplace(key,country).second;assert(names.first(key,country,hash)==expected);
        }
    }
    Table growing(257);std::vector<std::string> keys;
    for(unsigned i=0;i<60000;++i){keys.push_back("growth/"+std::to_string(i));auto& key=keys.back();assert(growing.first(key,i%257,Table::hash_key(key)));}
    assert(growing.used==60000&&growing.entries.size()>16384&&growing.storage.size()>1);
    for(unsigned i=0;i<keys.size();++i){const auto& key=keys[i];assert(!growing.first(key,i%257,Table::hash_key(key)));assert(growing.first(key,(i+1)%257,Table::hash_key(key)));}
    for(uint64_t owner=0;owner<4;++owner){
        Table routed(257);
        for(unsigned pass=0;pass<2;++pass)for(unsigned i=0;i<30000;++i){std::string key="routed/"+std::to_string(i);uint64_t hash=(Table::hash_key(key)&~uint64_t(3))|owner;assert(routed.first(key,i%257,hash)==(pass==0));}
    }
    Table direct(64);std::string exact((8192-2)*8,'e');auto first=direct.make(exact);assert(first==1&&direct.next==8192&&direct.remaining==0);
    direct.at(first)[1]=0xfedcba9876543210ULL;auto second=direct.make("");assert(second==8193&&direct.bytes(first)==exact&&direct.bytes(second).empty());assert(direct.at(first)[1]==0xfedcba9876543210ULL);
    std::vector<std::pair<uint32_t,std::string>> saved{{first,exact},{second,""}};
    for(size_t length:{0U,1U,7U,8U,63U,64U,65519U,65520U,65521U,65535U,65536U,65537U,1048576U}){
        std::string key(length,'x');for(size_t i=0;i<length;++i)key[i]=char(i%251);
        uint32_t index=direct.make(key);assert(direct.bytes(index)==key&&direct.at(index)[0]==key.size()&&direct.at(index)[1]==0);saved.emplace_back(index,key);
        assert(growing.first(key,256,Table::hash_key(key)));assert(!growing.first(key,256,Table::hash_key(key)));
        for(size_t country=0;country<257;++country)growing.first(key,country,Table::hash_key(key));
        for(size_t country=0;country<257;++country)assert(!growing.first(key,country,Table::hash_key(key)));
    }
    for(unsigned i=0;i<30000;++i)direct.make("extra/"+std::to_string(i));
    for(const auto& value:saved)assert(direct.bytes(value.first)==value.second);
    assert(direct.at(first)[1]==0xfedcba9876543210ULL);
    Table overflow(1);overflow.words=SIZE_MAX;bool threw=false;try{overflow.make("x");}catch(const std::runtime_error&){threw=true;}assert(threw);
    std::cout<<"PASS offset-name independent std::set, low32 fingerprint collisions including0/1, full-key collisions, all-country words, table/block growth, exact full/partial/oversized blocks, long NUL/UTF8 keys, encoded-index boundaries and overflow guards\n";
}
