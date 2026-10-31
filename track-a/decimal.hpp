#pragma once
#include <bit>
#include <cstdint>
#include <cstring>

// Four ASCII digits in one bounded load. Every byte is validated before batching.
inline uint64_t decimal_digits(const char*& p, const char* end) {
    uint64_t value = 0;
    if constexpr (std::endian::native == std::endian::little) {
        while (end - p >= 4) {
            uint32_t bytes;
            std::memcpy(&bytes, p, 4);
            uint32_t digits = bytes ^ 0x30303030U;
            if ((digits & 0xf0f0f0f0U) || ((digits + 0x06060606U) & 0x10101010U)) break;
            uint32_t pairs = (digits & 0x00ff00ffU) * 10 + ((digits >> 8) & 0x00ff00ffU);
            value = value * 10000 + (pairs & 0xffffU) * 100 + (pairs >> 16);
            p += 4;
        }
    }
    while (p < end && *p >= '0' && *p <= '9') value = value * 10 + *p++ - '0';
    return value;
}
