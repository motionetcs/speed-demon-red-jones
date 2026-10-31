# Track A: exact count/scatter log aggregation

Read `/data/requests.log`; write only `/out/summary.txt`. Local `--data`/`--out` options are supported. Standard C++20/OS only. `SPEED_DEMON_THREADS=1` through `12`; default12. The fixed72-hour UTC range and timestamp format come from the frozen task, not an input-specific answer catalog.

The first newline-aligned parallel pass parses hours, endpoints and status. A shared exact endpoint table assigns IDs using full hashes and byte equality. It starts with capacity2048 and doubles/reparses if necessary; no endpoint is dropped. Endpoint views refer to the immutable input mapping. Release/acquire publication protects each completed ID/view. Workers keep independent four-byte count cells per hour/endpoint: uint16 count plus uint16 error count. Every wrap adds65536 to an exact spill map. Duplicates count separately; statuses500 through599 count as errors.

After joining, exact totals and prefix ranges are computed. Each four-byte count cell becomes its worker's uint32 scatter cursor; the active union member changes only after its counts have been consumed. A second timed parse reads latencies and scatters each uint32 value once into disjoint ranges of one contiguous array. Prefix conservation proves complete, non-overlapping coverage. Count/cursor cells and spill maps are released before selection/output. Total request count is checked against the uint32 cursor range before allocation.

Workers own complete hours for percentile selection and formatting. Groups below64 values are sorted; larger groups use progressively restricted exact nearest-rank selection. The zero-based rank is `(p*n+99)/100-1`. Integer arithmetic computes errors per million. Endpoints are byte-sorted; hour labels are derived from actual input records.

Each worker reuses one hour buffer. Atomic tokens allow exactly the next UTC hour to write, so the program holds at most one pending buffer per worker rather than all72 hours of output. A token is waiting, permitted or cancelled; a normal compare/exchange handoff cannot overwrite cancellation. Failure wakes every waiting writer, joins workers and returns nonzero. The output stream has one writer at a time, with release/acquire ordering between writers.

Work is O(input bytes + requests + count cells), plus exact selection and output sorting. Storage is O(count cells + latencies + actual endpoints + bounded hour buffers), with spill storage only for large local counts. There is no line-offset index, stored eight-byte request record, precomputed dictionary or approximate percentile.

Docker builds offline from pinned allowlisted GCC15/Debian images. Sample104729/130363 generator output trains compilation in builder stages; only the executable enters runtime. Validation includes official examples, new independent seeds, exact full hashes at1/6/12 workers, endpoint growth, empty input, percentile ranks,65535/65536/140000 count/error cases, address/UB and race sanitizers, a four-thread std::map model, and restricted Linux runs. A Linux output-failure integration check confirms cancellation without deadlock. See `PERF.md` and `../docs/round8-*` for evidence and the board decision.

This is a memory/runtime tradeoff candidate. Local Apple ARM timing is slower despite lower RSS; actual board K decides retention. With another24 hours: profile parsing, count merging and output on Intel and retain only measured overall gains.

Specification: https://github.com/hackathon-raptors/speed-demon-2026/blob/main/specs/a-ingest.md
