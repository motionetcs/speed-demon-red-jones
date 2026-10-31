#ifdef LOAD_CURSORS_HEADER
#include LOAD_CURSORS_HEADER
#else
#include "../track-d/load_cursors.hpp"
#endif
#include <cassert>
#include <iostream>
#include <thread>

int main() {
    constexpr uint32_t nodes = 4 * SharedCursor::block_size + 17;
    std::vector<uint32_t> counts(nodes);
    counts[0] = 65535;
    counts[SharedCursor::block_size] = 65536;
    counts[2 * SharedCursor::block_size] = 255;
    counts[2 * SharedCursor::block_size + 1] = 256;
    counts[2 * SharedCursor::block_size + 2] = 257;
    counts[3 * SharedCursor::block_size] = 180000;
    counts.back() = 1025;
    for (unsigned owners = 1; owners <= 11; ++owners) {
        DegreeBytes degree(nodes);
        std::vector<DegreeBytes::Spills> spills(owners);
        std::vector<std::jthread> workers;
        for (unsigned owner = 0; owner < owners; ++owner) workers.emplace_back([&, owner] {
            for (uint32_t node = 0; node < nodes; ++node) if ((node >> 12) % owners == owner)
                for (uint32_t i = 0; i < counts[node]; ++i) degree.add_owned(node, spills[owner]);
        });
        workers.clear();
        std::vector<uint32_t> starts(size_t(nodes) + 1);
        for (uint32_t node = 0; node < nodes; ++node) {
            uint32_t actual = degree.values[node];
            for (auto& local : spills) if (auto it = local.find(node); it != local.end()) actual += it->second;
            assert(actual == counts[node]);
            starts[node + 1] = starts[node] + actual;
        }
        SharedCursor cursor(starts);
        assert(cursor.wide_blocks == 2);
        std::vector<uint8_t> written(starts.back());
        for (unsigned owner = 0; owner < owners; ++owner) workers.emplace_back([&, owner] {
            for (uint32_t node = 0; node < nodes; ++node) if ((node >> 12) % owners == owner) {
                cursor.prefetch<true>(node);
                for (uint32_t i = 0; i < counts[node]; ++i) {
                    uint32_t slot = cursor.take_owned<true>(node);
                    assert(slot == starts[node] + i);
                    written[slot] = 1;
                }
            }
        });
        workers.clear();
        for (auto byte : written) assert(byte == 1);
        std::vector<uint32_t> narrow_starts{0, 255, 511, 768, 1025};
        SharedCursor narrow(narrow_starts);
        assert(narrow.wide_blocks == 0);
        for (uint32_t node = 0; node + 1 < narrow_starts.size(); ++node)
            for (uint32_t i = narrow_starts[node]; i < narrow_starts[node + 1]; ++i)
                assert(narrow.take_owned<false>(node) == i);
    }
    std::cout << "PASS exclusive4096-node-block degree/cursor model: owners1..11, byte wraps,65535/65536 and full-width blocks, exact unique slots, partial final block\n";
}
