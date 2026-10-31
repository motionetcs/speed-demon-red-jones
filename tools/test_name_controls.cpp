#ifndef NAMES_HEADER
#error Select the grouped Names header with NAMES_HEADER
#endif
#include NAMES_HEADER
#include <cassert>
#include <iostream>
#include <random>

void check(uint64_t word, uint8_t tag) {
    bool busy=false; uint64_t empty=0, exact=0;
    for(unsigned i=0;i<8;++i){auto byte=uint8_t(word>>(i*8));busy|=byte==1;if(byte==0)empty|=uint64_t(128)<<(i*8);if(byte==tag)exact|=uint64_t(128)<<(i*8);}
    assert(bool(Names::matches(word,1))==busy);
    if(busy)return;
    assert(Names::matches(word,0)==empty);
    uint64_t candidates=Names::matches(word,tag);assert((candidates&exact)==exact);
    while(candidates){unsigned i=std::countr_zero(candidates)/8;assert(uint8_t(word>>(i*8))>=2);candidates&=candidates-1;}
}
int main(){
    std::mt19937_64 rng(0x4ca700);
    for(unsigned i=0;i<200000;++i)check(rng(),uint8_t(rng())|2);
    for(unsigned tag=2;tag<256;++tag)if(tag&2)for(unsigned position=0;position<8;++position)for(unsigned adjacent : {0U,1U,tag^1,tag,255U}){
        uint64_t word=uint64_t(tag)*Names::ones;unsigned j=(position+1)%8;word=(word&~(uint64_t(255)<<(j*8)))|(uint64_t(adjacent)<<(j*8));check(word,tag);
    }
    Names names(64,241); names.words=SIZE_MAX; StringArena arena;bool failed=false;
    try{names.intern("x",arena,42);}catch(const std::runtime_error&){failed=true;}
    assert(failed&&names.canceled.load());for(size_t i=0;i<8;++i)assert(!Names::matches(names.controls[i].load(),1));
    std::cout<<"PASS packed control-word reference, reserved states, candidate publication and allocation-failure release\n";
}
