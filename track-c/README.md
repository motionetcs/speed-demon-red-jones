# Track C: exact canonical CSV join

C++20 and standard-library/OS facilities only. Build offline with the pinned Dockerfile. Defaults read `/data/regions.csv` and `/data/records.csv` and write exactly `/out/aggregates.txt`; development `--data`/`--out` options remain. `SPEED_DEMON_THREADS=1..12`, default12.

The byte parser preserves quoting, doubled quotes, embedded newlines, BOM placement, CRLF/LF/EOF, trailing spaces, exact decoded byte lengths and signed integer cents. True record-boundary synchronization partitions the immutable input. All requested workers parse records and update private country aggregates. Region storage narrows only when every country and unmatched sentinel fits; complete wider-country support remains.

Names use canonical raw CSV interiors. Doubling literal quotes is injective, and legal unquoted fields have no quote, so quoted/unquoted empty and plain values compare correctly. Every hash collision still requires complete key-byte equality. No input seed or saved answer is recognized.

A shared exact name table removes event queues. A successful slot CAS owns initialization; the writer creates a stable key and actual atomic country words in its worker-owned arena, then release-publishes the full hash. Readers acquire publication before touching the key. An atomic country-bit OR returns true to exactly one worker for each name/country pair. All arenas remain alive until workers join.

The initial131072-slot table is a sizing choice, not a key-count bound. On capacity pressure, workers cancel promptly, join, discard that attempt's private aggregates, double safely and reparse. Actual parser/allocation errors propagate normally and are not mistaken for capacity retries. No partial attempt is reduced into final totals.

The earlier bounded owner pipeline and all rejected changes remain in PERF.md. Fresh untrained/reference, sanitizer/race, full country-width, deliberate collision/publication,120k-key retry, malformed cancellation, current-image Linux and actual-default evidence are tied in round89-candidate-source-match.json. Local Apple measurements are hypotheses; only actual board K decides retention.
