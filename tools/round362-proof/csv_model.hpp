#pragma once
#include "source/track-c/io.hpp"
#include "source/track-c/quote_scan.hpp"
struct Field { std::string_view value; size_t bytes; bool escaped; };
struct Csv {
    const char* p;
    const char* end;
    void bom() {
        if (end - p >= 3 && std::memcmp(p, "\xef\xbb\xbf", 3) == 0) p += 3;
    }
    Field field(std::string& scratch, bool decode) {
        const char* start = p;
        if (p == end || *p != '"') {
            while (p < end && *p != ',' && *p != '\r' && *p != '\n') ++p;
            return {{start, static_cast<size_t>(p - start)}, static_cast<size_t>(p - start), false};
        }
        const char* segment = ++p;
        start = segment;
        size_t bytes = 0;
        bool escaped = false;
        while (p < end) {
            const char* quote = find_quote(p, end);
            if (!quote) throw std::runtime_error("unterminated quoted field");
            bytes += static_cast<size_t>(quote - segment);
            if (quote + 1 < end && quote[1] == '"') {
                if (decode) {
                    if (!escaped) scratch.assign(start, quote - start);
                    else scratch.append(segment, quote - segment);
                    scratch.push_back('"');
                }
                ++bytes;
                escaped = true;
                segment = p = quote + 2;
            } else {
                p = quote + 1;
                if (decode && escaped) scratch.append(segment, quote - segment);
                std::string_view value = escaped && decode ? std::string_view(scratch)
                    : std::string_view(start, static_cast<size_t>(quote - start));
                return {value, bytes, escaped};
            }
        }
        throw std::runtime_error("unterminated quoted field");
    }
    void comma() {
        if (p == end || *p++ != ',') throw std::runtime_error("expected CSV comma");
    }
    uint64_t integer() {
        const char* start = p;
        uint64_t value = 0;
        while (p < end && *p >= '0' && *p <= '9') value = value * 10 + *p++ - '0';
        if (p == start) throw std::runtime_error("missing CSV integer");
        comma();
        return value;
    }
    int64_t amount() {
        bool negative = p < end && *p == '-';
        if (negative) ++p;
        const char* start = p;
        uint64_t value = 0;
        while (p < end && *p >= '0' && *p <= '9') value = value * 10 + *p++ - '0';
        if (p == start || p == end || *p++ != '.' || end - p < 2 || p[0] < '0' || p[0] > '9' || p[1] < '0' || p[1] > '9')
            throw std::runtime_error("invalid money");
        value = value * 100 + (p[0] - '0') * 10 + p[1] - '0'; p += 2;
        return negative ? -static_cast<int64_t>(value) : static_cast<int64_t>(value);
    }
    void newline() {
        if (p == end) return; // The final record may omit its terminator.
        if (*p == '\r') ++p;
        if (p == end || *p++ != '\n') throw std::runtime_error("expected CSV terminator");
    }
};

