#include "io.hpp"
#include "parallel.hpp"
#include <atomic>
#include <unordered_map>

struct Count { uint32_t count = 0, errors = 0; };
struct Local {
    struct Slot { std::string_view key; uint32_t id = UINT32_MAX; };
    std::vector<Slot> table = std::vector<Slot>(4096);
    std::vector<std::string_view> paths;
    std::vector<Count> groups;
    std::vector<uint64_t> records;
    std::array<std::string, 72> hours;
    uint32_t intern(std::string_view key) {
        size_t slot = std::hash<std::string_view>{}(key) & (table.size() - 1);
        while (table[slot].id != UINT32_MAX) {
            if (table[slot].key == key) return table[slot].id;
            slot = (slot + 1) & (table.size() - 1);
        }
        uint32_t id = static_cast<uint32_t>(paths.size());
        table[slot] = Slot{key, id}; paths.push_back(key); groups.resize(paths.size() * 72);
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
        unsigned threads = worker_count();
        std::vector<const char*> boundaries(threads + 1);
        boundaries.front() = file.data; boundaries.back() = file.data + file.size;
        for (unsigned i = 1; i < threads; ++i) {
            const char* p = file.data + file.size * i / threads;
            if (p > file.data && p[-1] != '\n') {
                auto newline = static_cast<const char*>(std::memchr(p, '\n', file.data + file.size - p));
                p = newline ? newline + 1 : file.data + file.size;
            }
            boundaries[i] = p;
        }
        std::vector<Local> locals(threads);
        parallel(threads, [&](unsigned worker) {
            auto& local = locals[worker];
            const char* p = boundaries[worker];
            const char* end = boundaries[worker + 1];
            local.records.reserve(static_cast<size_t>(end - p) / 64);
            while (p < end) {
                if (end - p < 28) throw std::runtime_error("truncated timestamp");
                int month = (p[5] - '0') * 10 + p[6] - '0';
                int day = (p[8] - '0') * 10 + p[9] - '0';
                int hour = (month == 10 ? day - 30 : day + 1) * 24
                         + (p[11] - '0') * 10 + p[12] - '0' - 18;
                if (hour < 0 || hour >= 72) throw std::runtime_error("hour outside specification");
                if (local.hours[hour].empty()) local.hours[hour] = std::string(p, 13) + ":00:00Z";
                p += 28;
                while (p < end && *p != ' ') ++p;
                if (p == end) throw std::runtime_error("missing endpoint");
                const char* start = ++p;
                p = static_cast<const char*>(std::memchr(start, ' ', end - start));
                if (!p) throw std::runtime_error("missing endpoint delimiter");
                std::string_view endpoint(start, p - start);
                if (end - p < 5) throw std::runtime_error("missing status");
                bool error = p[1] == '5'; p += 5;
                start = p;
                uint64_t latency = 0;
                while (p < end && *p >= '0' && *p <= '9') latency = latency * 10 + *p++ - '0';
                if (p == start || p - start > 10 || latency > UINT32_MAX || p == end || *p != '\n')
                    throw std::runtime_error("invalid latency line");
                ++p;
                uint32_t group = local.intern(endpoint) * 72 + hour;
                ++local.groups[group].count; local.groups[group].errors += error;
                local.records.push_back(uint64_t(group) << 32 | latency);
            }
        });
        std::unordered_map<std::string_view, uint32_t> ids;
        ids.reserve(2048);
        std::array<std::string, 72> hours;
        for (const auto& local : locals) {
            for (auto path : local.paths) ids.try_emplace(path, 0);
            for (size_t h = 0; h < 72; ++h) if (!local.hours[h].empty()) hours[h] = local.hours[h];
        }
        std::vector<std::string_view> endpoints;
        for (auto [path, id] : ids) endpoints.push_back(path);
        std::sort(endpoints.begin(), endpoints.end());
        for (uint32_t i = 0; i < endpoints.size(); ++i) ids[endpoints[i]] = i;
        size_t endpoint_count = endpoints.size(), group_count = endpoint_count * 72;
        std::vector<Count> totals(group_count);
        for (const auto& local : locals) for (size_t e = 0; e < local.paths.size(); ++e) {
            size_t id = ids.at(local.paths[e]);
            for (size_t h = 0; h < 72; ++h) {
                auto count = local.groups[e * 72 + h];
                totals[h * endpoint_count + id].count += count.count;
                totals[h * endpoint_count + id].errors += count.errors;
            }
        }
        std::vector<uint32_t> offsets(group_count + 1);
        for (size_t i = 0; i < group_count; ++i) offsets[i + 1] = offsets[i] + totals[i].count;
        std::vector<uint32_t> cursor(offsets), latencies(offsets.back());
        for (auto& local : locals) for (size_t e = 0; e < local.paths.size(); ++e) {
            size_t id = ids.at(local.paths[e]);
            for (size_t h = 0; h < 72; ++h) {
                auto& count = local.groups[e * 72 + h].count;
                size_t group = h * endpoint_count + id;
                uint32_t n = count; count = cursor[group]; cursor[group] += n;
            }
        }
        parallel(threads, [&](unsigned worker) {
            auto& local = locals[worker];
            for (uint64_t record : local.records)
                latencies[local.groups[record >> 32].count++] = static_cast<uint32_t>(record);
        });
        locals.clear();
        std::array<Output, 72> output;
        std::atomic<unsigned> next_hour{0};
        parallel(threads, [&](unsigned) {
            for (;;) {
                unsigned h = next_hour.fetch_add(1, std::memory_order_relaxed);
                if (h >= 72) return;
                output[h].bytes.reserve(endpoint_count * 100);
                for (size_t e = 0; e < endpoint_count; ++e) {
                    size_t group = h * endpoint_count + e;
                    uint64_t n = totals[group].count, errors = totals[group].errors;
                    if (!n) continue;
                    auto first = latencies.begin() + offsets[group];
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
                    output[h].text(hours[h]); output[h].text(" "); output[h].text(endpoints[e]);
                    for (uint64_t value : {n, uint64_t(first[(50 * n + 99) / 100 - 1]),
                                           uint64_t(first[(95 * n + 99) / 100 - 1]),
                                           uint64_t(first[(99 * n + 99) / 100 - 1]), errors, errors * 1000000 / n}) {
                        output[h].text(" "); output[h].number(static_cast<int64_t>(value));
                    }
                    output[h].text("\n");
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
