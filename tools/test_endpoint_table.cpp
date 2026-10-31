#ifndef ENDPOINTS_HEADER
#define ENDPOINTS_HEADER "../track-a/endpoint_table.hpp"
#endif
#include ENDPOINTS_HEADER
#include <array>
#include <cassert>
#include <functional>
#include <iostream>
#include <set>
#include <string>
#include <thread>
#include <vector>

int main() {
    Endpoints names;
    constexpr unsigned count = 701, workers = 4;
    std::vector<std::string> keys;
    for (unsigned i = 0; i < count; ++i) keys.push_back("endpoint/" + std::to_string(i));
    keys[0] = ""; keys[1] = std::string("a\0b", 3); keys[2] = "UTF-8 \xe5\x90\x8d";
    std::array<std::atomic<unsigned>, count> ids;
    for (auto& id : ids) id.store(UINT32_MAX);
    std::atomic<bool> mismatch{false};
    std::vector<std::thread> threads;
    for (unsigned w = 0; w < workers; ++w) threads.emplace_back([&, w] {
        for (unsigned i = 0; i < 6000; ++i) {
            unsigned key = (i * 7 + w * 13) % count;
            // Deliberately identical complete hashes: equality must compare bytes.
            unsigned actual = names.intern(keys[key], 42);
            unsigned expected = UINT32_MAX;
            if (!ids[key].compare_exchange_strong(expected, actual) && expected != actual) mismatch.store(true);
        }
    });
    for (auto& thread : threads) thread.join();
    assert(!mismatch.load() && names.used.load() == count);
    std::set<unsigned> unique;
    for (auto& id : ids) unique.insert(id.load());
    assert(unique.size() == count && *unique.rbegin() < 4096);
    Endpoints boundaries;
    std::vector<std::string> limit_keys;
    for (unsigned i = 0; i < 4097; ++i) limit_keys.push_back("boundary/" + std::to_string(i));
    for (unsigned i = 0; i < 4096; ++i) {
        auto hash = std::hash<std::string_view>{}(limit_keys[i]);
        assert(boundaries.intern(limit_keys[i], hash) == i);
        assert(boundaries.intern(limit_keys[i], hash) == i);
    }
    bool rejected = false;
    try { boundaries.intern(limit_keys.back(), 0); } catch (const std::runtime_error&) { rejected = true; }
    assert(rejected && boundaries.canceled.load());
    Endpoints states;
    assert(states.intern("zero", 0) == 0);
    assert(states.intern("one", 1) == 1);
    assert(states.intern("max", UINT64_MAX) == 2);
    assert(states.intern("zero", 0) == 0);
    std::cout << "PASS concurrent full-hash collisions, exact bytes, unique IDs, reserved states and 12-bit ID boundary\n";
}
