#ifndef NAMES_HEADER
#error Explicit NAMES_HEADER required
#endif
#include NAMES_HEADER
#include <cassert>
#include <iostream>
#include <random>
#include <string>
#include <unordered_map>

// Find a genuine collision through the production hash, without injected hashes.
int main(){
    static_assert(NAME_HASH_CRC == 1);
    std::mt19937_64 random(0x193cc012);
    std::unordered_map<uint64_t,std::string> seen;
    std::string left,right;uint64_t collision_hash=0;
    for(size_t i=0;i<1000000&&left.empty();++i){
        uint64_t value=random();std::string key="collision ";
        for(unsigned digit=0;digit<16;++digit)key.push_back(char('a'+((value>>(digit*4))&15)));
        uint64_t hash=Names::hash_key(key);
        auto [entry,added]=seen.emplace(hash,key);
        if(!added&&entry->second!=key){left=entry->second;right=key;collision_hash=hash;}
    }
    assert(!left.empty()&&left!=right&&Names::hash_key(left)==Names::hash_key(right));
    for(size_t countries:{1U,64U,65U,257U,17577U}){
        Names names(countries);
        for(size_t country=0;country<countries;++country){
            assert(names.first(left,country,Names::hash_key(left)));
            assert(names.first(right,country,Names::hash_key(right)));
            assert(!names.first(left,country,Names::hash_key(left)));
            assert(!names.first(right,country,Names::hash_key(right)));
        }
        assert(names.used==2);
    }
    std::cout<<"PASS genuine CRC full-hash collision, exact distinct keys/countries and repeated membership\n";
    std::cout<<"COLLISION\t"<<left<<'\t'<<right<<'\t'<<collision_hash<<'\n';
}
