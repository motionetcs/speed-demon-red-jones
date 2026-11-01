# Track C — exact CSV join

C++20, no additional runtime dependencies. Build with the pinned offline Dockerfile. Run with no arguments for `/data` and `/out`, or use `--data`/`--out` for development. The only output is `aggregates.txt`.

The parser follows the full byte-oriented CSV contract: quoting/doubled quotes, embedded newlines, BOMs only at record boundaries, mixed line endings, empty values and final EOF. Money uses exact integer cents. Region lookup has a narrow fast representation only when every country/sentinel fits, with the complete country-width fallback retained.

An exact local synchronization proof selects true record boundaries. Reader workers parse rows once and compute ordinary aggregates privately. Bounded512-event SPSC queues transfer name/country events to private hash-shard owners; full key equality and exact country bitmaps count distinct names. Canonical interior CSV bytes form an injective key encoding; decoded byte lengths remain exact. Events borrow the still-mapped immutable input. Ordered empty batches finish each stream, and exceptions cancel the pipeline. The default is8 readers plus4 owners,12 total workers; `SPEED_DEMON_THREADS=1..12` preserves that requested total, with a direct private-table path for one worker.

No input seed or answer is recognized. All output is computed in the timed run. See `PERF.md` for actual experiments, source/memory costs, independent tests and real board outcomes.

Owner table entries use a32-bit rejection fingerprint and a32-bit stable-block word index. Full length/byte equality still decides names, including collisions; the complete64-bit hash routes owners.64KiB word blocks and dedicated oversized-key blocks retain exact name bytes/country words with checked index arithmetic.

Candidate274 computes the same complete64-bit name hash, chooses the private owner from its upper32 bits, and keeps the existing lower32 table fingerprint and full-key equality. This separates routing bits from table placement without assuming collision freedom or changing the CSV grammar. All requested worker counts retain consistent ownership; one worker stays direct. Two pre-existing same-line queue statements are split for strict compiler clarity. Fresh native routing/collision/reference/race and exact current GCC/image/default checks pass; only a real total-K gain permits retention.
