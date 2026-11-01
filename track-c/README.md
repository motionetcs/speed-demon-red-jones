# Track C — exact CSV join

C++20, no additional runtime dependencies. Build with the pinned offline Dockerfile. Run with no arguments for `/data` and `/out`, or use `--data`/`--out` for development. The only output is `aggregates.txt`.

The parser follows the full byte-oriented CSV contract: quoting/doubled quotes, embedded newlines, BOMs only at record boundaries, mixed line endings, empty values and final EOF. Money uses exact integer cents. Region lookup has a narrow fast representation only when every country/sentinel fits, with the complete country-width fallback retained.

An exact local synchronization proof selects true record boundaries. Reader workers parse rows once and compute ordinary aggregates privately. Bounded512-event SPSC queues transfer name/country events to private hash-shard owners; full key equality and exact country bitmaps count distinct names. Canonical interior CSV bytes form an injective key encoding; decoded byte lengths remain exact. Events borrow the still-mapped immutable input. Ordered empty batches finish each stream, and exceptions cancel the pipeline. The default is8 readers plus4 owners,12 total workers; `SPEED_DEMON_THREADS=1..12` preserves that requested total, with a direct private-table path for one worker.

No input seed or answer is recognized. All output is computed in the timed run. See `PERF.md` for actual experiments, source/memory costs, independent tests and real board outcomes.

Owner table entries use a32-bit rejection fingerprint and a32-bit stable-block word index. Full length/byte equality still decides names, including collisions; the complete64-bit hash routes owners.64KiB word blocks and dedicated oversized-key blocks retain exact name bytes/country words with checked index arithmetic.


Candidate230 uses the fresh entry’s existing bounded8-byte decimal reducer only for the amount’s dollar digits. It retains the scalar continuation and every sign/missing-digit/dot/two-cent-digit/terminator check; integer IDs/regions remain scalar. The helper is copied into track-c and charged normally. Original12-worker runtime/full1000003+sample130363 PGO/hash/queue/country behavior stays unchanged. Native screen is a hypothesis; real total K must improve.
