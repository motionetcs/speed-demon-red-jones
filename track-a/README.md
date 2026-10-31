# Track A: exact hourly log aggregation

Read `/data/requests.log`; write only `/out/summary.txt`. Development `--data`/`--out` options are supported. Standard C++20/OS facilities only. `SPEED_DEMON_THREADS=1` through `12`; default12.

Newline-aligned workers parse each timestamp, endpoint, status and exact uint32 latency once. The frozen specification supplies the72-hour range and timestamp grammar. An exact shared endpoint dictionary assigns input-derived IDs. Its hash fingerprint only chooses candidates: complete byte equality resolves every collision. Release/acquire publication prevents readers from seeing incomplete entries. The specified endpoint catalogue contains1,842 names; the representation supports4,096 IDs and rejects overflow explicitly.

Each request becomes one four-byte record:12 endpoint-ID bits,1 error bit and19 latency-tag bits. The all-ones latency tag consumes a full uint32 latency from that worker/hour's side vector. Values equal to the sentinel, larger values and MAX_UINT32 all retain their exact values. Duplicate requests remain separate records. Only hour vectors that receive a record reserve space. The input mapping outlives every endpoint view; dictionary metadata can be released once those views have been copied.

A worker then owns a complete hour. It counts each endpoint and its errors, computes prefix offsets, and scatters exact latencies into contiguous ranges. Small groups are sorted; larger groups use progressively restricted exact nearest-rank selections. The zero-based rank is `(p*n+99)/100-1`. HTTP500 through599 are errors; integer arithmetic computes parts per million exactly. No quantile is approximated.

Only the owner of an hour reads or releases that hour's record/escape vectors. Worker-private counts, offsets, cursors and latency buffers are reused across hours. Output is formatted into independent hour buffers, endpoints sorted by complete bytes, then written in UTC-hour order. Input order does not affect grouping. A file above4GB is rejected before converting its first-line positions to uint32.

Work is O(input bytes + requests), plus exact selection/small-group sorting and key ordering. Storage is O(compact request records + exact escapes + live hourly workspaces + output). Thread exceptions are joined and propagated. The bounded decimal helper validates every digit; scalar tails cover short and non-little-endian inputs.

Build: `clang++ -std=c++20 -O3 -pthread main.cpp -o solution`. Docker builds a static Linux executable offline from pinned allowlisted images. The unchanged official generator trains independent sample seeds104729/130363 for PGO. Only the executable enters the runtime image; no dataset, profile or answer cache does.

Validation covers untrained samples, full published hashes at1/6/12 workers, strict memory/UB and race sanitizers, deliberate full-hash collisions, unique IDs, ID4095/overflow, exact latency escapes, and restricted GCC15/Linux cases/defaults. Exact scored commit/run IDs and rejected experiments are in `PERF.md`. Local Apple timing is development evidence; real board K decides retention.

With another24 hours: obtain legitimate Intel profiles, measure parse/selection/output phases, and test changes against independent seeds before board promotion.

Specification: https://github.com/hackathon-raptors/speed-demon-2026/blob/main/specs/a-ingest.md
