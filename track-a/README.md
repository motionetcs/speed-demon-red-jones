# Track A: exact hourly log aggregation

Read `/data/requests.log`; write only `/out/summary.txt`. Local `--data` and `--out` options are supported. No extra runtime dependencies.

Workers parse disjoint newline-aligned input chunks and intern exact endpoint bytes in local flat hash tables. Bounded delimiter search finds each endpoint, and the uint32 latency is parsed while consuming its digits rather than scanning it twice. Counts and errors are reduced by full UTC hour and endpoint. Prefix offsets give every worker a disjoint slice of a contiguous latency array, so scattering needs no shared increments or locks. All 72 buckets remain available because requests arrive out of order. The fixed date span and ASCII field format are specified by the organizers, not inferred from seed 1.

Workers process disjoint groups and format separate hourly output buffers. Groups below 64 items are sorted; larger groups use three progressively restricted exact selections, preserving earlier selected ranks. Nearest-rank percentiles use `(p*n+99)/100-1` as a zero-based index. Error counts include 500 through 599 and use 64-bit integer multiplication for parts per million. Duplicated lines count twice. The main thread writes hourly buffers in order, with byte-sorted endpoints. `SPEED_DEMON_THREADS=1` through `12` controls parallelism. Twelve is the default: the six-worker board experiment used less memory but had a slightly lower measured K.

Storage is O(requests + workers*endpoints*72); small-group sorting and average-linear exact rank selection add work proportional to group sizes. Temporary packed records and local tables are released before formatting. Endpoint string views remain valid while the mapping exists. Worker exceptions are joined and propagated to the main thread; invalid/truncated fields produce a nonzero exit on stderr.

Build: `clang++ -std=c++20 -O3 -pthread main.cpp -o solution`. The Dockerfile independently compiles a static Linux executable offline from the official allowlist.

Verification includes official worked/edge cases, 101-request rank boundaries, empty input, multiple generated seeds, and published full data. See `../docs/validation-*.json` and `PERF.md` for actual results. The original serial-layout selection experiment was slower on samples. Selection was retested after the contiguous parallel layout change: seven alternating full-data trials favored it by about 6% locally at twelve workers. The real board run `run-3e1350a66528` scored K=20.449888 versus sorting K=19.908239, so this layout retains selection. The later direct parser scored K=21.467492 in `run-bbd53e3cc9e6` and is retained.

Specification: https://github.com/hackathon-raptors/speed-demon-2026/blob/main/specs/a-ingest.md
