#include "io.hpp"
#include <array>
#include <memory>
#include <unordered_map>
#include <vector>

struct Group {
    std::vector<uint32_t> latencies;
    uint32_t errors = 0;
};
struct Endpoint {
    std::string_view path;
    std::array<Group, 72> hours;
};

int main(int argc, char** argv) {
    try {
        Paths paths(argc, argv);
        MappedFile file(paths.data / "requests.log");
        const char* p = file.data;
        const char* end = p + file.size;
        std::unordered_map<std::string_view, size_t> ids;
        ids.reserve(2048);
        std::vector<std::unique_ptr<Endpoint>> endpoints;
        std::array<std::string, 72> hours;
        while (p < end) {
            if (end - p < 28) throw std::runtime_error("truncated timestamp");
            int month = (p[5] - '0') * 10 + p[6] - '0';
            int day = (p[8] - '0') * 10 + p[9] - '0';
            int hour = ((month == 10 ? day - 30 : day + 1) * 24)
                       + (p[11] - '0') * 10 + p[12] - '0' - 18;
            if (hour < 0 || hour >= 72) throw std::runtime_error("hour outside specification");
            if (hours[hour].empty()) hours[hour] = std::string(p, 13) + ":00:00Z";
            p += 28;
            while (p < end && *p != ' ') ++p; // Skip the method; it is not part of the key.
            if (p == end) throw std::runtime_error("missing endpoint");
            const char* start = ++p;
            while (p < end && *p != ' ') ++p;
            std::string_view endpoint(start, p - start);
            if (end - p < 5) throw std::runtime_error("missing status");
            bool error = p[1] == '5';
            p += 5;
            start = p;
            while (p < end && *p != '\n') ++p;
            uint64_t latency = unsigned_number({start, static_cast<size_t>(p - start)});
            if (latency > UINT32_MAX || p == end) throw std::runtime_error("invalid latency line");
            ++p;
            auto [it, inserted] = ids.try_emplace(endpoint, endpoints.size());
            if (inserted) {
                auto entry = std::make_unique<Endpoint>();
                entry->path = endpoint;
                endpoints.push_back(std::move(entry));
            }
            Group& group = endpoints[it->second]->hours[hour];
            group.latencies.push_back(static_cast<uint32_t>(latency));
            group.errors += error;
        }
        std::sort(endpoints.begin(), endpoints.end(), [](const auto& a, const auto& b) {
            return a->path < b->path;
        });
        Output output;
        for (size_t hour = 0; hour < hours.size(); ++hour) {
            for (const auto& endpoint : endpoints) {
                Group& group = endpoint->hours[hour];
                auto& values = group.latencies;
                if (values.empty()) continue;
                std::sort(values.begin(), values.end());
                uint64_t n = values.size();
                output.text(hours[hour]); output.text(" "); output.text(endpoint->path);
                for (uint64_t v : {n, uint64_t(values[(50 * n + 99) / 100 - 1]),
                                   uint64_t(values[(95 * n + 99) / 100 - 1]),
                                   uint64_t(values[(99 * n + 99) / 100 - 1]),
                                   uint64_t(group.errors), uint64_t(group.errors) * 1000000 / n}) {
                    output.text(" "); output.number(static_cast<int64_t>(v));
                }
                output.text("\n");
            }
        }
        output.save(paths.out / "summary.txt");
    } catch (const std::exception& e) {
        std::fprintf(stderr, "track-a: %s\n", e.what());
        return 1;
    }
}
