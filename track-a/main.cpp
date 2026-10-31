#include "io.hpp"
#include "decimal.hpp"
#include "endpoint_table.hpp"
#include "parallel.hpp"
#include <atomic>
#include <memory>
#include <numeric>

static constexpr uint32_t latency_escape = (1U << 19) - 1;
struct Count { uint32_t count = 0, errors = 0; };

int main(int argc, char** argv) {
    try {
        Paths run_paths(argc, argv);
        MappedFile file(run_paths.data / "requests.log");
        if (file.size > UINT32_MAX) throw std::runtime_error("input exceeds uint32 capacity");
        const char* end = file.data + file.size;
        unsigned threads = worker_count();
        std::vector<const char*> boundaries(threads + 1);
        boundaries.front() = file.data; boundaries.back() = end;
        for (unsigned i = 1; i < threads; ++i) {
            const char* p = file.data + file.size * i / threads;
            if (p > file.data && p[-1] != '\n') {
                const char* newline = static_cast<const char*>(std::memchr(p, '\n', end - p)); p = newline ? newline + 1 : end;
            }
            boundaries[i] = p;
        }
        Endpoints endpoints;
        struct Chunk {
            std::array<std::vector<uint32_t>, 72> records, wide;
            std::array<uint32_t, 72> first;
            Chunk() { first.fill(UINT32_MAX); }
        };
        std::vector<Chunk> chunks(threads);
        parallel(threads, [&](unsigned worker) {
            const char* p = boundaries[worker]; const char* limit = boundaries[worker + 1];
            auto& chunk = chunks[worker];
            size_t reserve_hint = (limit - p) / (72 * 64);
            while (p < limit) {
                if (limit - p < 28) throw std::runtime_error("truncated timestamp");
                const char* line = p;
                int month = (p[5] - '0') * 10 + p[6] - '0', day = (p[8] - '0') * 10 + p[9] - '0';
                int hour = (month == 10 ? day - 30 : day + 1) * 24 + (p[11] - '0') * 10 + p[12] - '0' - 18;
                if (hour < 0 || hour >= 72) throw std::runtime_error("hour outside specification");
                p += 28; while (p < limit && *p != ' ') ++p;
                if (p == limit) throw std::runtime_error("missing endpoint");
                const char* start = ++p;
                p = static_cast<const char*>(std::memchr(start, ' ', limit - start));
                if (!p || limit - p < 5) throw std::runtime_error("missing endpoint/status");
                std::string_view endpoint(start, p - start);
                bool error = p[1] == '5'; p += 5; start = p;
                uint64_t latency = decimal_digits(p, limit);
                if (p == start || p - start > 10 || latency > UINT32_MAX || p == limit || *p != '\n') throw std::runtime_error("invalid latency");
                ++p;
                uint16_t key = endpoints.intern(endpoint, std::hash<std::string_view>{}(endpoint));
                if (chunk.first[hour] == UINT32_MAX) {
                    chunk.first[hour] = static_cast<uint32_t>(line - file.data);
                    chunk.records[hour].reserve(reserve_hint);
                }
                chunk.records[hour].push_back(std::min(uint32_t(latency), latency_escape) << 13 | uint32_t(error) << 12 | key);
                if (latency >= latency_escape) chunk.wide[hour].push_back(static_cast<uint32_t>(latency));
            }
        });
        std::vector<std::string_view> paths(endpoints.used.load());
        for (size_t i = 0; i < Endpoints::capacity; ++i) {
            auto state = endpoints.entries[i].state.load();
            if (state > 1) paths[(state & 65535) - 2] = endpoints.entries[i].value;
        }
        endpoints.entries.reset(); // Path views borrow the still-mapped input.
        std::vector<uint16_t> order(paths.size()); std::iota(order.begin(), order.end(), 0);
        std::sort(order.begin(), order.end(), [&](uint16_t a, uint16_t b) { return paths[a] < paths[b]; });
        std::array<Output, 72> output;
        std::atomic<unsigned> next_hour{0};
        parallel(threads, [&](unsigned) {
            std::vector<Count> groups(paths.size());
            std::vector<uint32_t> offsets(paths.size()), cursor(paths.size()), latencies;
            for (;;) {
                unsigned hour = next_hour.fetch_add(1, std::memory_order_relaxed); if (hour >= 72) return;
                std::fill(groups.begin(), groups.end(), Count{});
                size_t count = 0; uint32_t first_line = UINT32_MAX;
                for (const auto& chunk : chunks) {
                    count += chunk.records[hour].size(); first_line = std::min(first_line, chunk.first[hour]);
                    for (uint32_t record : chunk.records[hour]) { auto& group = groups[record & 4095]; ++group.count; group.errors += (record >> 12) & 1; }
                }
                if (!count) continue;
                uint32_t offset = 0;
                for (uint16_t key : order) { cursor[key] = offsets[key] = offset; offset += groups[key].count; }
                latencies.resize(count);
                for (auto& chunk : chunks) {
                    size_t wide = 0;
                    for (uint32_t record : chunk.records[hour]) {
                        uint32_t latency = record >> 13;
                        if (latency == latency_escape) latency = chunk.wide[hour][wide++];
                        latencies[cursor[record & 4095]++] = latency;
                    }
                    std::vector<uint32_t>().swap(chunk.records[hour]); std::vector<uint32_t>().swap(chunk.wide[hour]);
                }
                std::string label = std::string(file.data + first_line, 13) + ":00:00Z";
                auto& out = output[hour]; out.bytes.reserve(order.size() * 100);
                for (uint16_t key : order) {
                    uint64_t n = groups[key].count, errors = groups[key].errors; if (!n) continue;
                    auto first = latencies.begin() + offsets[key];
                    if (n < 64) std::sort(first, first + n);
                    else {
                        size_t unselected = 0;
                        for (uint64_t percentile : {50, 95, 99}) {
                            size_t rank = (percentile * n + 99) / 100 - 1;
                            if (rank >= unselected) { std::nth_element(first + unselected, first + rank, first + n); unselected = rank + 1; }
                        }
                    }
                    out.text(label); out.text(" "); out.text(paths[key]);
                    for (uint64_t value : {n, uint64_t(first[(50 * n + 99) / 100 - 1]), uint64_t(first[(95 * n + 99) / 100 - 1]), uint64_t(first[(99 * n + 99) / 100 - 1]), errors, errors * 1000000 / n}) { out.text(" "); out.number(static_cast<int64_t>(value)); }
                    out.text("\n");
                }
            }
        });
        std::ofstream stream(run_paths.out / "summary.txt", std::ios::binary);
        for (const auto& hour : output) stream.write(hour.bytes.data(), static_cast<std::streamsize>(hour.bytes.size()));
        stream.close(); if (!stream) throw std::runtime_error("cannot write summary.txt");
    } catch (const std::exception& e) { std::fprintf(stderr,"track-a: %s\n",e.what()); return 1; }
}
