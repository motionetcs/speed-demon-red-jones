#include NAMES_HEADER
#include <cassert>
#include <iostream>
#include <random>
#include <set>
#include <string>
#include <unordered_map>
unsigned route(uint64_t hash,unsigned owners){
    unsigned owner=hash%owners;
    return owner;
}
std::string key(unsigned n){std::string s="Routing ";for(unsigned i=0;i<10;++i){s.push_back(char('a'+n%26));n/=26;}return s;}
uint64_t injected(unsigned n){
    constexpr uint32_t low[]={0,1,2,42,0xdeadbeefU,UINT32_MAX};
    constexpr uint32_t high[]={0,1,2,3,4,7,8,0x80000000U,UINT32_MAX};
    return (uint64_t(high[n%9])<<32)|low[(n/9)%6];
}
void run_route_model(){
    uint64_t checks=0;std::mt19937_64 rng(0x274a11);
    for(unsigned owners=1;owners<=11;++owners){
        for(unsigned i=0;i<100000;++i){uint64_t h=rng();assert(route(h,owners)==h-(h/owners)*owners);++checks;}
        for(size_t countries:{1U,65U,257U,17577U}){
            std::vector<Names> shards;shards.reserve(owners);for(unsigned o=0;o<owners;++o)shards.emplace_back(countries);
            std::set<std::pair<size_t,std::string>> expected;
            for(unsigned pass=0;pass<2;++pass)for(unsigned j=0;j<192;++j){
                unsigned n=pass?191-j:j;auto text=key(n);uint64_t h=injected(n);
                for(size_t country:{0U,1U,63U,64U,65U,254U,255U,256U,257U,17576U}){
                    if(country>=countries)continue;
                    bool fresh=expected.emplace(country,text).second;
                    assert(shards[route(h,owners)].first(text,country,h)==fresh);++checks;
                }
            }
            size_t total=0;for(auto& names:shards)total+=names.used;assert(total==192);
        }
    }
    // Low two bits fixed zero force the unchanged modulo4 owner; remaining fingerprint bits vary.
    {Names names(257);for(unsigned i=0;i<50000;++i){auto text=key(i+1000000);uint64_t h=Names::hash_key(text)&~uint64_t(3);assert(route(h,4)==0);assert(names.first(text,i%257,h));++checks;}
     for(unsigned i=0;i<50000;++i){auto text=key(i+1000000);uint64_t h=Names::hash_key(text)&~uint64_t(3);assert(!names.first(text,i%257,h));++checks;}assert(names.used==50000&&names.entries.size()>4096);}
    // Genuine low32 collision sharing unchanged modulo4 owner, through production std::hash.
    std::unordered_map<uint64_t,std::pair<std::string,uint64_t>> seen;seen.reserve(300000);
    std::string left,right;uint64_t lh=0,rh=0;size_t searched=0;
    for(unsigned i=0;i<1000000&&left.empty();++i){auto text=key(i+2000000);uint64_t h=Names::hash_key(text);uint64_t signature=uint32_t(h)|(uint64_t(route(h,4))<<32);auto [it,added]=seen.emplace(signature,std::make_pair(text,h));if(!added&&it->second.first!=text){left=it->second.first;right=text;lh=it->second.second;rh=h;}searched=i+1;}
    assert(!left.empty()&&left!=right&&uint32_t(lh)==uint32_t(rh)&&route(lh,4)==route(rh,4));
    for(unsigned owners=1;owners<=11;++owners)for(size_t countries:{1U,65U,257U,17577U}){
        std::vector<Names> shards;shards.reserve(owners);for(unsigned o=0;o<owners;++o)shards.emplace_back(countries);
        for(size_t c:{0U,63U,64U,65U,255U,256U,17576U}){if(c>=countries)continue;assert(shards[route(lh,owners)].first(left,c,lh));assert(shards[route(rh,owners)].first(right,c,rh));assert(!shards[route(lh,owners)].first(left,c,lh));assert(!shards[route(rh,owners)].first(right,c,rh));checks+=4;}
    }
    std::cout<<"PASS route membership "<<checks<<" checks\n";
    std::cout<<"COLLISION\t"<<left<<'\t'<<right<<'\t'<<lh<<'\t'<<rh<<'\t'<<uint32_t(lh)<<'\t'<<route(lh,4)<<'\t'<<searched<<'\n';
}
