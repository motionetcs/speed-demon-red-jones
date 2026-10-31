# Track D: compact directed shortest paths

Read `/data/graph.txt` and `/data/queries.txt`; write only `/out/distances.txt`. Local `--data` and `--out` options are supported. No extra runtime dependencies. `SPEED_DEMON_THREADS=1` through `12` selects workers; the default is six.

Two passes over the graph build compressed outgoing adjacency arrays without retaining an extra edge-tuple array. All directed edges are preserved, including parallel edges, exact duplicates, zero weights, and self-loops. A compact incoming-edge flag permits a sound early rejection of a distinct target with no in-edges. A source with no outgoing edges is also unreachable unless source equals target.

Each worker runs exact forward Dijkstra with uint64 distances. Its monotone radix heap groups keys by the highest bit differing from the last popped distance. All inserted candidates are at least that last distance because weights are non-negative. When bucket zero is empty, the next bucket is rebased to its minimum key and redistributed into lower buckets. Zero-weight edges and repeated keys are valid. Stale queue entries are ignored.

Workers reuse distance arrays and reset only touched nodes between searches. Query jobs use an atomic index; each answer has one writer, and output follows the original query order. The result is `-1` for unreachable nodes and can exceed uint32 for reachable paths.

Graph storage is O(nodes + edges); distance workspace is O(nodes * workers), plus frontier storage. On the public full graph, six workers were faster than three locally at a higher process RSS. The actual board's cgroup counter and CPU may favor a different worker count, so retain the configurable option. Preprocessing, both parse passes, searches, and writing all occur within the timed process.

Build: `clang++ -std=c++20 -O3 -pthread main.cpp -o solution`. The Dockerfile includes the radix header and builds independently/offline. Verification includes independent Floyd–Warshall comparisons for all pairs on 12 random small graphs, the official example, generated seeds, and full public output hashes. Next useful experiments are board-measured worker counts and forward versus bidirectional storage, with complete correctness checks before adoption.

Specification: https://github.com/hackathon-raptors/speed-demon-2026/blob/main/specs/d-traverse.md
