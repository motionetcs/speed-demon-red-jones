#ifndef QUOTE_SCAN_HEADER
#define QUOTE_SCAN_HEADER "../track-c/quote_scan.hpp"
#endif
#include QUOTE_SCAN_HEADER
#include <cassert>
#include <iostream>
#include <random>
#include <string>
#include <sys/mman.h>
#include <unistd.h>

const char* reference(const char* p, const char* end) {
    while (p < end && *p != '"') ++p;
    return p == end ? nullptr : p;
}
int main() {
    size_t page = static_cast<size_t>(sysconf(_SC_PAGESIZE));
    char* memory = static_cast<char*>(mmap(nullptr, page * 3, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANON, -1, 0));
    assert(memory != MAP_FAILED && mprotect(memory, page, PROT_NONE) == 0);
    assert(mprotect(memory + page * 2, page, PROT_NONE) == 0);
    char* usable = memory + page;
    auto check = [&](const std::string& value) {
        assert(value.size() <= page);
        for (bool at_head : {false, true}) {
            char* start = at_head ? usable : usable + page - value.size();
            if (!value.empty()) std::memcpy(start, value.data(), value.size());
            assert(find_quote(start, start + value.size()) == reference(start, start + value.size()));
        }
    };
    for (size_t length = 0; length <= 256; ++length) {
        std::string value(length, 'x'); check(value);
        for (size_t at = 0; at < length; ++at) { value[at] = '"'; check(value); value[at] = 'x'; }
    }
    for (size_t at = 0; at < 96; ++at) for (unsigned byte = 0; byte < 256; ++byte) {
        std::string value(97, 'x'); value[at] = char(byte); check(value);
    }
    for (unsigned mask = 0; mask < 65536; ++mask) {
        std::string value(64, 'x');
        for (unsigned i = 0; i < 16; ++i) if (mask & (1U << i)) value[i] = '"';
        value[31] = value[63] = '"'; check(value);
    }
    for (size_t offset = 0; offset < 64; ++offset) for (size_t length = 0; length < 128; ++length) {
        std::memset(usable, '"', page);
        char* start = usable + offset;
        std::memset(start, 'x', length);
        assert(find_quote(start, start + length) == nullptr); // Quotes beyond the logical end do not count.
        if (length) {
            start[length - 1] = '"'; assert(find_quote(start, start + length) == start + length - 1);
            start[0] = '"'; assert(find_quote(start, start + length) == start);
        }
    }
    std::mt19937 random(0x9017);
    for (unsigned trial = 0; trial < 100000; ++trial) {
        std::string value(random() % 1025, ' ');
        for (char& byte : value) byte = char(random() % 256);
        check(value);
    }
    std::string long_value(1U << 20, 'x');
    assert(find_quote(long_value.data(), long_value.data() + long_value.size()) == nullptr);
    for (size_t at : {size_t(0), size_t(31), size_t(32), size_t(63), size_t(64), long_value.size() - 1}) {
        long_value[at] = '"';
        assert(find_quote(long_value.data(), long_value.data() + long_value.size()) == long_value.data() + at);
        long_value[at] = 'x';
    }
    munmap(memory, page * 3);
#if defined(__AVX2__)
    const char* path = "AVX2";
#elif defined(__SSE2__)
    const char* path = "SSE2";
#elif defined(__ARM_NEON)
    const char* path = "NEON";
#else
    const char* path = "scalar";
#endif
    std::cout << "PASS independent first-quote reference, all bytes/offsets,16-bit masks, random/1MiB/logical-tail and both protected-page boundaries; compiled=" << path << "\n";
}
