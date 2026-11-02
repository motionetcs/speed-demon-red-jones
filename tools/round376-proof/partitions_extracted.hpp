#pragma once
#include <atomic>
#include <cstddef>
#include <cstring>
#include <vector>
struct SplitResult {size_t parts;std::vector<const char*> boundaries;};
template<size_t Block> SplitResult split_actual(const char* data,size_t size){
    static_assert(Block>0);
    struct FileView {const char* data;size_t size;};FileView file{data,size};
    const char* end=data+size;
        constexpr size_t parse_block_bytes = Block;
        size_t parts = (file.size + parse_block_bytes - 1) / parse_block_bytes;
        std::vector<const char*> boundaries(parts + 1);
        boundaries.front() = file.data; boundaries.back() = end;
        for (size_t i = 1; i < parts; ++i) {
            const char* p = file.data + i * parse_block_bytes;
            if (p > file.data && p[-1] != '\n') {
                const char* newline = static_cast<const char*>(std::memchr(p, '\n', end - p)); p = newline ? newline + 1 : end;
            }
            boundaries[i] = p;
        }
    return {parts,std::move(boundaries)};
}
template<class Callback> void claims_actual(const std::vector<const char*>& boundaries,size_t parts,std::atomic<size_t>& next_part,Callback callback){
            for (;;) {
                size_t part = next_part.fetch_add(1, std::memory_order_relaxed);
                if (part >= parts) break;
                const char* p = boundaries[part]; const char* limit = boundaries[part + 1];
                callback(part,p,limit);
            }
}
