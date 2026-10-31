# Rejected prototype sources

These are historical experiments, not the submitted track sources. Apply each patch to a disposable checkout of its baseline; do not apply it to the live submission merely because it passes correctness. Timings are Apple ARM development measurements, not board scores.

- `round3-private-loader.patch`: baseline `a5394d3`; compile D with ordinary release flags for four loaders, or add `-DLOADER_COUNT=2` for two. Compact degree counters and relative cursors retain exact overflow. Both variants are slower locally; rejected. Raw reports: `round3-private-d-*`.
- `round3-c-crc.patch`: baseline `d2fd0b5`; compile with `-march=armv8-a+crc` on Apple ARM or `-march=native` on x86 with SSE4.2. Exact string equality remains mandatory. It passes output tests but is slower locally; rejected. Raw reports: `round3-c-*`.
- `round2-c-private-membership.patch`: baseline `a5394d3`; replace shared membership updates with worker-private compressed country sets and a parallel exact union, using original atomics beyond255 countries. Build normally. It is slower locally; rejected. Raw reports: `round2-c-private-*`. Those older verification reports explicitly distinguish workspace source hashes from the tested prototype binary; this patch preserves its actual source.

All variants were written during this event. No copied answers or training outputs are included.

For the private-loader cursor model, copy `test-private-loader.cpp` to the disposable checkout root and compile it with address/UB sanitizers. It checks80 generated degree layouts, high-degree overflow, and the65535/65536 block boundary against explicit32-bit cursor ranges. This test passed before the slower prototype was rejected.

C locality prototypes `round6-owned-blocks.patch` and `round6-inline262k.patch` apply to `eb16c07`. Compile normally; warm once and hash each full trial. Owned names with a separate bitmap are slower than the selected inline-country layout. Doubling the inline table saves about3% local time but costs2.1MB, so it is not selected. These variants were not sent to the board.

The rejected flat/streaming A program is fully preserved at commit2917982. `rejected_log_aggregate.hpp` preserves its exact helper for the current standalone `tools/test_log_aggregate.cpp`; this file is outside every scored build context and is not used by the retained A runtime. The model also accepts LOG_AGGREGATE_HEADER for reproducing another checkout.

`round9-eight-digit.patch` applies to61e345f and is checked with tools/test_primitives.cpp using DECIMAL_HEADER; it is rejected for a marginal1.2% local change. `round11-prefetch-l1.patch` and `round11-prefetch-l3.patch` also apply to61e345f; both are slower locally and never board-submitted. The rejected SIMD scanner is preserved at1b21266 and as rejected_csv_scan.hpp for tools/test_csv_scan.cpp; explicit SSE2/AVX2/NEON models passed, but official total K was lower. CSV_SCAN_HEADER selects another source copy for reproduction.
