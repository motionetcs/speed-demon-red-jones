#include NAMES_HEADER
#include <array>
#include <cassert>
#include <iostream>
#include <map>
#include <random>
#include <set>

static size_t checks=0;
static void invariant(const Names& names) {
    assert(names.controls.size()==names.entries.size());size_t used=0;
    for(size_t at=0;at<names.entries.size();++at){
        const auto& e=names.entries[at];
        assert((names.controls[at]==128)==!e.index);
        if(!e.index)continue;
        ++used;assert(names.controls[at]==Names::tag(e.hash));
        size_t group=Names::home(e.hash,names.entries.size());
        while(group!=(at&~size_t(7))){
            for(unsigned lane=0;lane<8;++lane)assert(names.controls[group+lane]!=128);
            group=(group+8)&(names.entries.size()-1);
        }
    }
    assert(used==names.used);++checks;
}
int main(){
    std::mt19937_64 rng(0xc25961aa);
    for(unsigned t=0;t<128;++t)for(unsigned trial=0;trial<2048;++trial){
        std::array<uint8_t,8> flags;uint64_t expected=0,expected_empty=0;
        for(unsigned i=0;i<8;++i){flags[i]=rng()%5==0?128:uint8_t(rng()%128);if((trial+i)%11==0)flags[i]=uint8_t(t);}
        uint64_t word;std::memcpy(&word,flags.data(),8);
        for(unsigned i=0;i<8;++i){unsigned shift=(std::endian::native==std::endian::little?i:7-i)*8+7;if(flags[i]==t)expected|=uint64_t(1)<<shift;if(flags[i]==128)expected_empty|=uint64_t(1)<<shift;}
        uint64_t actual=Names::matches(word,uint8_t(t));assert((actual&expected)==expected);assert((word&Names::high)==expected_empty);
        while(actual){assert(flags[Names::lane(actual)]<128);actual&=actual-1;}
        ++checks;
    }
    for(size_t countries:{size_t(1),size_t(64),size_t(65),size_t(257),size_t(17576)}){
        Names names(countries);names.entries=std::vector<Names::Entry>(8);names.controls=std::vector<uint8_t>(8,128);
        std::vector<std::string> keys;keys.reserve(1100);
        for(unsigned i=0;i<1025;++i){std::string key="same-prefix/"+std::to_string(i);if(i%11==0)key.push_back('\0');if(i%13==0)key+="\xef\xbb\xbf\xc3\xa9";keys.push_back(key);}
        for(size_t length:{0U,1U,125U,65535U,65536U,1048576U})keys.emplace_back(length,'z');
        std::vector<uint64_t> hashes;
        for(unsigned i=0;i<keys.size();++i)hashes.push_back(i<311?uint64_t(0):i<620?(uint64_t(1)<<25):Names::hash_key(keys[i]));
        std::map<std::string,std::set<size_t>> reference;size_t capacity=names.entries.size();
        for(unsigned i=0;i<15000;++i){
            unsigned key=i<keys.size()?i:unsigned(rng()%keys.size());size_t country=rng()%countries;
            bool expected=reference[keys[key]].insert(country).second;
            assert(names.first(keys[key],country,hashes[key])==expected);++checks;
            if(capacity!=names.entries.size()){invariant(names);capacity=names.entries.size();}
        }
        invariant(names);assert(names.used==reference.size());
        for(size_t i=0;i<names.entries.size();++i)if(names.entries[i].index){
            auto value=names.bytes(names.entries[i].index);auto found=reference.find(std::string(value));assert(found!=reference.end());
            auto* data=names.at(names.entries[i].index);
            for(size_t country=0;country<countries;++country){assert(bool(data[1+country/64]&(uint64_t(1)<<(country%64)))==found->second.count(country));++checks;}
        }
    }
    // Exactly allocated metadata tail; no group lookup may read a ninth byte.
    for(size_t capacity:{8U,16U,32U,16384U}){
        std::vector<uint8_t> flags(capacity,128);assert(flags.capacity()==flags.size());
        for(unsigned lane=0;lane<8;++lane)flags[capacity-8+lane]=uint8_t(lane);
        auto word=Names::control_word(flags,capacity-8);assert(!(word&Names::high));
        for(unsigned t=0;t<8;++t){assert(Names::matches(word,uint8_t(t))!=0);++checks;}
    }
    std::cout<<"PASS "<<checks<<" independent group-mask superset/empty/lane, exact full-key/country, forced hash/tag collision, probe-stop/growth/count, UTF8/NUL/long arena and allocation-tail checks\n";
}
