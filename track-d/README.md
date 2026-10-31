# Track D: exact bidirectional shortest paths

Read `/data/graph.txt` and `/data/queries.txt`; write exactly `/out/distances.txt`. Local `--data` and `--out` options are supported. Standard C++20/OS facilities only. `SPEED_DEMON_THREADS=1` through `12` selects query workers; default6, based on prior real-board comparisons.

Up to4 workers count outgoing and incoming degrees in newline-aligned chunks. Atomic references increment shared degree arrays, avoiding one full pair of arrays per loader. After joining, prefix sums create forward and reverse CSR offsets. A second parallel parse claims disjoint edge slots with atomic cursors. All cursors are freed before searches. Duplicates, parallel edges, zero weights, and self-loops are preserved. No-out sources and no-in targets permit exact early rejection.

Each edge stores a uint32 destination and uint16 weight. Sentinel65535 redirects to a full uint32 weight table keyed by edge index and direction. This is lossless across the complete specified weight range. Sums are uint64.

Queries use bidirectional label correction with radix queues grouped into128-distance bands. Every queued entry retains its exact uint64 distance; banding changes only processing order. Eight entries from one current band are prefetched and processed together. Labels improved within the same band are requeued and can be processed again; no settled flag suppresses those improvements. Stale labels are checked immediately before expansion, including after earlier batch items may have improved them.

Queue sizes choose the expansion direction. Meeting paths give actual path-length upper bounds. A queue minimum is the lower boundary of its earliest nonempty band, so adding both minima gives a conservative stopping bound. Stopping is checked only between fully processed batches. Work below each boundary has been exhausted, and nonnegative weights cannot create a lower band. Lowering the bound can require extra work but cannot justify an early stop. Compact entries hold uint32 distances and nodes in one uint64; larger distances use an exact full-width queue. Neither stored labels nor answers are rounded.

Each worker owns its two distance maps. Ordinary labels pack node+1 and uint32 distance into uint64 slots with exact node comparison, linear probing, and growth below50% occupancy. Touched slots are cleared between queries; rehashing updates the touched-slot list. Large distances and the UINT32_MAX node key use an exact uint64 fallback map. A smaller label can migrate from fallback into compact storage without losing its value. There is no approximate distance, node-count cutoff, or shared query-label overwrite.

An atomic job index assigns each query once. Each answer has one writer; final output preserves input query order. Unreachable pairs emit`-1`; source=target emits0. Graph storage is O(nodes+edges), and query workspaces scale with explored frontiers. Loading, allocation/reset, queries, and output are all timed.

Verification includes independent all-pairs Floyd–Warshall graphs, weight boundaries65534/65535/65536/MAX, a20,000-node chain with 64-bit paths and workspace growth, multiple untrained generator seeds, published full hashes at1/6/12 workers, address/UB and race sanitizers, independent queue/map models, bounded parser guard-page tests, and offline restricted GCC15 Linux builds. See `PERF.md` and `../docs/round2-*`.

With another24 hours: use real Intel phase profiles to compare cache layouts and compiler-guided training on independent synthetic seeds. Keep only observed total-score gains, with exact fallback behavior tested.

Specification: https://github.com/hackathon-raptors/speed-demon-2026/blob/main/specs/d-traverse.md

The Docker build retains profile-guided compilation after a real-board gain. `training_generator.py` is byte-identical to the official generator; it creates two independent sample seeds inside the offline build. GCC collects execution profiles, then recompiles without runtime instrumentation. The final stage copies only the executable. The published rules explicitly permit this training and exclude unchanged official generator copies from S. All untrained/full-output checks still apply; PERF.md distinguishes experiments from confirmed gains.
