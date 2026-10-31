#ifndef SPACE_SCAN_HEADER
#define SPACE_SCAN_HEADER "../track-a/space_scan.hpp"
#endif
#include SPACE_SCAN_HEADER
#include <cassert>
#include <iostream>
#include <random>
#include <string>
#include <sys/mman.h>
#include <unistd.h>

const char* reference(const char* p, const char* end) {
    while (p < end && *p != ' ') ++p;
    return p == end ? nullptr : p;
}
int main() {
    size_t page = static_cast<size_t>(sysconf(_SC_PAGESIZE));
    char* memory = static_cast<char*>(mmap(nullptr, page * 2, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANON, -1, 0));
    assert(memory != MAP_FAILED && mprotect(memory + page, page, PROT_NONE) == 0);
    auto check = [&](const std::string& value) {
        char* start = memory + page - value.size();
        if (!value.empty()) std::memcpy(start, value.data(), value.size());
        assert(find_space(start, memory + page) == reference(start, memory + page));
    };
    for (size_t length = 0; length <= 128; ++length) {
        std::string value(length, 'x'); check(value);
        for (size_t at = 0; at < length; ++at) { value[at] = ' '; check(value); value[at] = 'x'; }
    }
    for (size_t at = 0; at < 64; ++at) for (unsigned byte = 0; byte < 256; ++byte) {
        std::string value(65, 'x'); value[at] = char(byte); check(value);
    }
    std::mt19937 random(0x9017);
    for (unsigned trial = 0; trial < 100000; ++trial) {
        std::string value(random() % 1025, ' ');
        for (char& byte : value) byte = char(random() % 256);
        check(value);
    }
    munmap(memory, page * 2);
    std::cout << "PASS bounded word-space scan: scalar reference, every byte/offset, random buffers and protected-page tails\n";
}
