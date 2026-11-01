#include "radix_heap.hpp"
#include "edge_store.hpp"
#include "load_cursors.hpp"
#include "io.hpp"
#include "decimal.hpp"
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
        uint64_t value = decimal_digits(p, end);
        if (value > UINT32_MAX) throw std::runtime_error("graph integer out of range");
        return static_cast<uint32_t>(value);
    }
};
using Item = std::pair<uint64_t, uint32_t>;

int main(int argc, char** argv) {
    try {
        Paths paths(argc, argv);
        unsigned threads = 12;
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
        unsigned loaders = std::min(threads, 12U);
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
        struct Local { size_t count = 0; DegreeBytes::Spills out_spills, in_spills; std::vector<std::pair<uint32_t, uint32_t>> wide; };
        std::vector<Local> locals(loaders);
        DegreeBytes degree(n), reverse_degree(n);
        parallel(loaders, [&](unsigned worker) {
            auto& local = locals[worker];
            Scanner input{boundaries[worker], boundaries[worker + 1]};
            std::array<std::pair<uint32_t,uint32_t>, 16> batch;
            while (input.more()) {
                size_t count = 0;
                while (count < batch.size() && input.more()) {
                    uint32_t u = input.number(), v = input.number(); input.number();
                    if (u >= n || v >= n) throw std::runtime_error("node outside graph");
                    __builtin_prefetch(&degree.values[u], 1, 1); __builtin_prefetch(&reverse_degree.values[v], 1, 1);
                    batch[count++] = {u,v};
                }
                local.count += count;
                for (size_t i=0;i<count;++i) { auto [u,v]=batch[i]; degree.add(u, local.out_spills); reverse_degree.add(v, local.in_spills); }
            }
        });
        size_t edge_count = 0;
        for (const auto& local : locals) edge_count += local.count;
        if (edge_count != m) throw std::runtime_error("edge count does not match header");
        std::vector<uint32_t> offsets(size_t(n) + 1), reverse_offsets(size_t(n) + 1);
        for (const auto& local : locals) {
            for (auto [node, count] : local.out_spills) offsets[size_t(node) + 1] += count;
            for (auto [node, count] : local.in_spills) reverse_offsets[size_t(node) + 1] += count;
        }
        for (size_t i = 1; i <= n; ++i) {
            offsets[i] += offsets[i - 1] + degree.values[i - 1];
            reverse_offsets[i] += reverse_offsets[i - 1] + reverse_degree.values[i - 1];
        }
        degree.release(); reverse_degree.release();
        SharedCursor cursor(offsets), reverse_cursor(reverse_offsets);
        bool wide_cursors = cursor.wide_blocks || reverse_cursor.wide_blocks;
        EdgeStore edges(m, n), reverse_edges(m, n);
        auto scatter = [&]<bool Compact, bool WideCursors>() {
            parallel(loaders, [&](unsigned worker) {
            auto& local = locals[worker];
            Scanner input{boundaries[worker], boundaries[worker + 1]};
            struct Row { uint32_t u, v, value, out, in; };
            std::array<Row, 16> batch;
            while (input.more()) {
                size_t count = 0;
                while (count < batch.size() && input.more()) {
                    auto& row = batch[count++]; row.u=input.number(); row.v=input.number(); row.value=input.number();
                    cursor.template prefetch<WideCursors>(row.u); reverse_cursor.template prefetch<WideCursors>(row.v);
                }
                for (size_t i=0;i<count;++i) {
                    auto& row=batch[i]; row.out=cursor.template take<WideCursors>(row.u); row.in=reverse_cursor.template take<WideCursors>(row.v);
                    edges.template prefetch<Compact,true>(row.out); reverse_edges.template prefetch<Compact,true>(row.in);
                }
                for (size_t i=0;i<count;++i) {
                    auto& row=batch[i]; uint32_t weight=std::min(row.value, Compact ? EdgeStore::small_limit : uint32_t(UINT16_MAX));
                    edges.set<Compact>(row.out,row.v,weight); reverse_edges.set<Compact>(row.in,row.u,weight);
                    if(row.value >= (Compact ? EdgeStore::small_limit : uint32_t(UINT16_MAX))) { local.wide.emplace_back(row.out*2,row.value); local.wide.emplace_back(row.in*2+1,row.value); }
                }
            }
        });
        };
        if (edges.compact) {
            if (wide_cursors) scatter.template operator()<true,true>(); else scatter.template operator()<true,false>();
        } else {
            if (wide_cursors) scatter.template operator()<false,true>(); else scatter.template operator()<false,false>();
        }
        std::unordered_map<uint32_t, uint32_t> wide_weights;
        for (const auto& local : locals) for (auto [index, weight] : local.wide) wide_weights.emplace(index, weight);
        locals.clear(); cursor.release(); reverse_cursor.release();
        Scanner qscan{queries_file.data, queries_file.data + queries_file.size};
        std::vector<std::pair<uint32_t, uint32_t>> queries;
        while (qscan.more()) {
            uint32_t s = qscan.number(), t = qscan.number();
            if (s >= n || t >= n) throw std::runtime_error("query outside graph");
            queries.emplace_back(s, t);
        }
        threads = static_cast<unsigned>(std::min<size_t>(threads, queries.size()));
        std::vector<int64_t> answers(queries.size(), -1);
        std::atomic<size_t> next{0};
        auto worker = [&]<bool Compact>() {
            constexpr uint64_t infinity = UINT64_MAX;
            FastDistances forward, backward;
            RadixHeap forward_heap, backward_heap;
            for (;;) {
                size_t query = next.fetch_add(1, std::memory_order_relaxed);
                if (query >= queries.size()) return;
                auto [source, target] = queries[query];
                if (source == target) { answers[query] = 0; continue; }
                if (offsets[source] == offsets[source + 1] || reverse_offsets[target] == reverse_offsets[target + 1]) continue;
                forward.reset(); backward.reset(); forward_heap.clear(); backward_heap.clear();
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
                    std::array<Item, 32> work;
                    std::array<std::pair<uint32_t, uint32_t>, 32> ranges;
                    size_t count = heap.pop_batch(work.data(), work.size());
                    for (size_t k = 0; k < count; ++k) __builtin_prefetch(&starts[work[k].second], 0, 1);
                    for (size_t k = 0; k < count; ++k) {
                        uint32_t node = work[k].second;
                        ranges[k] = {starts[node], starts[node + 1]};
                        if (ranges[k].first < ranges[k].second) adjacency.template prefetch<Compact>(ranges[k].first);
                    }
                    for (size_t k = 0; k < count; ++k) {
                        auto [d, u] = work[k];
                        if (d != own.get(u)) continue; // Earlier items may improve this label within the band.
                        for (uint32_t i = ranges[k].first; i < ranges[k].second; ++i) {
                            auto [destination, tag] = adjacency.template get<Compact>(i);
                            uint32_t weight = tag == (Compact ? EdgeStore::small_limit : uint32_t(UINT16_MAX)) ? wide_weights.at(i * 2 + (from_source ? 0 : 1)) : tag;
                            uint64_t candidate = d + weight;
                            if (candidate >= best) continue;
                            if (own.improve(destination, candidate)) {
                                heap.push({candidate, destination});
                                uint64_t opposite = other.get(destination);
                                if (opposite != infinity) best = std::min(best, candidate + opposite);
                            }
                        }
                    }
                }
                if (best != infinity) answers[query] = static_cast<int64_t>(best);
            }
        };
        if (threads) {
            if (edges.compact) parallel(threads, [&](unsigned) { worker.template operator()<true>(); });
            else parallel(threads, [&](unsigned) { worker.template operator()<false>(); });
        }
        Output output;
        for (int64_t answer : answers) { output.number(answer); output.text("\n"); }
        output.save(paths.out / "distances.txt");
    } catch (const std::exception& e) {
        std::fprintf(stderr, "track-d: %s\n", e.what());
        return 1;
    }
}
