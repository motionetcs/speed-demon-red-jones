
#pragma once
#include "quote_scan.hpp"
#include <algorithm>
#include <array>
#include <cstddef>
#include <stdexcept>
struct RawCsvField { const char* first; const char* last; size_t quotes; };
// Streaming CSV structural masks. Complete in-range blocks only. Every quote
// toggles parity; a doubled CSV quote therefore toggles it twice.
struct RecordScanner {
    const char* cursor; const char* end; const char* begin; const char* block; const char* next;
    uint64_t quotes=0,separators=0; bool inside=false,terminated=false;
    RecordScanner(const char* p,const char* e):cursor(p),end(e),begin(p),block(p),next(p){}
#if defined(__aarch64__) && defined(__ARM_NEON) && !defined(RECORD_SCAN_SCALAR)
    static uint32_t bits(uint8x16_t equal){
        const uint8x8_t weights={1,2,4,8,16,32,64,128};
        auto v=vandq_u8(equal,vcombine_u8(weights,weights));
        return uint32_t(vaddv_u8(vget_low_u8(v)))|(uint32_t(vaddv_u8(vget_high_u8(v)))<<8);
    }
#endif
    static uint64_t prefix_xor(uint64_t value){
#if defined(__PCLMUL__) && !defined(RECORD_SCAN_SCALAR)
        auto product=_mm_clmulepi64_si128(_mm_set_epi64x(0,static_cast<int64_t>(value)),_mm_set1_epi8(-1),0);
        return static_cast<uint64_t>(_mm_cvtsi128_si64(product));
#else
        value^=value<<1;value^=value<<2;value^=value<<4;value^=value<<8;value^=value<<16;value^=value<<32;return value;
#endif
    }
    bool load(){
        if(next==end)return false;
        block=next;unsigned width=unsigned(std::min<ptrdiff_t>(64,end-next));
        uint64_t comma=0,line=0;quotes=0;unsigned i=0;
#if defined(__AVX2__) && !defined(RECORD_SCAN_SCALAR)
        for(;i+32<=width;i+=32){
            auto v=_mm256_loadu_si256(reinterpret_cast<const __m256i*>(next+i));
            quotes|=uint64_t(uint32_t(_mm256_movemask_epi8(_mm256_cmpeq_epi8(v,_mm256_set1_epi8('"')))))<<i;
            comma|=uint64_t(uint32_t(_mm256_movemask_epi8(_mm256_cmpeq_epi8(v,_mm256_set1_epi8(',')))))<<i;
            line|=uint64_t(uint32_t(_mm256_movemask_epi8(_mm256_cmpeq_epi8(v,_mm256_set1_epi8('\n')))))<<i;
        }
#endif
#if defined(__SSE2__) && !defined(RECORD_SCAN_SCALAR)
        for(;i+16<=width;i+=16){
            auto v=_mm_loadu_si128(reinterpret_cast<const __m128i*>(next+i));
            quotes|=uint64_t(uint32_t(_mm_movemask_epi8(_mm_cmpeq_epi8(v,_mm_set1_epi8('"')))))<<i;
            comma|=uint64_t(uint32_t(_mm_movemask_epi8(_mm_cmpeq_epi8(v,_mm_set1_epi8(',')))))<<i;
            line|=uint64_t(uint32_t(_mm_movemask_epi8(_mm_cmpeq_epi8(v,_mm_set1_epi8('\n')))))<<i;
        }
#elif defined(__aarch64__) && defined(__ARM_NEON) && !defined(RECORD_SCAN_SCALAR)
        for(;i+16<=width;i+=16){
            auto v=vld1q_u8(reinterpret_cast<const uint8_t*>(next+i));
            quotes|=uint64_t(bits(vceqq_u8(v,vdupq_n_u8('"'))))<<i;
            comma|=uint64_t(bits(vceqq_u8(v,vdupq_n_u8(','))))<<i;
            line|=uint64_t(bits(vceqq_u8(v,vdupq_n_u8('\n'))))<<i;
        }
#endif
        for(;i<width;++i){quotes|=uint64_t(next[i]=='"')<<i;comma|=uint64_t(next[i]==',')<<i;line|=uint64_t(next[i]=='\n')<<i;}
        uint64_t prefix=prefix_xor(quotes)^(uint64_t(0)-uint64_t(inside));
        bool previous=block==begin||block[-1]=='"'||block[-1]==','||block[-1]=='\n';
        const char* following=next+width;bool after=following==end||*following=='"'||*following==','||*following=='\n'||*following=='\r';
        uint64_t before_allowed=((quotes|comma|line)<<1)|uint64_t(previous);
        uint64_t after_allowed=((quotes|comma|line)>>1)|(uint64_t(after)<<(width-1));
        if((quotes&prefix&~before_allowed)||(quotes&~prefix&~after_allowed))throw std::runtime_error("invalid CSV quote placement");
        inside^=(std::popcount(quotes)&1)!=0;separators=(comma|line)&~prefix;next+=width;return true;
    }
    const char* separator(size_t& count){
        for(;;){
            if(separators){
                unsigned i=std::countr_zero(separators);uint64_t through=i==63?UINT64_MAX:(uint64_t(1)<<(i+1))-1;
                count+=std::popcount(quotes&through);quotes&=~through;separators&=separators-1;return block+i;
            }
            count+=std::popcount(quotes);quotes=0;
            if(!load()){if(inside)throw std::runtime_error("unterminated CSV quotes");return end;}
        }
    }
    bool record(std::array<RawCsvField,5>& fields){
        if(cursor==end)return false;
        for(unsigned f=0;f<5;++f){
            size_t count=0;const char* stop=separator(count);fields[f]={cursor,stop,count};
            if(f<4){if(stop==end||*stop!=',')throw std::runtime_error("missing CSV field");cursor=stop+1;}
            else{if(stop!=end&&*stop!='\n')throw std::runtime_error("extra CSV field");terminated=stop!=end;cursor=stop==end?end:stop+1;}
        }
        return true;
    }
};
