# Rejected prototype sources

These are historical experiments, not the submitted track sources. Apply each patch to a disposable checkout of its baseline; do not apply it to the live submission merely because it passes correctness. Timings are Apple ARM development measurements, not board scores.

- `round3-private-loader.patch`: baseline `a5394d3`; compile D with ordinary release flags for four loaders, or add `-DLOADER_COUNT=2` for two. Compact degree counters and relative cursors retain exact overflow. Both variants are slower locally; rejected. Raw reports: `round3-private-d-*`.
- `round3-c-crc.patch`: baseline `d2fd0b5`; compile with `-march=armv8-a+crc` on Apple ARM or `-march=native` on x86 with SSE4.2. Exact string equality remains mandatory. It passes output tests but is slower locally; rejected. Raw reports: `round3-c-*`.
- `round2-c-private-membership.patch`: baseline `a5394d3`; replace shared membership updates with worker-private compressed country sets and a parallel exact union, using original atomics beyond255 countries. Build normally. It is slower locally; rejected. Raw reports: `round2-c-private-*`. Those older verification reports explicitly distinguish workspace source hashes from the tested prototype binary; this patch preserves its actual source.

All variants were written during this event. No copied answers or training outputs are included.

For the private-loader cursor model, copy `test-private-loader.cpp` to the disposable checkout root and compile it with address/UB sanitizers. It checks80 generated degree layouts, high-degree overflow, and the65535/65536 block boundary against explicit32-bit cursor ranges. This test passed before the slower prototype was rejected.
