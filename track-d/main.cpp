#include "radix_heap.hpp"
#include "io.hpp"
#include "distance_map.hpp"
#include "parallel.hpp"
#include <memory>
#include <atomic>
#include <cstdlib>
#include <functional>
#include <thread>
#include <utility>
#include <vector>
#include <unordered_map>

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
struct __attribute__((packed)) Edge { uint32_t to; uint16_t weight; };
static_assert(sizeof(Edge) == 6);
using Item = std::pair<uint64_t, uint32_t>;

int main(int argc, char** argv) {
    try {
        Paths paths(argc, argv);
        unsigned threads = 6;
        if (const char* value = std::getenv("SPEED_DEMON_THREADS")) {
            uint64_t requested = unsigned_number(value);
            if (requested < 1 || requested > 12) throw std::runtime_error("threads must be 1 to 12");
            threads = static_cast<unsigned>(requested);
        }
        MappedFile graph(paths.data / "graph.txt"), queries_file(paths.data / "queries.txt");
        Scanner scan{graph.data, graph.data + graph.size};
        uint32_t n = scan.number(), m = scan.number();
        const char* edge_start = scan.p;
        while (edge_start < graph.data + graph.size && *edge_start <= ' ') ++edge_start;
        unsigned loaders = std::min(threads, 4U);
        std::vector<const char*> boundaries(loaders + 1);
        boundaries.front() = edge_start; boundaries.back() = graph.data + graph.size;
        for (unsigned i = 1; i < loaders; ++i) {
            const char* p = edge_start + (graph.data + graph.size - edge_start) * i / loaders;
            if (p > edge_start && p[-1] != '\n') {
                const char* newline = static_cast<const char*>(std::memchr(p, '\n', graph.data + graph.size - p));
                p = newline ? newline + 1 : graph.data + graph.size;
            }
            boundaries[i] = p;
        }
        struct Triple { uint32_t from, to, weight; };
        struct Local {
            std::vector<Triple> edges;
            std::vector<uint32_t> out, in;
            std::vector<std::pair<uint32_t, uint32_t>> wide;
        };
        std::vector<Local> locals(loaders);
        parallel(loaders, [&](unsigned worker) {
            auto& local = locals[worker]; local.out.resize(n); local.in.resize(n);
            Scanner input{boundaries[worker], boundaries[worker + 1]};
            local.edges.reserve(static_cast<size_t>(input.end - input.p) / 18);
            while (input.more()) {
                uint32_t u = input.number(), v = input.number(), weight = input.number();
                if (u >= n || v >= n) throw std::runtime_error("node outside graph");
                local.edges.push_back(Triple{u, v, weight}); ++local.out[u]; ++local.in[v];
            }
        });
        std::vector<uint32_t> offsets(size_t(n) + 1), reverse_offsets(size_t(n) + 1);
        size_t edge_count = 0;
        for (const auto& local : locals) {
            edge_count += local.edges.size();
            for (size_t i = 0; i < n; ++i) {
                offsets[i + 1] += local.out[i]; reverse_offsets[i + 1] += local.in[i];
            }
        }
        if (edge_count != m) throw std::runtime_error("edge count does not match header");
        for (size_t i = 1; i <= n; ++i) {
            offsets[i] += offsets[i - 1]; reverse_offsets[i] += reverse_offsets[i - 1];
        }
        // Local degree arrays become disjoint scatter cursors; shift the advanced
        // global ends back into starts after assigning each worker its range.
        for (auto& local : locals) for (size_t i = 0; i < n; ++i) {
            uint32_t out = local.out[i], in = local.in[i];
            local.out[i] = offsets[i]; local.in[i] = reverse_offsets[i];
            offsets[i] += out; reverse_offsets[i] += in;
        }
        for (size_t i = n; i > 0; --i) { offsets[i] = offsets[i - 1]; reverse_offsets[i] = reverse_offsets[i - 1]; }
        offsets[0] = reverse_offsets[0] = 0;
        std::vector<Edge> edges(m), reverse_edges(m);
        parallel(loaders, [&](unsigned worker) {
            auto& local = locals[worker];
            for (const auto& edge : local.edges) {
                uint32_t out = local.out[edge.from]++, in = local.in[edge.to]++;
                uint16_t weight = static_cast<uint16_t>(std::min(edge.weight, uint32_t(UINT16_MAX)));
                edges[out] = Edge{edge.to, weight}; reverse_edges[in] = Edge{edge.from, weight};
                if (edge.weight >= UINT16_MAX) {
                    local.wide.emplace_back(out * 2, edge.weight);
                    local.wide.emplace_back(in * 2 + 1, edge.weight);
                }
            }
        });
        std::unordered_map<uint32_t, uint32_t> wide_weights;
        for (const auto& local : locals) for (auto [index, weight] : local.wide) wide_weights.emplace(index, weight);
        locals.clear();
        Scanner qscan{queries_file.data, queries_file.data + queries_file.size};
        std::vector<std::pair<uint32_t, uint32_t>> queries;
        while (qscan.more()) {
            uint32_t s = qscan.number(), t = qscan.number();
            if (s >= n || t >= n) throw std::runtime_error("query outside graph");
            queries.emplace_back(s, t);
        }
        threads = static_cast<unsigned>(std::min<size_t>(threads, queries.size()));
        std::vector<int64_t> answers(queries.size(), -1);
        auto primary_forward = std::make_unique<std::atomic<uint64_t>[]>(n);
        auto primary_backward = std::make_unique<std::atomic<uint64_t>[]>(n);
        std::atomic<size_t> next{0};
        auto worker = [&] {
            constexpr uint64_t infinity = UINT64_MAX;
            SharedDistances forward(primary_forward.get()), backward(primary_backward.get());
            RadixHeap forward_heap, backward_heap;
            for (;;) {
                size_t query = next.fetch_add(1, std::memory_order_relaxed);
                if (query >= queries.size()) return;
                auto [source, target] = queries[query];
                if (source == target) { answers[query] = 0; continue; }
                if (offsets[source] == offsets[source + 1] || reverse_offsets[target] == reverse_offsets[target + 1]) continue;
                forward.reset(query); backward.reset(query); forward_heap.clear(); backward_heap.clear();
                forward.improve(source, 0); backward.improve(target, 0);
                forward_heap.push({0, source}); backward_heap.push({0, target});
                uint64_t best = infinity;
                while (!forward_heap.empty() && !backward_heap.empty()) {
                    if (best != infinity && forward_heap.minimum() + backward_heap.minimum() >= best) break;
                    // Balance frontier work rather than absolute distances: no-in sources have huge initial weights.
                    bool from_source = forward_heap.count <= backward_heap.count;
                    auto& heap = from_source ? forward_heap : backward_heap;
                    auto& own = from_source ? forward : backward;
                    auto& other = from_source ? backward : forward;
                    const auto& starts = from_source ? offsets : reverse_offsets;
                    const auto& adjacency = from_source ? edges : reverse_edges;
                    auto [d, u] = heap.pop();
                    if (d != own.get(u)) continue;
                    for (uint32_t i = starts[u]; i < starts[u + 1]; ++i) {
                        Edge edge = adjacency[i];
                        uint32_t destination = edge.to;
                        uint32_t weight = edge.weight == UINT16_MAX ? wide_weights.at(i * 2 + (from_source ? 0 : 1)) : edge.weight;
                        uint64_t candidate = d + weight;
                        if (own.improve(destination, candidate)) {
                            heap.push({candidate, destination});
                            uint64_t opposite = other.get(destination);
                            if (opposite != infinity) best = std::min(best, candidate + opposite);
                        }
                    }
                }
                if (best != infinity) answers[query] = static_cast<int64_t>(best);
            }
        };
        if (threads) parallel(threads, [&](unsigned) { worker(); });
        Output output;
        for (int64_t answer : answers) { output.number(answer); output.text("\n"); }
        output.save(paths.out / "distances.txt");
    } catch (const std::exception& e) {
        std::fprintf(stderr, "track-d: %s\n", e.what());
        return 1;
    }
}
