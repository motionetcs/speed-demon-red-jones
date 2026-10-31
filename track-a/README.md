# Track A: exact hourly log aggregation

Read `/data/requests.log`; write exactly `/out/summary.txt`. Local `--data` and `--out` options are supported. No extra runtime dependencies. `SPEED_DEMON_THREADS=1` through `12` selects workers; twelve is the default.

A parallel newline-aligned prepass reads timestamps and stores input-derived line offsets by full UTC hour. The 72-hour range and ASCII timestamp format come from the frozen specification. Offsets are uint32 because the published full-scale input is below 4 GB; a larger file is rejected explicitly. All offsets are computed anew during the timed run, with no stored input catalog or answers.

A worker owns one complete hour at a time. It parses endpoints, status, and exact uint32 latencies into a reusable small workspace. Local endpoint interning checks complete byte equality and grows its flat table. Counts and errors are exact. Prefix offsets scatter that hour's latency values into contiguous per-endpoint ranges. Groups below64 items are sorted; larger groups use progressively restricted exact nearest-rank selections. The zero-based rank is `(p*n+99)/100-1`. Duplicate requests count twice, and 500 through599 count as errors; integer arithmetic computes parts per million.

Only one worker reads or releases each hour's line-offset vectors. Releasing them after use bounds live temporary storage instead of retaining all requests and all worker/hour groups together. Per-worker endpoint catalogs and allocations are reused across hours. String views refer to the immutable mapping, which outlives every worker. Output is formatted into separate hour buffers, with endpoints in byte order, then written in UTC-hour order.

Work is O(input bytes + requests), plus exact selection and small-group sorting. Storage is O(line offsets + live hourly workspaces + output). Thread exceptions are joined and propagated. Four ASCII digits can be parsed in one bounded integer load after validating every byte; scalar handling covers tails and non-little-endian hosts. No approximation is used.

Build: `clang++ -std=c++20 -O3 -pthread main.cpp -o solution`. Docker independently builds a static Linux executable offline from pinned allowlisted images. New-seed examples, rank boundaries, empty input, growth beyond2500 endpoints, full published hashes, memory/UB and race sanitizers, and Linux checks pass. See `PERF.md` and `../docs/round2-ac-*.json`; local timing is not an official score.

With another24 hours: profile the retained layout on Intel, compare bounded load/formatting paths, and test any compiler-guided tuning on independent generator seeds before board submission.

Specification: https://github.com/hackathon-raptors/speed-demon-2026/blob/main/specs/a-ingest.md

Profile-guided compilation on the stronger hour-owned algorithm is retained after a real-board gain. The byte-identical official generator trains two independent sample seeds104729/130363 inside an offline builder. Only the executable is copied into the final image; all answers are recomputed at runtime. Prior PGO comparisons also carried rejected allocator/delimiter changes, so they do not establish the effect on this restored algorithm. The exact board result is recorded in PERF.md.
