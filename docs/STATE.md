# Current working state

Fresh Red Jones entry: https://github.com/motionetcs/speed-demon-red-jones ; private repository, required branch `speed-demon`, selected tracks A/C/D. Preserve unrelated workspace folders. Use only this fresh event implementation and pinned official material.

## Best confirmed configurations

- A: source algorithm from `d2fd0b5`, generic GCC with sample-seed PGO from `46504cb`; twelve workers/hour-owned workspaces, exact selection, original allocator environment. Best69.621943 points/K24.685326, `run-7b5e46ea09f2`.
- C: exact d2 parser/compact mapped-and-decoded keys and atomic membership, twelve workers, ordinary native-targeted GCC. Best63.747340/K18.834184, `run-60c3460244d4`. Sample PGO, canonical interiors and delimiter-only variants scored lower; hardware hashing was rejected locally before submission.
- D: `a5394d3` six-byte CSR edges, private compact exact labels,64-distance bands with8-entry batches, six workers/up tofour loaders, sample PGO. Best57.219555/K13.944120, `run-ca3be2d2ada3`.

`bba4fe0` is pushed and passed all gates, but its variable-width packed D edges score55.706308:77.61 MB helps memory, while0.513509 s hurts total K. It is a rejected candidate, not the strongest D source.

## Current unscored candidate

Working tree tests full-scale PGO training at independent seed1000003 plus sample130363 for A/C/D. D specializes21-bit packed-node loops once at the graph header, retaining exact six-byte fallback beyond2^21 nodes and exact uint32 weight side tables. The code computes every answer from current timed input; no cached outputs or seed recognition. The runtime images copy only executables.

Native D fresh sample/full/Floyd-Warshall, strict ASAN/UBSAN, TSAN and both compact/wide-ID fixtures pass. A/C full-training Linux images and63 independent untrained Linux runs pass. D full-training offline build/replay remains in progress. Do not submit until it passes, build input hashes match, and the precise candidate is documented. Do not push a subsequent source until the preceding exact-commit board report is saved. Reject this candidate if its real K is lower, restoring the configurations above.

## Iteration commands and evidence

`make` builds native C++20. Benchmark one process at a time, with no simultaneous compilers/tests/training; warm once, alternate configurations, hash every output. Native Apple ARM timings/RSS and emulated Linux times are not Intel/cgroup score evidence.

`tools/verify.py` compares official references and adversarial outputs, accepts `--tracks`, `--source-root`, `--binary-dir`, fresh seeds, worker counts and unique report names. UBSAN halts on the first diagnostic. `tools/test_band_graphs.py` supplies256 independent all-pairs graphs. `tools/test_primitives.cpp` models queues/labels and guard-page parsing. `tools/test_edge_store.cpp` covers exact storage and sentinels. `tools/container_verify.py` checks offline allowlisted GCC15/Linux builds and default output contract. `tools/verify_container_cases.py` replays independently checked cases at1/6/12 workers.

`python3 tools/watch_board.py --commit <sha> --report docs/<unique-name>.json` waits for every exact A/C/D scored result. Official team dispatches are at least five minutes apart; do not flood the queue. `python3 tools/compare_board.py` refreshes complete official snapshots and computes best-three machine-point ranks. Human judging/holdout are separate. Keep historical reports truthful and immutable. Per-track PERF.md records accepted and rejected experiments; reproducible rejected patches are under `docs/prototype-patches`.

## Entry requirements

Registration is entrant-confirmed; team form/app installation and real scored tracks are verified. The board app has read access to this repository only. Current entry audit passes all observable checks; this is not an organizer-issued eligibility certificate. The browser shows Red Jones, with B blank because it is not entered. “MY TEAM” and visual reactions are browser/presentation features.

Freeze is2 November2026,15:00 UTC/20:30 IST. Keep the passing commit on `speed-demon`, and publish that MIT-licensed source by16:00 UTC/21:30 IST. It may remain private before then. No publication or monitoring automation is scheduled. The owner must remain reachable and may need to explain the approach; `docs/OWNER-BRIEFING.md` is an honest explanation, not a claim of personal understanding.
