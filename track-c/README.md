# Track C — exact CSV join

C++20, no additional runtime dependencies. Build with the pinned offline Dockerfile. Run with no arguments for `/data` and `/out`, or use `--data`/`--out` for development. The only output is `aggregates.txt`.

The parser follows the full byte-oriented CSV contract: quoting/doubled quotes, embedded newlines, BOMs only at record boundaries, mixed line endings, empty values and final EOF. Money uses exact integer cents. Region lookup has a narrow representation only when every country/sentinel fits, with the complete country-width fallback retained.

An exact local synchronization proof selects true record boundaries. All requested workers parse records and aggregate ordinary fields privately. A shared exact name index uses eight-byte atomic rejection-fingerprint/dense-index slots; full lengths and bytes always decide equality. Canonical interior CSV bytes form an injective key encoding; decoded lengths remain exact. Lazy blocks hold64-byte descriptors with24 inline key bytes, a complete length and four atomic country words. Longer keys are copied into stable worker-owned blocks. Extra countries use complete spill bitmaps. Atomic country-bit updates count each distinct name exactly once per country. Slots and descriptor blocks use release/acquire publication, and worker arenas remain alive through all joined accesses.

Capacity exhaustion cancels the whole attempt. After all readers join, partial aggregates and name storage are discarded and the exact parse restarts with doubled capacity. Other errors cancel peers and propagate after joining. No partial result is emitted. The default is12 readers; `SPEED_DEMON_THREADS=1..12` selects that requested total without changing the exact result.

No input seed or answer is recognized. All output is computed in the timed run. See `PERF.md` for experiments, independent tests and real board outcomes. Native screen314 used a raw allocation inserted directly into an owning vector;315 first places that allocation in a local unique pointer so vector allocation failure cannot leak it. Source-specific strict/race/image checks bind315 separately.
