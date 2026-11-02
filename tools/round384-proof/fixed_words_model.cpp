#include "source/track-c/names.hpp"
#include "../../tools/offset_names_model.hpp"
#include <array>
#include <thread>

struct SelectedNames:Names {
    using Names::Names;
    uint32_t make(std::string_view key){return words==4?Names::make<4>(key):Names::make<0>(key);}
    std::string_view bytes(uint32_t index)const{return words==4?Names::bytes<4>(index):Names::bytes<0>(index);}
    bool first(std::string_view key,size_t country,uint64_t hash){return words==4?Names::first<4>(key,country,hash):Names::first<0>(key,country,hash);}
};
void fixed_words_case(size_t countries) {
    assert((countries+63)/64==4);
    Names fixed(countries),generic(countries);
    std::set<std::pair<std::string,size_t>> reference;
    for(unsigned pass=0;pass<4;++pass)for(unsigned i=0;i<700;++i){
        std::string key="full-collision/"+std::to_string(i);
        size_t country=(i+pass/2)%countries;
        uint64_t hash=(uint64_t(i+1)<<32)|uint32_t(pass<2?0:UINT32_MAX);
        // A key has a stable hash within each independent subtable below.
        if(pass>=2)key+="/max";
        bool expected=reference.emplace(key,country).second;
        assert(fixed.first<4>(key,country,hash)==expected);
        assert(generic.first<0>(key,country,hash)==expected);
    }
    for(unsigned i=0;i<60000;++i){
        std::string key="grow-four/"+std::to_string(i);size_t country=i%countries;
        uint64_t hash=Names::hash_key(key);
        assert(fixed.first<4>(key,country,hash));assert(generic.first<0>(key,country,hash));
        assert(!fixed.first<4>(key,country,hash));assert(!generic.first<0>(key,country,hash));
    }
    assert(fixed.used==generic.used&&fixed.entries.size()>16384&&fixed.storage.size()>1);
    assert(fixed.next==generic.next&&fixed.remaining==generic.remaining&&fixed.storage.size()==generic.storage.size());
    for(size_t length:{0U,1U,7U,8U,63U,64U,65495U,65496U,65497U,65535U,65536U,1048576U}){
        std::string key(length,'x');for(size_t i=0;i<length;++i)key[i]=char(i%251);
        uint64_t hash=Names::hash_key(key);
        for(size_t country=0;country<countries;++country){
            assert(fixed.first<4>(key,country,hash));assert(generic.first<0>(key,country,hash));
            assert(!fixed.first<4>(key,country,hash));assert(!generic.first<0>(key,country,hash));
        }
    }
    // Exact full arena block, next-block rollover and all four zeroed words.
    Names arena(countries);std::string full((8192-5)*8,'z');auto first=arena.make<4>(full);
    assert(first==1&&arena.next==8192&&arena.remaining==0&&arena.bytes<4>(first)==full);
    for(unsigned i=1;i<=4;++i)assert(arena.at(first)[i]==0);
    auto second=arena.make<4>("");assert(second==8193&&arena.bytes<4>(second).empty());
    arena.at(first)[4]=UINT64_MAX;
    for(unsigned i=0;i<20000;++i)arena.make<4>("roll/"+std::to_string(i));
    assert(arena.bytes<4>(first)==full&&arena.at(first)[4]==UINT64_MAX);
}
int main(){
    run_offset_name_model<SelectedNames>();
    for(size_t countries:{193U,241U,256U})fixed_words_case(countries);
    for(size_t countries:{1U,63U,64U,65U,192U,193U,241U,256U,257U,17577U}){
        SelectedNames table(countries);std::set<std::pair<std::string,size_t>> reference;
        for(size_t c=0;c<countries;++c){std::string key="each/\"\"/UTF-8 \xe5\x90\x8d";assert(table.first(key,c,42)==reference.emplace(key,c).second);assert(!table.first(key,c,42));}
    }
    std::array<std::thread,4> workers;
    for(unsigned owner=0;owner<workers.size();++owner)workers[owner]=std::thread([owner]{
        Names table(241);std::set<std::pair<std::string,size_t>> reference;
        for(unsigned pass=0;pass<3;++pass)for(unsigned i=0;i<20000;++i){std::string key="private/"+std::to_string(owner)+"/"+std::to_string(i);size_t c=(i+pass/2)%241;uint64_t h=Names::hash_key(key);assert(table.first<4>(key,c,h)==reference.emplace(key,c).second);}
    });
    for(auto& thread:workers)thread.join();
    std::cout<<"PASS384 exact changed-header FixedWords4/generic0/selected dispatch: independent set, full-key/low32 zero/MAX collisions, 193/241/256 growth, all country words and192/193/256/257 seams, exact/oversized/1MiB arena blocks, stable indices, four private owners; original generic all-boundary/overflow model also executed\n";
}
