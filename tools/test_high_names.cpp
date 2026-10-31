#include NAMES_HEADER
#include "offset_names_model.hpp"
int main(){
    run_offset_name_model<Names>();
    for(uint32_t high:{0U,1U,2U,42U,0xdeadbeefU,UINT32_MAX}){
        Names names(257);std::set<std::pair<std::string,size_t>> expected;
        for(unsigned pass=0;pass<3;++pass)for(unsigned i=0;i<900;++i){
            std::string key="upper-collision/"+std::to_string(i);uint64_t hash=(uint64_t(high)<<32)|(i*16+(i%4));size_t country=(i+pass/2)%257;
            bool fresh=expected.emplace(key,country).second;assert(names.first(key,country,hash)==fresh);
        }
        assert(names.used==900);for(const auto& e:names.entries)if(e.index)assert(e.hash==high);
    }
    std::cout<<"PASS exact upper32 placement including0/1, colliding upper/different lower hashes, all low-bit owners and full-key country membership\n";
}
