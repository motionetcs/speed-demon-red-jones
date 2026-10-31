# Track A: exact hourly log aggregation

Read `/data/requests.log`; write only `/out/summary.txt`. Local `--data` and `--out` options are supported. No extra runtime dependencies.

The parser uses a read-only memory map, ignores the HTTP method, interns exact endpoint bytes, and places each latency in its full UTC-hour bucket. All 72 buckets remain available because requests arrive out of order. The fixed date span and ASCII field format are specified by the organizers, not inferred from seed 1.

Each nonempty group's uint32 latencies are sorted. Nearest-rank percentiles use `(p*n+99)/100-1` as a zero-based index. Error counts include 500 through 599 and use 64-bit integer multiplication for parts per million. Duplicated lines count twice. Output iterates hours and byte-sorted endpoints.

Storage is O(requests + endpoints*72); comparisons across latency groups total at most O(requests*log(requests)). Endpoint string views remain valid while the mapping exists. Invalid/truncated fields produce a nonzero exit on stderr.

Build: `clang++ -std=c++20 -O3 -pthread main.cpp -o solution`. The Dockerfile independently compiles a static Linux executable offline from the official allowlist.

Verification includes official worked/edge cases, 101-request rank boundaries, empty input, multiple generated seeds, and published full data. See `../docs/validation-*.json` and `PERF.md` for actual results. The next optimization decision should come from profiling the full run on the board; the local selection experiment was slower and was rejected.

Specification: https://github.com/hackathon-raptors/speed-demon-2026/blob/main/specs/a-ingest.md
