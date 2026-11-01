# Track C — exact CSV join

C++20, no additional runtime dependencies. Build with the pinned offline Dockerfile. Run with no arguments for `/data` and `/out`, or use `--data`/`--out` for development. The only output is `aggregates.txt`.

The parser follows the full byte-oriented CSV contract: quoting/doubled quotes, embedded newlines, BOMs only at record boundaries, mixed line endings, empty values and final EOF. Money uses exact integer cents. Region lookup has a narrow fast representation only when every country/sentinel fits, with the complete country-width fallback retained.

An exact local synchronization proof selects true record boundaries. Reader workers parse rows once and compute ordinary aggregates privately. Bounded512-event SPSC queues transfer name/country events to private hash-shard owners; full key equality and exact country bitmaps count distinct names. Canonical interior CSV bytes form an injective key encoding; decoded byte lengths remain exact. Events borrow the still-mapped immutable input. Ordered empty batches finish each stream, and exceptions cancel the pipeline. Candidate212 sets only the final container's default to6 workers (4 readers plus2 owners); native CLI fallback and build-time PGO remain12 (8 readers plus4 owners). `SPEED_DEMON_THREADS=1..12` overrides either default, with a direct private-table path for one worker. This target-specific concurrency trial is unconfirmed until its real total-K record is evaluated.

No input seed or answer is recognized. All output is computed in the timed run. See `PERF.md` for actual experiments, source/memory costs, independent tests and real board outcomes.

Owner table entries use a32-bit rejection fingerprint and a32-bit stable-block word index. Full length/byte equality still decides names, including collisions; the complete64-bit hash routes owners.64KiB word blocks and dedicated oversized-key blocks retain exact name bytes/country words with checked index arithmetic.
