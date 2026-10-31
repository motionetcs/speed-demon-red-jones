# Track A: exact hourly log aggregation

Read `/data/requests.log`; write only `/out/summary.txt`. Local `--data` and `--out` options are supported. No extra runtime dependencies.

Workers parse disjoint newline-aligned input chunks and intern exact endpoint bytes in local flat hash tables. Counts and errors are reduced by full UTC hour and endpoint. Prefix offsets give every worker a disjoint slice of a contiguous latency array, so scattering needs no shared increments or locks. All 72 buckets remain available because requests arrive out of order. The fixed date span and ASCII field format are specified by the organizers, not inferred from seed 1.

Workers sort disjoint groups and format separate hourly output buffers. Nearest-rank percentiles use `(p*n+99)/100-1` as a zero-based index. Error counts include 500 through 599 and use 64-bit integer multiplication for parts per million. Duplicated lines count twice. The main thread writes hourly buffers in order, with byte-sorted endpoints. `SPEED_DEMON_THREADS=1` through `12` controls parallelism. Twelve workers passed the first parallel board experiment; the current comparison uses six.

Storage is O(requests + workers*endpoints*72); comparisons across latency groups total at most O(requests*log(requests)). Temporary packed records and local tables are released before formatting. Endpoint string views remain valid while the mapping exists. Worker exceptions are joined and propagated to the main thread; invalid/truncated fields produce a nonzero exit on stderr.

Build: `clang++ -std=c++20 -O3 -pthread main.cpp -o solution`. The Dockerfile independently compiles a static Linux executable offline from the official allowlist.

Verification includes official worked/edge cases, 101-request rank boundaries, empty input, multiple generated seeds, and published full data. See `../docs/validation-*.json` and `PERF.md` for actual results. The next optimization decision should come from profiling the full run on the board; the local selection experiment was slower and was rejected.

Specification: https://github.com/hackathon-raptors/speed-demon-2026/blob/main/specs/a-ingest.md
