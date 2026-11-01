#pragma once
#include <cstdint>
#include <cstring>
#include <functional>
#include <string_view>
#if __BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__ && defined(__x86_64__) && defined(__SSE4_2__)
#include <immintrin.h>
#define NAME_HASH_CRC 1
inline uint32_t name_crc64(uint32_t state,uint64_t word){return static_cast<uint32_t>(_mm_crc32_u64(state,word));}
inline uint32_t name_crc32(uint32_t state,uint32_t word){return _mm_crc32_u32(state,word);}
inline uint32_t name_crc16(uint32_t state,uint16_t word){return _mm_crc32_u16(state,word);}
inline uint32_t name_crc8(uint32_t state,uint8_t word){return _mm_crc32_u8(state,word);}
#else
#define NAME_HASH_CRC 0
#endif
inline uint64_t whole_name_hash(std::string_view key){
#if NAME_HASH_CRC
    uint32_t state=static_cast<uint32_t>(key.size())^0x9e3779b9U;
    const char* p=key.data();size_t n=key.size();
    while(n>=8){uint64_t word;std::memcpy(&word,p,8);state=name_crc64(state,word);p+=8;n-=8;}
    if(n>=4){uint32_t word;std::memcpy(&word,p,4);state=name_crc32(state,word);p+=4;n-=4;}
    if(n>=2){uint16_t word;std::memcpy(&word,p,2);state=name_crc16(state,word);p+=2;n-=2;}
    if(n)state=name_crc8(state,static_cast<uint8_t>(*p));
    uint64_t hash=uint64_t(state)*0x9e3779b97f4a7c15ULL;
#else
    uint64_t hash=std::hash<std::string_view>{}(key);
#endif
    return hash<2?hash+2:hash;
}
