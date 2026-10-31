#pragma once
#include <bit>
#include <cstdint>
#if defined(__AVX2__)
#include <immintrin.h>
#elif defined(__SSE2__)
#include <emmintrin.h>
#elif defined(__aarch64__)
#include <arm_neon.h>
#endif

// Return the first comma/CR/LF, reading only complete bounded vectors.
inline const char* csv_text_end(const char* p,const char* end) {
#if defined(__AVX2__)
    while(end-p>=32) {
        auto bytes=_mm256_loadu_si256(reinterpret_cast<const __m256i*>(p));
        auto special=_mm256_or_si256(_mm256_cmpeq_epi8(bytes,_mm256_set1_epi8(',')),_mm256_or_si256(_mm256_cmpeq_epi8(bytes,_mm256_set1_epi8('\r')),_mm256_cmpeq_epi8(bytes,_mm256_set1_epi8('\n'))));
        uint32_t mask=static_cast<uint32_t>(_mm256_movemask_epi8(special));
        if(mask)return p+std::countr_zero(mask);p+=32;
    }
#elif defined(__SSE2__)
    while(end-p>=16) {
        auto bytes=_mm_loadu_si128(reinterpret_cast<const __m128i*>(p));
        auto special=_mm_or_si128(_mm_cmpeq_epi8(bytes,_mm_set1_epi8(',')),_mm_or_si128(_mm_cmpeq_epi8(bytes,_mm_set1_epi8('\r')),_mm_cmpeq_epi8(bytes,_mm_set1_epi8('\n'))));
        unsigned mask=static_cast<unsigned>(_mm_movemask_epi8(special));
        if(mask)return p+std::countr_zero(mask);p+=16;
    }
#elif defined(__aarch64__)
    if constexpr(std::endian::native==std::endian::little) {
        while(end-p>=16) {
            auto bytes=vld1q_u8(reinterpret_cast<const uint8_t*>(p));
            auto special=vorrq_u8(vceqq_u8(bytes,vdupq_n_u8(',')),vorrq_u8(vceqq_u8(bytes,vdupq_n_u8('\r')),vceqq_u8(bytes,vdupq_n_u8('\n'))));
            // Each byte pair becomes two four-bit flags in one packed byte.
            uint64_t mask=vget_lane_u64(vreinterpret_u64_u8(vshrn_n_u16(vreinterpretq_u16_u8(special),4)),0);
            if(mask)return p+std::countr_zero(mask)/4;p+=16;
        }
    }
#endif
    while(p<end && *p!=',' && *p!='\r' && *p!='\n')++p;
    return p;
}
