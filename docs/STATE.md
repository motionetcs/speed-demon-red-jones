# Current working state

Fresh Red Jones entry: https://github.com/motionetcs/speed-demon-red-jones ; private repository, required branch `speed-demon`, selected tracks A/C/D. Preserve unrelated workspace folders. Use only this fresh event implementation and pinned official material.

## Best confirmed configurations

- A: source algorithm from `d2fd0b5`, generic GCC with sample-seed PGO from `46504cb`; twelve workers/hour-owned workspaces, exact selection, original allocator environment. Best69.704972 points/K24.779894, `run-1f9a7602cf67` (same-source repeat).
- C: exact d2 parser/compact mapped-and-decoded keys and atomic membership, twelve workers, native-targeted GCC with full seed1000003 and sample130363 training. Best64.904735/K19.865280 with dense keys and full-scale training, `run-4bcf23d06742` (same-source repeat). Sample PGO, canonical interiors and delimiter-only variants scored lower; hardware hashing was rejected locally before submission.
- D: `eb16c07` specialized four-byte CSR edges with exact six-byte fallback, private compact exact labels,64-distance bands with8-entry batches, six workers/up tofour loaders, full-scale PGO. Best60.050609/K15.885913 with narrow degree/cursor loader, `run-f53c4e4a6ec9` (same-source repeat).

`bba4fe0` is pushed and passed all gates, but its variable-width packed D edges score55.706308:77.61 MB helps memory, while0.513509 s hurts total K. It is a rejected candidate, not the strongest D source.

## Current unscored candidate

`2917982` passed all official gates, but flat/streaming A scored66.822927, below69.704972. Working tree restores exact strong A main/Docker source from61e345f and removes its rejected helper from the scored folder. Rejected source/models remain in history/artifacts. D/C otherwise retain their latest confirmed algorithms.

Current C candidate adds bounded SIMD comma/CR/LF scanning only for unquoted fields, preserving quoting/EOF/BOM/byte semantics. NEON local median improves about4%; S and actual Intel time still decide K. Fresh sample/full, strict ASAN/UBSAN/TSAN, all-byte/offset/random scalar models, protected-page tests, explicit GCC SSE2/AVX2/native and Apple NEON models, and Linux cases pass. Assert exact build-input hashes, push, then capture exact A/C/D scores before another source push.

D eight-byte numeric parser is rejected before submission for a marginal1.2% local gain. An unsubmitted neighbor-label prefetch prototype is prepared under `.build/round11-d-prefetch`; it has not been compiled/tested. Never promote a prototype on local timing alone. Benchmark sequentially with no competing compilers/tests/training.

## Iteration commands and evidence

`make` builds native C++20. Benchmark one process at a time, with no simultaneous compilers/tests/training; warm once, alternate configurations, hash every output. Native Apple ARM timings/RSS and emulated Linux times are not Intel/cgroup score evidence.

`tools/verify.py` compares official references and adversarial outputs, accepts `--tracks`, `--source-root`, `--binary-dir`, fresh seeds, worker counts and unique report names. UBSAN halts on the first diagnostic. `tools/test_band_graphs.py` supplies256 independent all-pairs graphs. `tools/test_primitives.cpp` models queues/labels and guard-page parsing. `tools/test_edge_store.cpp` covers exact storage and sentinels. `tools/container_verify.py` checks offline allowlisted GCC15/Linux builds and default output contract. `tools/verify_container_cases.py` replays independently checked cases at1/6/12 workers.

`python3 tools/watch_board.py --commit <sha> --report docs/<unique-name>.json` waits for every exact A/C/D scored result. Official team dispatches are at least five minutes apart; do not flood the queue. `python3 tools/compare_board.py` refreshes complete official snapshots and computes best-three machine-point ranks. Human judging/holdout are separate. Keep historical reports truthful and immutable. Per-track PERF.md records accepted and rejected experiments; reproducible rejected patches are under `docs/prototype-patches`.

## Entry requirements

Registration is entrant-confirmed; team form/app installation and real scored tracks are verified. The board app has read access to this repository only. Current entry audit passes all observable checks; this is not an organizer-issued eligibility certificate. The browser shows Red Jones, with B blank because it is not entered. “MY TEAM” and visual reactions are browser/presentation features.

Freeze is2 November2026,15:00 UTC/20:30 IST. Keep the passing commit on `speed-demon`, and publish that MIT-licensed source by16:00 UTC/21:30 IST. It may remain private before then. No publication or monitoring automation is scheduled. The owner must remain reachable and may need to explain the approach; `docs/OWNER-BRIEFING.md` is an honest explanation, not a claim of personal understanding.
