#include "io.hpp"
#include "decimal.hpp"
#include "parallel.hpp"
#include <atomic>
#include <numeric>

struct Count { uint32_t count = 0, errors = 0; };
struct Workspace {
    struct Slot { std::string_view key; uint32_t id = UINT32_MAX; };
    std::vector<Slot> table = std::vector<Slot>(4096);
    std::vector<std::string_view> paths;
    std::vector<Count> groups;
    std::vector<uint64_t> records;
    std::vector<uint32_t> offsets, cursor, latencies, order;
    uint32_t intern(std::string_view key) {
        size_t slot = std::hash<std::string_view>{}(key) & (table.size() - 1);
        while (table[slot].id != UINT32_MAX) {
            if (table[slot].key == key) return table[slot].id;
            slot = (slot + 1) & (table.size() - 1);
        }
        uint32_t id = static_cast<uint32_t>(paths.size());
        table[slot] = Slot{key, id}; paths.push_back(key); groups.resize(paths.size());
        if (paths.size() * 2 > table.size()) {
            table.assign(table.size() * 2, Slot{});
            for (uint32_t i = 0; i < paths.size(); ++i) {
                size_t p = std::hash<std::string_view>{}(paths[i]) & (table.size() - 1);
                while (table[p].id != UINT32_MAX) p = (p + 1) & (table.size() - 1);
                table[p] = Slot{paths[i], i};
            }
        }
        return id;
    }
};

int main(int argc, char** argv) {
    try {
        Paths paths(argc, argv);
        MappedFile file(paths.data / "requests.log");
        if (file.size > UINT32_MAX) throw std::runtime_error("input exceeds uint32 line-offset capacity");
        const char* end = file.data + file.size;
        unsigned threads = worker_count();
        std::vector<const char*> boundaries(threads + 1);
        boundaries.front() = file.data; boundaries.back() = end;
        for (unsigned i = 1; i < threads; ++i) {
            const char* p = file.data + file.size * i / threads;
            if (p > file.data && p[-1] != '\n') {
                const char* newline = static_cast<const char*>(std::memchr(p, '\n', end - p));
                p = newline ? newline + 1 : end;
            }
            boundaries[i] = p;
        }
        struct Chunk { std::array<std::vector<uint32_t>, 72> lines; };
        std::vector<Chunk> chunks(threads);
        parallel(threads, [&](unsigned worker) {
            const char* p = boundaries[worker];
            const char* limit = boundaries[worker + 1];
            for (auto& lines : chunks[worker].lines) lines.reserve((limit - p) / (72 * 64));
            while (p < limit) {
                if (limit - p < 28) throw std::runtime_error("truncated timestamp");
                int month = (p[5] - '0') * 10 + p[6] - '0';
                int day = (p[8] - '0') * 10 + p[9] - '0';
                int hour = (month == 10 ? day - 30 : day + 1) * 24
                         + (p[11] - '0') * 10 + p[12] - '0' - 18;
                if (hour < 0 || hour >= 72) throw std::runtime_error("hour outside specification");
                chunks[worker].lines[hour].push_back(static_cast<uint32_t>(p - file.data));
                const char* newline = static_cast<const char*>(std::memchr(p + 28, '\n', limit - p - 28));
                if (!newline) throw std::runtime_error("missing latency newline");
                p = newline + 1;
            }
        });
        std::array<Output, 72> output;
        std::atomic<unsigned> next_hour{0};
        parallel(threads, [&](unsigned) {
            Workspace local;
            for (;;) {
                unsigned hour = next_hour.fetch_add(1, std::memory_order_relaxed);
                if (hour >= 72) return;
                local.records.clear();
                std::fill(local.groups.begin(), local.groups.end(), Count{});
                size_t count = 0;
                for (const auto& chunk : chunks) count += chunk.lines[hour].size();
                if (!count) continue;
                local.records.reserve(count);
                std::string label;
                for (auto& chunk : chunks) {
                    for (uint32_t position : chunk.lines[hour]) {
                        const char* p = file.data + position;
                        if (label.empty()) label = std::string(p, 13) + ":00:00Z";
                        p += 28;
                        while (p < end && *p != ' ') ++p;
                        if (p == end) throw std::runtime_error("missing endpoint");
                        const char* start = ++p;
                        p = static_cast<const char*>(std::memchr(start, ' ', end - start));
                        if (!p || end - p < 5) throw std::runtime_error("missing endpoint/status");
                        std::string_view endpoint(start, p - start);
                        bool error = p[1] == '5'; p += 5;
                        start = p;
                        uint64_t latency = decimal_digits(p, end);
                        if (p == start || p - start > 10 || latency > UINT32_MAX || p == end || *p != '\n')
                            throw std::runtime_error("invalid latency line");
                        uint32_t group = local.intern(endpoint);
                        ++local.groups[group].count; local.groups[group].errors += error;
                        local.records.push_back(uint64_t(group) << 32 | latency);
                    }
                    // Only this hour's worker reads or releases this vector.
                    std::vector<uint32_t>().swap(chunk.lines[hour]);
                }
                size_t endpoints = local.paths.size();
                local.offsets.assign(endpoints + 1, 0);
                for (size_t e = 0; e < endpoints; ++e) local.offsets[e + 1] = local.offsets[e] + local.groups[e].count;
                local.cursor = local.offsets;
                local.latencies.resize(count);
                for (uint64_t record : local.records) local.latencies[local.cursor[record >> 32]++] = uint32_t(record);
                if (local.order.size() != endpoints) {
                    local.order.resize(endpoints); std::iota(local.order.begin(), local.order.end(), 0);
                    std::sort(local.order.begin(), local.order.end(), [&](auto a, auto b) { return local.paths[a] < local.paths[b]; });
                }
                auto& out = output[hour];
                out.bytes.reserve(endpoints * 100);
                for (uint32_t e : local.order) {
                    uint64_t n = local.groups[e].count, errors = local.groups[e].errors;
                    if (!n) continue;
                    auto first = local.latencies.begin() + local.offsets[e];
                    if (n < 64) std::sort(first, first + n);
                    else {
                        size_t unselected = 0;
                        for (uint64_t percentile : {50, 95, 99}) {
                            size_t rank = (percentile * n + 99) / 100 - 1;
                            if (rank >= unselected) {
                                std::nth_element(first + unselected, first + rank, first + n);
                                unselected = rank + 1;
                            }
                        }
                    }
                    out.text(label); out.text(" "); out.text(local.paths[e]);
                    for (uint64_t value : {n, uint64_t(first[(50 * n + 99) / 100 - 1]),
                                           uint64_t(first[(95 * n + 99) / 100 - 1]),
                                           uint64_t(first[(99 * n + 99) / 100 - 1]), errors, errors * 1000000 / n}) {
                        out.text(" "); out.number(static_cast<int64_t>(value));
                    }
                    out.text("\n");
                }
            }
        });
        std::ofstream stream(paths.out / "summary.txt", std::ios::binary);
        for (const auto& hour : output) stream.write(hour.bytes.data(), static_cast<std::streamsize>(hour.bytes.size()));
        stream.close();
        if (!stream) throw std::runtime_error("cannot write summary.txt");
    } catch (const std::exception& error) {
        std::fprintf(stderr, "track-a: %s\n", error.what());
        return 1;
    }
}
