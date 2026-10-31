# Scored optimization results

Official board snapshot: 2026-10-31T07:17:20Z. These are public practice-board machine points, separate from final holdout scoring and human judging.

Best-three machine-point geometric mean: **45.22 → 64.77**. Current rank **33/61** teams with three scored tracks; leader Cause Of Death **79.63**. The leaders remain ahead.

| Track | Original points | Our best points | Leader points | Rank |
| --- | ---: | ---: | ---: | ---: |
| A | 47.25 | 69.70 | 85.79 (NickTrapp) | 31/76 |
| C | 40.42 | 64.90 | 80.65 (NickTrapp) | 31/63 |
| D | 48.43 | 60.05 | 72.99 (Cause Of Death) | 21/66 |

| Track | Best run | Time | Cgroup peak | K |
| --- | --- | ---: | ---: | ---: |
| A | `run-1f9a7602cf67` | 0.060856 s | 39.80 MB | 24.779894 |
| C | `run-4bcf23d06742` | 0.088260 s | 12.45 MB | 19.865280 |
| D | `run-9f77334ae44a` | 0.326739 s | 78.05 MB | 15.886532 |

## Exact retained-source confirmation

Commit `d28fe2590101b6b9a362e71b7bd8ee8f379f0741` passed **check, build, correctness, timeout and sandbox** for every selected track. All 25 runtime/build inputs and track metadata are byte-identical to the previously scored commit `61e345f`; documentation/tests are separate. This exact combined confirmation is distinct from historical best observations.

| Track | Confirmation run | Time | Points |
| --- | --- | ---: | ---: |
| A | `run-4055dcf05865` | 0.061166 s | 69.531199 |
| C | `run-a3119404362b` | 0.096142 s | 64.042244 |
| D | `run-f169e16c8fde` | 0.348996 s | 59.323451 |

Same-source practice runs vary, including the lower C/D values in this confirmation. No repeated-run delta is called a new algorithm improvement. Final scoring uses the separate holdout and organizer procedure.

## Retained techniques

- A: hour-owned small workspaces, exact percentile selection, twelve workers, generic GCC/sample PGO, original allocator environment.
- C: quote-aware scalar field parser, exact decoded name keys co-located with actual atomic country words, release/acquire publication, twelve workers, native GCC/full+sample PGO.
- D: exact byte-degree wrap recovery, narrow/wide atomic scatter cursors, lossless specialized edge encoding, private exact labels, distance bands of width 64 and batches of eight, six query workers/four loaders, native GCC/full+sample PGO.

Flat/streaming A and SIMD C passed correctness but lowered real total K, so their runtime code was removed. Eight-byte parsing and extra label-prefetch prototypes were not promoted after marginal/slower local measurements. Other rejected experiments remain in per-track PERF.md and reproducible historical patches.

## Verification and eligibility evidence

Final retained native/reference/new-seed/adversarial/full hashes and offline restricted GCC15/Linux full outputs pass. Retained algorithms also passed memory/UB and thread sanitizers, independent Floyd–Warshall graphs, exact name/country models, and exact degree/cursor ownership models. Linux/Apple development timings are not presented as official score evidence.

Reports: [final board](board-retained-final.json), [native](final-retained-native.json), [full public](final-retained-public.json), [Linux](final-retained-container.json), [source identity](final-retained-source-match.json), [leader comparison](optimization-comparison.json), [entry audit](ENTRY-AUDIT.md), [owner explanation](OWNER-BRIEFING.md).

The audit checks observable rules/provenance, not an organizer-issued eligibility certificate. Individual registration is entrant-confirmed; team registration/app scope/scored tracks are verified. AI assistance is disclosed; no personal-understanding attestation is invented.

**Still required:** keep the passing `speed-demon` commit through 2 November 2026 at 15:00 UTC (20:30 IST), and make that MIT-licensed source public by 16:00 UTC (21:30 IST). The repository remains private; no automatic publication or monitor is scheduled.

[Official team board](https://speeddemon.dev/board/#red-jones-00c4a7) · [Official feed](https://s3.amazonaws.com/raptors.dev/speeddemon.dev/2026/board/board.json)
