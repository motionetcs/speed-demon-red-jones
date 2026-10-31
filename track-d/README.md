# Track D: exact bidirectional shortest paths

Read `/data/graph.txt` and `/data/queries.txt`; write only `/out/distances.txt`. Local `--data` and `--out` options are supported. No extra runtime dependencies. `SPEED_DEMON_THREADS=1` through `12` selects query workers; the default is six.

Up to four workers parse newline-aligned graph chunks into local degree counts. Prefix offsets assign disjoint scatter ranges for forward and reverse compressed adjacency arrays. A second parallel parse fills those ranges directly, avoiding a retained edge-tuple array. Degree/cursor buffers are released before query processing. All directed edges are preserved, including duplicates, zero weights, and self-loops. Sources with no outgoing edges and targets with no incoming edges permit exact early rejection.

Each packed adjacency entry has a uint32 destination and uint16 weight. The sentinel 65535 redirects to an exact uint32 weight table keyed by edge index and direction. This is lossless for every valid weight; it does not assume that all weights are small. Path sums remain uint64.

Queries run exact bidirectional Dijkstra using monotone radix heaps. Frontier queue sizes choose the expansion direction. Complete path candidates update the best distance; the sum of minimum frontier keys supplies the termination bound. Stale queue entries are ignored. Zero weights and repeated keys remain valid.

Two shared atomic label arrays provide compact primary storage. A unique query token owns each claimed cell until that query resets or finishes. Overlapping queries and distances at least UINT32_MAX use private, dynamically growing epoch-stamped exact maps. Workers cannot overwrite another active query's labels. Claimed cells are released exactly once; per-query fallback maps reuse allocation. Exceptions are joined and propagated.

An atomic job index assigns each query once. Each answer has one writer, and output follows original query order. Unreachable results are `-1`; reachable results can exceed uint32. Graph and shared label storage are O(nodes + edges); private fallback and heap storage scale with explored frontiers. Parsing, preprocessing, searches, cleanup, and output all occur within the timed process.

Build: `clang++ -std=c++20 -O3 -pthread main.cpp -o solution`. The Dockerfile includes all headers and builds offline. Verification includes independent Floyd–Warshall comparisons for all pairs on 12 random graphs, weight boundaries 65534/65535/65536/MAX, a 20,000-node chain with over-32-bit paths, generated independent seeds, and full public hashes. Address/undefined-behavior and thread sanitizers pass; the offline GCC15 Linux container also passes. Actual board results are recorded in `PERF.md`.

Specification: https://github.com/hackathon-raptors/speed-demon-2026/blob/main/specs/d-traverse.md
