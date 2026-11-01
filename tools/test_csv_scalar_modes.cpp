#ifndef CSV_HEADER
#define CSV_HEADER "c-note-count-csv.hpp"
#endif
#include CSV_HEADER
#include <cassert>
#include <iostream>
#include <random>
#include <sys/mman.h>
#include <unistd.h>

void check(const char* begin, const char* end, std::string_view raw, std::string_view decoded) {
    std::string scratch;
    Csv raw_csv{begin, end};
    auto field = raw_csv.field(scratch,false);
    assert(raw_csv.p == end && field.value == raw && field.bytes == decoded.size());
    Csv decoded_csv{begin, end};
    auto decoded_field = decoded_csv.field(scratch,true);
    assert(decoded_csv.p == end && decoded_field.value == decoded && decoded_field.bytes == decoded.size());
    Csv count_csv{begin, end};
    auto count = count_csv.field(scratch,false).bytes;
    assert(count_csv.p == end && count == decoded.size());
}
void quoted(std::string_view decoded) {
    std::string raw;
    for (char byte : decoded) {
        raw += byte;
        if (byte == '"') raw += '"';
    }
    std::string input = '"' + raw + '"';
    check(input.data(), input.data() + input.size(), raw, decoded);
    size_t page = static_cast<size_t>(sysconf(_SC_PAGESIZE));
    if (input.size() <= page) {
        void* allocation = mmap(nullptr, page * 3, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANON, -1, 0);
        assert(allocation != MAP_FAILED);
        auto* data = static_cast<char*>(allocation);
        assert(mprotect(data, page, PROT_NONE) == 0);
        assert(mprotect(data + 2 * page, page, PROT_NONE) == 0);
        for (char* location : {data + page, data + 2 * page - input.size()}) {
            std::memcpy(location, input.data(), input.size());
            check(location, location + input.size(), raw, decoded);
        }
        assert(munmap(allocation, page * 3) == 0);
    }
}
int main() {
    for (unsigned byte = 0; byte < 256; ++byte) quoted(std::string(1, static_cast<char>(byte)));
    for (std::string value : {"", "plain", "trailing ", "comma,here", "\"quoted\"", "line\nnext", "\r\n", "\xef\xbb\xbf"}) quoted(value);
    std::mt19937_64 random(0xC5F1E1D);
    for (unsigned iteration = 0; iteration < 700; ++iteration) {
        std::string value(random() % 1500, ' ');
        for (char& byte : value) byte = static_cast<char>(random());
        quoted(value);
    }
    quoted(std::string(1 << 20, '"'));
    for (std::string input : {"", "plain", "trailing ", "\xef\xbb\xbf"}) check(input.data(), input.data() + input.size(), input, input);
    for (std::string input : {"\"", "\"unterminated", "\"\"\"", "\"abc\"\""}) {
        std::string scratch;
        Csv csv{input.data(), input.data() + input.size()};
        bool threw = false;
        try { csv.field(scratch,false); } catch (const std::runtime_error&) { threw = true; }
        assert(threw);
    }
    std::cout << "PASS exact original scalar raw/decoded/byte-count CSV bytes, every byte, quotes, LF/CR/BOM/NUL, random fields,1MiB values and protected boundaries\n";
}
