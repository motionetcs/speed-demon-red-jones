# Current working state

Fresh Red Jones entry: https://github.com/motionetcs/speed-demon-red-jones ; private, required branch `speed-demon`, tracks A/C/D. Preserve unrelated workspace folders. All own code is fresh event code; pinned official reference material is under tools/official.

## Retained runtime

Retained runtime/build source commit `11e467385c4d8869a4afbcc7bb8a80d42ff99e98` is pushed and scored; every A/C/D gate passed in board-round15-offsets.json. All25 current runtime/build inputs and track metadata match that exact scored commit, proven in round15-final-source-match.json. A adds lossless16-bit line-offset deltas with full32-bit escape anchors. C/D match the previously confirmed d28fe25 runtime inputs byte for byte. Only documentation/test updates follow this exact confirmation.

- A: twelve workers; generic GCC, PGO trained on sample seeds 104729 and 130363; hour-owned workspaces, lossless16-bit line deltas/32-bit absolute escapes, exact ranks, original allocator environment. Best70.144504 points / K25.286579, run-c26f23dfdc36.
- C: twelve workers; native GCC, PGO trained on full seed 1000003 and sample seed 130363; scalar quote-aware fields, dense immutable decoded names plus actual atomic country words, exact equality/growing table. Best 64.904735 / K 19.865280, run-4bcf23d06742.
- D: six query workers/up to four loaders; native GCC/full+sample PGO; exact byte degree wraps and narrow/wide shared cursors, specialized 21-bit/11-bit edges with exact larger-node/weight fallback, private labels, distance bands of width 64 and batches of eight. Best 60.051455 / K 15.886532, run-9f77334ae44a. Same-source repeated records are variation, not new algorithm gains.

Flat/streaming A, SIMD C, wider D bands, variable edge decoding, private loader copies, hardware hashing, private membership, eight-digit parsing and extra label prefetch were rejected based on documented total-score/local evidence. Never reintroduce them from Apple timing alone. Source and truthful raw reports remain in history and docs/prototype-patches. No unscored runtime prototype is retained. C membership-read and D negative-filter experiments were reverted after lower real K; small-group A selection and D corridors were rejected as slower locally.

## Iteration rules

Benchmark one process at a time, with no simultaneous compilers/tests/training; warm once, alternate and hash every output. Native Apple RSS/timing and emulated Linux times are not official Intel/cgroup score evidence. Include canonical S and dependencies in K decisions. Do not overwrite historical reports.

Use tools/verify.py with unique reports/new seeds/source roots, tools/test_band_graphs.py for independent all-pairs graphs, the primitive/name/loader models for changed invariants, and tools/container_verify.py plus verify_container_cases.py for exact offline restricted Linux outputs. UBSAN halts on the first diagnostic. Models explicitly cover full-hash collisions, Unicode/NUL/empty values, country boundaries, degrees/cursors at 65,535 and 65,536, wide node IDs, MAX weights and 64-bit paths. All final algorithms passed strict memory/UB and race checks.

`tools/watch_board.py --commit <sha> --report docs/<unique>.json` waits for exact A/C/D real scores. Save the preceding commit before another source push; dispatches are at least five minutes apart. `tools/compare_board.py` refreshes best records/ranks and best-three machine-point geometric mean. Human judging/holdout are separate. RESULTS.md and optimization-comparison.json contain the current final snapshot; later live ranks can move.

## Entry requirements

Registration is entrant-confirmed; team form/app access and real scored A/C/D are verified. Board app read access is limited to this repository. MIT attribution is preserved. The audit checks observable evidence, not organizer-issued eligibility. Red Jones is visible; B is blank because it is not entered. MY TEAM and visual effects are browser/presentation features.

Freeze: 2 November 2026 at 15:00 UTC (20:30 IST). Preserve the passing branch commit and publish that MIT source by 16:00 UTC (21:30 IST). Private is allowed before then. No publication or monitoring automation is scheduled. The owner must remain reachable and may need to explain the approach; OWNER-BRIEFING.md is an honest guide, not a claim that the owner has reviewed it.

Final saved machine snapshot: 2026-10-31T07:50:02Z; mean64.902963, rank32/66, leader80.244238. Leaders remain ahead; no win is claimed. No unscored runtime candidate remains.

Separate clicker counts: respect3,123 / devils10,371 / pumpkins24 / cans21, total13,539; demon level18. Visible controls were used, no counter API or rate-limit bypass. A bulk pumpkin hold was blocked by automatic review and stopped. No finite cap was shown; do not claim a maximum or clicker leadership.
