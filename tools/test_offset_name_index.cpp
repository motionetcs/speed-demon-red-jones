#ifndef NAMES_HEADER
#define NAMES_HEADER "../track-c/names.hpp"
#endif
#include NAMES_HEADER
#include <cassert>
#include <iostream>
#include <set>

int main(){
    for(uint32_t base:{0U,4U,65532U,UINT32_MAX-3}){
        Names table(257);std::set<std::pair<std::string,size_t>> reference;
        for(unsigned pass=0;pass<4;++pass)for(unsigned i=0;i<2048;++i){
            std::string key="mixed-low-bits/"+std::to_string(i);
            uint32_t low=base+(i&3U);uint64_t hash=(uint64_t(i+1)<<32)|low;
            size_t country=(i+pass/2)%257;
            assert(table.first(key,country,hash)==reference.emplace(key,country).second);
        }
        assert(table.used==2048);
    }
    for(unsigned owners=1;owners<=11;++owners){
        std::vector<std::unique_ptr<Names>> tables;
        std::vector<std::set<std::pair<std::string,size_t>>> references(owners);
        for(unsigned i=0;i<owners;++i)tables.push_back(std::make_unique<Names>(257));
        for(unsigned pass=0;pass<3;++pass)for(unsigned i=0;i<owners*18000;++i){
            std::string key="arbitrary-routing/"+std::to_string(i);
            uint64_t hash=Names::hash_key(key);unsigned owner=hash%owners;
            size_t country=(i+pass/2)%257;
            assert(tables[owner]->first(key,country,hash)==references[owner].emplace(key,country).second);
        }
        for(const auto& table:tables)assert(table->entries.size()>16384);
    }
    std::cout<<"PASS independent std::set: mixed low2 fingerprints with same shifted home, zero/MAX32 homes and wrap probes, distinct full64 hashes, every1..11 owner routing with table growth and repeated exact country updates\n";
}
