#include "io.hpp"
#include <atomic>
#include <cstdlib>
#include <functional>
#include <thread>
#include <utility>
#include <vector>

struct Scanner {
    const char* p;
    const char* end;
    bool more() { while (p < end && *p <= ' ') ++p; return p < end; }
    uint32_t number() {
        if (!more() || *p < '0' || *p > '9') throw std::runtime_error("missing graph number");
        uint64_t value = 0;
        while (p < end && *p >= '0' && *p <= '9') value = value * 10 + *p++ - '0';
        if (value > UINT32_MAX) throw std::runtime_error("graph integer out of range");
        return static_cast<uint32_t>(value);
    }
};
struct Edge { uint32_t to, weight; };
using Item = std::pair<uint64_t, uint32_t>;

int main(int argc, char** argv) {
    try {
        Paths paths(argc, argv);
        MappedFile graph(paths.data / "graph.txt"), queries_file(paths.data / "queries.txt");
        Scanner scan{graph.data, graph.data + graph.size};
        uint32_t n = scan.number(), m = scan.number();
        const char* edge_start = scan.p;
        std::vector<uint32_t> offsets(size_t(n) + 1, 0);
        std::vector<uint8_t> incoming(n, 0);
        for (uint32_t i = 0; i < m; ++i) {
            uint32_t u = scan.number(), v = scan.number(); scan.number();
            if (u >= n || v >= n) throw std::runtime_error("node outside graph");
            ++offsets[size_t(u) + 1]; incoming[v] = 1;
        }
        if (scan.more()) throw std::runtime_error("extra graph edges");
        for (size_t i = 1; i < offsets.size(); ++i) offsets[i] += offsets[i - 1];
        std::vector<Edge> edges(m);
        std::vector<uint32_t> cursor(offsets);
        scan.p = edge_start;
        for (uint32_t i = 0; i < m; ++i) {
            uint32_t u = scan.number(), v = scan.number(), w = scan.number();
            edges[cursor[u]++] = Edge{v, w};
        }
        std::vector<uint32_t>().swap(cursor);
        Scanner qscan{queries_file.data, queries_file.data + queries_file.size};
        std::vector<std::pair<uint32_t, uint32_t>> queries;
        while (qscan.more()) {
            uint32_t s = qscan.number(), t = qscan.number();
            if (s >= n || t >= n) throw std::runtime_error("query outside graph");
            queries.emplace_back(s, t);
        }
        unsigned threads = 3;
        if (const char* value = std::getenv("AFTERBURNER_THREADS")) {
            uint64_t requested = unsigned_number(value);
            if (requested < 1 || requested > 12) throw std::runtime_error("threads must be 1 to 12");
            threads = static_cast<unsigned>(requested);
        }
        threads = static_cast<unsigned>(std::min<size_t>(threads, queries.size()));
        std::vector<int64_t> answers(queries.size(), -1);
        std::atomic<size_t> next{0};
        auto worker = [&] {
            constexpr uint64_t infinity = UINT64_MAX;
            std::vector<uint64_t> distance(n, infinity);
            std::vector<uint32_t> touched;
            std::vector<Item> heap;
            auto greater = std::greater<Item>{};
            for (;;) {
                size_t query = next.fetch_add(1, std::memory_order_relaxed);
                if (query >= queries.size()) return;
                auto [source, target] = queries[query];
                if (source == target) { answers[query] = 0; continue; }
                if (offsets[source] == offsets[source + 1] || !incoming[target]) continue;
                for (uint32_t node : touched) distance[node] = infinity;
                touched.clear(); heap.clear();
                distance[source] = 0; touched.push_back(source); heap.emplace_back(0, source);
                while (!heap.empty()) {
                    std::pop_heap(heap.begin(), heap.end(), greater);
                    auto [d, u] = heap.back(); heap.pop_back();
                    if (d != distance[u]) continue;
                    if (u == target) { answers[query] = static_cast<int64_t>(d); break; }
                    for (uint32_t i = offsets[u]; i < offsets[u + 1]; ++i) {
                        Edge edge = edges[i];
                        uint64_t candidate = d + edge.weight;
                        if (candidate < distance[edge.to]) {
                            if (distance[edge.to] == infinity) touched.push_back(edge.to);
                            distance[edge.to] = candidate;
                            heap.emplace_back(candidate, edge.to);
                            std::push_heap(heap.begin(), heap.end(), greater);
                        }
                    }
                }
            }
        };
        std::vector<std::thread> workers;
        for (unsigned i = 0; i < threads; ++i) workers.emplace_back(worker);
        for (auto& thread : workers) thread.join();
        Output output;
        for (int64_t answer : answers) { output.number(answer); output.text("\n"); }
        output.save(paths.out / "distances.txt");
    } catch (const std::exception& e) {
        std::fprintf(stderr, "track-d: %s\n", e.what());
        return 1;
    }
}
