#pragma once
#include <bit>
#include <cstdint>
#include <cstring>
inline const char* find_space(const char* p,const char* end){
    if constexpr(std::endian::native==std::endian::little){
        while(end-p>=8){
            uint64_t bytes;std::memcpy(&bytes,p,8);bytes^=0x2020202020202020ULL;
            uint64_t mask=(bytes-0x0101010101010101ULL)&~bytes&0x8080808080808080ULL;
            if(mask)return p+std::countr_zero(mask)/8;
            p+=8;
        }
    }
    return static_cast<const char*>(std::memchr(p,' ',end-p));
}
