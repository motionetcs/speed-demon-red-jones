# Scored optimization results

Complete official snapshot: 2026-10-31T10:56:56Z. These are public practice-board machine points; final holdout and human judging are separate.

During this pass the best-three machine-point mean rises **66.095609 → 66.828101**. Rank moves from **32/68** to **29/70**. Current overall leader Cause Of Death: **80.786854**. We are not first; the gap remains substantial.

| Track | Starting best | Current best | Rank | Current track leader |
| --- | ---: | ---: | ---: | --- |
| A | 72.105578 | 72.105578 | 36/85 | Kirk Mates 86.472268 |
| C | 66.473216 | 66.473216 | 29/72 | NickTrapp 82.553467 |
| D | 60.242402 | 62.267555 | 21/75 | Cause Of Death 72.994274 |

## What is retained

D's retained changes are the bounded 16-row degree/cursor/edge prefetch loader, process-local glibc arena cap of 2, and up to 12 loading workers. The exact query algorithm, full-width fallbacks and output order remain. Observed best points progress 60.242402 →60.654874 →60.664986 →62.267555, K=16.026845 →17.593454, including charged source and memory. The twelve-loader test is run-9f2217b19cd8 at c4f966f: T=0.248728 s, M=88,686,592, S=772. Its 163.371-second build is within 600 seconds. The final byte-identical repeat 61.156615 also exceeds the preceding cap2 best 60.664986.

A and C restore their exact previously scored bf75194 runtime/build/metadata. A retains fused exact four-byte request records/full uint32 escapes, lazy hour storage, full-equality endpoint IDs, 8,192 slots and sort cutoff 32. C retains exact quote-aware parsing, full-hash/name equality, inline atomic country membership, narrow region lookup with full fallback, direct country map and XOR quote parity. No A/C algorithm gain is claimed in this pass.

The hour/method caches, word scanner, grouped/aligned name lookup, aligned aggregate counters and A input prefaulting passed full validation but failed to beat retained real K. They are reverted. Block/deque/reservation/cache/split/tagged/layout/output/delimiter/ordered-query screening losers remain in prototype patches with their actual validation limits. The small numeric-suffix gain is only local screening and is not promoted. Mac timings did not consistently transfer to Intel; every submitted candidate was decided by a real board run.

## Exact selected combination

Commit `07c31360af938e391c3e09e3d21f969a1709b092` passes all five board gates for A/C/D. Every one of 27 current runtime/build/track-metadata inputs matches that exact scored commit and each current best-record source in round55-final-source-match.json. Further evidence/documentation updates change no compiled input. No active source candidate or board watcher remains.

| Track | Final confirmation run | Time | Charged memory | K | Points |
| --- | --- | ---: | ---: | ---: | ---: |
| A | `run-7263989cd59b` | 0.064861 s | 33,828,864 B | 24.447324 | 69.411566 |
| C | `run-5f54924be806` | 0.080746 s | 11,706,368 B | 20.649589 | 65.745571 |
| D | `run-ec2238f1c6b2` | 0.272721 s | 90,984,448 B | 16.715998 | 61.156615 |

Historical best observations and latest confirmations are separate. Same-source practice results vary; lower repeats are preserved honestly and are not described as algorithm regressions or gains.

## Validation and entry

Selected A/C source passes fresh isolated 1109/1117 strict ASAN/UBSAN, 1123 TSAN, every adversarial/reference case, and country widths 0/1/254/255/256/257/17576. D retains exact isolated 1079/1087 strict ASAN/UBSAN, 1091 TSAN and 256 independent Floyd–Warshall graphs/85,871 answers. Public outputs at 1/6/12 workers match. All selected Linux images pass full public/default contracts and 1,056 current-image fixture replays; D's new image identity was replayed rather than inheriting another image's result. Exact source/input/image hashes are preserved.

The native validator now isolates fixture/output paths with --run-id. Original round38 adversarial suites could share paths; isolated reruns and 1,047 exact-image Linux replays corrected that attribution. Original reports state the limitation. Final selected-source suites use isolated paths. No diagnostic or failed tradeoff is hidden.

Observable entry checks pass: fresh event-written source, required branch/files, pinned allowlisted offline builds, MIT attribution, accepted team/app scope and disclosed AI assistance. Registration is entrant-confirmed; no organizer eligibility certificate or human-understanding attestation is fabricated.

**Still required:** preserve the final passing branch at 2 November 2026 15:00 UTC / 20:30 IST and make that MIT source public by 16:00 UTC / 21:30 IST. The repository remains private, which is allowed now. Publication/future monitoring are not scheduled.

## Separate emoji target

The clarified target was overall #1's counters. The saved visible row respect 5,848 / devils 13,290 / pumpkins 38 / cans 37 exceeds observed Cause Of Death 369/75/28/8 in all four. No reactions were added in this pass. Counts can change through visitors; reactions do not change K, rank or demon level. Proof: emoji-status.json and emoji-result.jpg.

[Real final confirmation](board-round55-selected-final.json) · [All27 source identities](round55-final-source-match.json) · [Leader comparison](round55-final-comparison.json) · [Entry audit](ENTRY-AUDIT.md) · [Official board](https://speeddemon.dev/board/#red-jones-00c4a7)
