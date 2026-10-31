# Scored optimization results

Complete public-board snapshot: **2026-10-31T12:58:43Z**. These are practice machine points; final holdout and human judging are separate.

This pass raises the best-three mean **67.471954 → 67.848530**. Rank changes **29/71 → 32/75** as other teams improve. Overall leader Cause Of Death: **81.805732**. We are not first.

| Track | Starting best | Current best | Rank | Track leader |
| --- | ---: | ---: | ---: | --- |
| A | 72.105578 | 72.105578 | 41/90 | Cause Of Death 86.819493 |
| C | 66.473216 | 67.592444 | 30/76 | NickTrapp 83.006413 |
| D | 64.084694 | 64.084694 | 14/79 | Cause Of Death 73.008704 |

## Retained changes and exact selected source

C adds two measured improvements: exact local CSV synchronization, then a bounded one-pass canonical-name ownership pipeline. Points **66.473216 →66.848983 →67.592444**, K **21.353266 →21.725994 →22.482722**. The final pipeline has8 readers/4owners at12 workers,512-event SPSC vectors, exact full-key equality and private country membership. Compared with the starting C best, observed runtime falls **77.215 →62.764 ms (18.72%)** while memory rises **11,071,488 →13,221,888 B** and charged source **591 →660**; those costs are already included in K. The unchanged pipeline repeats67.583792 on round70, within0.01 point of its best and above the earlier66.848983 version.

A retains exact57cc23e source: fused four-byte records/full uint32 escapes, full endpoint equality, lazy hour storage and sort cutoff32. All allocator/scalar/native/CRC variants that fail real K are removed. D retains exact57cc23e:12 loaders,16-row degree/cursor/edge prefetch, compact exact storage/distances/queues and process-local arena cap2. Its64.084694 best is an unchanged-source repeat, not a new D algorithm gain in this pass.

Every one of27 selected source/build/metadata inputs matches **eb80bc6d279802d8280a0dc15b8d824aa2d96ac1**, which passes every official gate for A/C/D, and each track's current best source. Proof: [round71-final-source-match.json](round71-final-source-match.json). A fresh official confirmation of the restoration commit is the next final step; documentation/evidence-only changes do not alter these inputs.

## Genuine new candidate batches

| Batch / commit | A points | C points | D points | Decision |
| --- | ---: | ---: | ---: | --- |
| [60 / a5887ec](board-round60-intel-c-allocator-a.json) | 69.716930 | 66.064518 | 62.250218 | Reject A arena cap and C word/CRC; D repeat |
| [62 /9933500](board-round62-mapped-splits-endpoints.json) | 71.976519 | 66.848983 | 63.188089 | Retain C local synchronization; reject A/D |
| [64 /44d8c63](board-round64-native-scalar-sse.json) | 71.503199 | 66.522472 | 63.549678 | Reject A lean/native and isolated C128; D repeat |
| [67 /eb80bc6](board-round67-bounded-c-pipeline.json) | 71.296967 | 67.592444 | 62.752392 | Retain C bounded pipeline; A/D repeat |
| [70 /7402c7f](board-round70-endpoint-crc.json) | 68.916469 | 67.583792 | 60.515575 | Reject A CRC; C repeat confirms pipeline; D repeat |

Every submitted batch passes check/build/correctness/timeout/sandbox. Lower repeats and losing candidates remain in the raw reports and per-track PERF logs. No same-source delta is labelled an algorithm gain.

## Validation and reproducibility

Current exact Linux images have **A69/C120/D945=1,134 fixture replays** with matching image IDs. Fresh combined Make builds and full-public outputs at1/6/12 workers, and actual native/Linux defaults with no thread/path override, pass. Selected A uses its exact prior strict sanitizer/race source; selected C has fresh1223/1229 ASAN/UBSAN and1231 TSAN, complete country widths through17576, and queue progress/ownership/reference checks across every1..12 worker count. Malformed-input cancellation exits normally and promptly. Independent private-name std::set/collision/growth/country/stable-block/long-key/overflow and CSV boundary/guard-page models pass native/GCC. The unified name-store model also retests the legacy shared API. D keeps the exact prior sanitizer/race/primitive and independent256-graph/85,871-answer evidence, replayed in its current image.

The round70 A CRC candidate additionally passes actual SSE4.2 polynomial-reference/guard-page/collision/ID checks and69 GCC sanitizer integration runs. It is rejected solely because actual total K loses. Those target-specific results are not claimed for the restored standard-hash A.

The earlier round38 shared test-path limitation is preserved and corrected by isolated reruns; later native suites use unique run IDs. The Darwin allocator observer was corrected after mincore diagnostics; its production allocator never changed, and Linux still verifies actual unmapping. Old invalid assumptions, rejected tradeoffs and source/image identity limitations are not hidden.

## Next optimization evidence

Retained-source high-level native profiles identify A parsing (~25 ms of45.5 ms) and D search (~154 ms of272 ms) as largest local phases. They are Apple diagnostics, not Intel phase measurements. Endpoint pipelines/prefetch, C probing/layout/word/hash, graph staging/private degrees and D hash/reset variants fail their recorded tradeoffs. Reproducible patches and precise screening-versus-full-validation limits are indexed in round57-59, round61, round63-64, round65-67 and round68-70 prototype reports. No rejected implementation remains in a track folder.

## Entry requirements

Fresh event-written code, MIT attribution, disclosed AI assistance, required branch/files, allowlisted pinned offline builds and source-only contexts pass observable audit checks. Registration is entrant-confirmed; team/app scope and real gates are verified. This is not an organizer eligibility certificate or a claim of personal human code understanding.

**Still required:** preserve the final passing branch at **2 November2026 15:00 UTC /20:30 IST**, then make that MIT source public by **16:00 UTC /21:30 IST**. The repository is private now, which is allowed. Future publication/monitoring are not scheduled.

The saved four-emoji target exceeds the observed overall leader at the recorded time; counts can change through visitors. No reactions were added during this pass. Reactions do not change K, rank or demon level. Saved proof: emoji-status.json and emoji-result.jpg.

[Full leader snapshot](round71-final-board.json) · [Comparison](round71-final-comparison.json) · [Entry audit](ENTRY-AUDIT.md) · [Live board](https://speeddemon.dev/board/#red-jones-00c4a7)
