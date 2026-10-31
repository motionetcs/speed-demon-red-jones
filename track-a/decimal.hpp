#pragma once
#include <bit>
#include <cstdint>
#include <cstring>

// Validate a bounded word, then decimal-reduce its leading digit bytes only.
inline uint64_t decimal_digits(const char*& p,const char* end) {
    uint64_t value=0;
    if constexpr(std::endian::native==std::endian::little) {
        if(end-p>=8){
            uint64_t bytes;std::memcpy(&bytes,p,8);
            uint64_t digits=bytes^0x3030303030303030ULL;
            uint64_t invalid=(digits&0xf0f0f0f0f0f0f0f0ULL)|((digits+0x0606060606060606ULL)&0x1010101010101010ULL);
            unsigned count=std::countr_zero(invalid)/8;
            if(count){
                digits<<=(8-count)*8;
                digits=(digits*10+(digits>>8))&0x00ff00ff00ff00ffULL;
                digits=(digits*100+(digits>>16))&0x0000ffff0000ffffULL;
                value=(digits*10000+(digits>>32))&0xffffffffULL;p+=count;
            }
        }
    }
    while(p<end&&*p>='0'&&*p<='9')value=value*10+*p++-'0';
    return value;
}
