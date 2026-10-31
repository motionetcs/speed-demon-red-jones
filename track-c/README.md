# Track C — exact CSV join

C++20, no additional runtime dependencies. Build with the pinned offline Dockerfile. Run with no arguments for `/data` and `/out`, or use `--data`/`--out` for development. The only output is `aggregates.txt`.

The parser follows the full byte-oriented CSV contract: quoting/doubled quotes, embedded newlines, BOMs only at record boundaries, mixed line endings, empty values and final EOF. Money uses exact integer cents. Region lookup has a narrow fast representation only when every country/sentinel fits, with the complete country-width fallback retained.

An exact local synchronization proof selects true record boundaries. Every requested worker parses one partition and owns one exact name shard. Its own names update directly; other names use64-event SPSC batches. Full key equality and exact country words count distinct canonical CSV names. Events borrow the still-mapped immutable input; decoded byte lengths remain exact. A sender blocked on a full outgoing queue consumes its incoming work, and also checks incoming queues after64 rows. Consumption never sends. Partial data precedes one empty EOF per peer; each worker drains all incoming EOFs before exiting. Exceptions cancel waits, and the single-worker path is direct. `SPEED_DEMON_THREADS=1..12` preserves that total.

No input seed or answer is recognized. All output is computed in the timed run. See `PERF.md` for actual experiments, source/memory costs, independent tests and real board outcomes.

Owner table entries use a32-bit rejection fingerprint and a32-bit stable-block word index. Full length/byte equality still decides names, including collisions; the complete64-bit hash routes owners.64KiB word blocks and dedicated oversized-key blocks retain exact name bytes/country words with checked index arithmetic.
