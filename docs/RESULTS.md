# Results — 1 November 2026

Complete normal public feed **2026-11-01 00:14:45 UTC**: Red Jones is **41st of90**, versus40th/89 at23:34. Best-three machine mean **69.436015**, versus69.396597. Leader Cause Of Death has**82.410012**. We are not number one. Only a modest A build choice is retained this cycle, with0.128065 higher best points and mixed repeats. Both C inlining trials lose real K and are fully restored. Every selected187 track passes real gates; latest C is a lower same-code outlier. Public bests and final holdout/judging remain separate.

| Track | Best points | K | Rank | Leader |
| --- | ---: | ---: | ---: | --- |
| A | 75.240074 | 31.974332 | 42/107 | Kirk Mates 87.283533 |
| C | 68.118071 | 23.033578 | 45/91 | NickTrapp 83.814878 |
| D | 65.319494 | 20.248361 | 26/93 | Cause Of Death 73.181601 |

Four changes are retained:

- **A:mapped record storage with the accepted endpoint cache.** Actual145 raises72.924546 to73.371413 and K28.740275 to29.337848. Charged memory35,426,304→27,340,800B falls22.82%, while time0.044513→0.046329s is4.08% slower and source424→457 grows. The net K improves2.08%. This is a memory/source/time tradeoff, not a runtime-speed claim or a precise causal estimate from one observation. Completed hour owners return fully consumed record pages directly to the OS. The exact4096 cache/canonical views, four-byte records/full32 escapes, quantiles and original generic/sample PGO stay. Earlier allocator62 used the older interner and64 also changed scalar/native flags; this combination has fresh strict/reference/image proof.
- **A:ordered completion with directly mapped output and bounded prefix8 decoding.** All12 aggregation workers remain. Each completed hour publishes under a mutex; that publisher writes consecutive completed hours and releases mapped output strings. Empty hours also publish, and no worker waits for a missing hour. Final close follows joined workers. A bounded8-byte digit-prefix decoder preserves exact fulluint32/scalar tails. First actual163 raises73.371413 to74.448567, K29.337848 to30.829845 (+5.09%); memory27,340,800→20,787,200B falls23.97%, time0.046329→0.045650s is1.47% lower, and source457→497 grows8.75%. This is the combined design's measured tradeoff, not separate component effects or a precise causal timing estimate. Exact-source165 later reaches74.747885/K31.257749,17374.858990/K31.418092 and17575.112009/K31.786315; these extra repeat increases are variation.
- **C:eight-byte owner entries.** Full length/byte equality follows a32-bit rejection fingerprint; checked indices address stable64KiB word blocks, with dedicated oversized-key blocks. Full64 hashes still route owners. Actual128 raises67.750087 to67.875642, K22.646534 to22.777856; charged memory13,045,760→12,378,112B falls while time0.062192→0.062444s and source660→672 grow. Unchanged137 later measures67.916082/K22.820315,147 measures67.958752/K22.865201, restored165 measures68.007047/K22.916113,16768.028087/K22.938327 and17568.118071/K23.033578; these extra bests are variation, not additional algorithm changes.
- **D:32-entry query batches.** Same exact64-distance bands, full-width distances, packed labels and conservative stopping rule; only batch8→32 changes. Actual104 raises64.570088 to65.222044, K19.561482 to20.157695. Unchanged163 later reaches65.319494/K20.248361; that extra best is variation. Later identical-source results vary materially; the best observation and native controls support retention without a precise causal timing estimate.

A178 also changes first build-time training104729/sample→1000003/full, keeping130363/sample, generic GCC flags and every C++/header byte unchanged. First actual raises75.112009→75.240074 and K31.786315→31.974332 (+0.59%); T0.042786→0.042474s, M20,979,712→20,746,240B, S497 unchanged. Four same-build K31.974332/31.268346/31.905497/31.607629 give two above prior best, two below. Retain the best observed build choice, with no robust causal timing estimate or promised holdout gain. This is not a fifth algorithm gain. Only the executable enters the final image; public seed1 is never trained.

A retains163 ordered mapped-output/prefix8/exact4096 cache. C is fully original low32 offset8-reader/4-owner512-event with full1000003/sample130363 PGO. D retains12 atomic loaders/cursors/CSR, exact bidirectional band64/query32 and arena2. Every inlining/tail/staging/overwrite/one-way/hint prototype is absent. OWNER-BRIEFING describes actual techniques without claiming personal understanding.

All29 inputs/full runtime-build file sets exactly match real all-gates selected187/d6cea744a3e5d8790d777445aee82b7ea58b79ba and each current best source(A178,C175,D163). [Final source/local-image proof](round187-final-source-match.json) distinguishes replayed local IDs from unexposed organizer IDs. Later documentation heads are not individually claimed scored.

| Selected187 | Run | Time | Charged memory | S | K | Points |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| A | run-d3e26c39a872 | 0.043080s | 21,213,184B | 497 | 31.607629 | 74.989596 |
| C | run-0040c07b5d6f | 0.098959s | 12,079,104B | 672 | 18.182538 | 62.982725 |
| D | run-893f46cf2767 | 0.201343s | 77,291,520B | 827 | 19.893315 | 64.935358 |

All check/build/correctness/timeout/sandbox gates pass. [Raw selected record](board-round187-selected-confirmation.json). Original-C1870.098959s/62.982725 stays separate from68.118071 best, with no invented algorithm regression or target-phase explanation. A/D lower repeats are preserved too.

| Actual batch / commit | A points | C points | D points | Decision |
| --- | ---: | ---: | ---: | --- |
| [89 /864fb25](board-round89-canonical-shared.json) | 72.410292 | 65.966555 | 64.284606 | Reject shared canonical C |
| [95 /13e3224](board-round95-full-pgo-pause.json) | 72.744778 | 67.272496 | 64.000687 | Reject full-PGO A and pause C |
| [104 /252d750](board-round104-event24-batch32.json) | 72.837330 | 67.731481 | **65.222044** | Keep D32; reject24-byte C event |
| [107 /8182e42](board-round107-owned-loader.json) | 71.448230 | 67.502025 | 57.652656 | Reject owned D loader |
| [109 /6e5950c](board-round109-selected-confirmation.json) | 72.786488 | 67.402878 | 64.547044 | Confirm selected combination |
| [111 /cc66c82](board-round111-native-a-arena-c.json) | 72.203363 | 67.448548 | 64.946617 | Reject native A and arena C |
| [118 /ea8bfe3](board-round118-calendar-a.json) | 72.421065 | 67.371094 | 64.827966 | Reject calendar A |
| [119 /f69d4db](board-round119-selected-confirmation.json) | 72.323326 | 62.708517 | 64.741616 | Preserve lower identical-source C outlier |
| [121 /e3eb08d](board-round121-structural-c.json) | 72.371758 | 60.906292 | 62.581261 | Reject64-byte C structural scanner |
| [124 /b3d0cef](board-round124-avx2-d.json) | 72.133969 | 67.426918 | 65.060530 | Reject D AVX2 lookup |
| [128 /93fc9c9](board-round128-offset-c.json) | 72.781312 | **67.875642** | 64.706922 | Keep exact compact C table |
| [130 /83a5f9c](board-round130-evidence-head.json) | 70.452640 | 64.166152 | 63.404992 | Preserve lower identical-source repeats |
| [133 /16bedd2](board-round133-cooperative-c.json) | 72.079753 | 67.120025 | 65.221092 | Reject cooperative C roles |
| [135 /2b3834d](board-round135-selected-confirmation.json) | 72.731143 | 63.445764 | 64.978380 | Confirm exact selected128 restoration |
| [137 /715dcc6](board-round137-evidence-head.json) | 71.744299 | **67.916082** | 64.626046 | Same-source C best is variation |
| [139 /184778c](board-round139-method-reserve.json) | 72.847125 | 63.691689 | 63.052547 | Reject method dispatch and D reserve |
| [145 /348257e](board-round145-mapped-cache.json) | **73.371413** | 67.905347 | 64.765597 | Keep mapped/cache A; C/D original |
| [147 /69322d0](board-round147-evidence-head.json) | 71.405557 | 67.958752 | 64.767748 | Same-source C best is variation |
| [151 /9e5d342](board-round151-spsc-windows.json) | 72.809116 | 66.399760 | 64.514489 | Reject per-connection SPSC C |
| [155 /4191767](board-round155-pooled-private.json) | 72.308880 | 67.741711 | 63.893717 | Reject pooled C and private-degree D |
| [157 /34293c2](board-round157-selected-confirmation.json) | 71.321046 | 67.796856 | 62.479120 | Confirm exact selected145 restoration |
| [159 /0882828](board-round159-evidence-head.json) | 72.366333 | 67.901744 | 65.047586 | Unchanged lower repeats |
| [163 /d0bf708](board-round163-ordered-high.json) | 74.448567 | 67.874898 | 65.319494 | Keep ordered mapped/prefix A; reject upper32 C; D best is variation |
| [165 /72b040a](board-round165-selected-confirmation.json) | 74.747885 | 68.007047 | 64.983008 | Confirm selected combo; extra A/C bests are variation |
| [167 /b693b45](board-round167-evidence-head.json) | 74.589732 | 68.028087 | 64.772011 | Same-source C higher best is variation |
| [173 /7e77576](board-round173-adjacency-pages.json) | 74.858990 | 67.908361 | 65.097396 | Reject D page storage/advice; A higher best is variation |
| [175 /e8a5109](board-round175-selected-confirmation.json) | 75.112009 | 68.118071 | 63.626140 | Confirm exact restoration; A/C higher bests are variation |
| [177 /5bf3ee3](board-round177-evidence-head.json) | 73.800432 | 67.696567 | 63.885830 | Lower unchanged repeats |
| [178 /42c50ce](board-round178-full-pgo.json) | 75.240074 | 67.771896 | 65.094043 | Small A build best; mixed repeats follow |
| [181 /95c75c7](board-round181-inline-field.json) | 74.755246 | 67.701018 | 64.536399 | Reject field-only C |
| [184 /2a228b4](board-round184-inline-parsers.json) | 75.193276 | 67.826593 | 64.955779 | Reject all-parser C |
| [187 /d6cea74](board-round187-selected-confirmation.json) | 74.989596 | 62.982725 | 64.935358 | Confirm A-PGO/original-C/D; lower C outlier |

Every historical row passes all five gates. Unchanged tracks are repeated observations; higher repeats are variation, not extra algorithms. Exact time/memory/S/K/source/run IDs remain in JSON and PERF logs.

Current selected local images have **A81/C405/D996=1,482** reference invocations, with overlapping semantics explicitly not independent timing samples. A178 has81 exact-image references/3 normal sink errors, new ASAN/UBSAN1913/1931/full1951, TSAN1973 and pinned GCC strict54+3 normal errors. Original A163 OrderedOutput/prefix/cache/mapped-char models stay valid by byte identity; no new protocol. Restored original C freshly replays405 independent184 references/30 normal errors, including new full2039/every worker topology. Original C127 offset/full-key/country/SPSC/quote strict/race models and D104 band/Floyd/race/full64 proofs remain source-bound. Previous original C135228+24 errors/C15748 pressure and D1080 cases remain valid, not new timing samples. Fresh selected187 Make/public1/6/12/native+Linux defaults pass. [Combined public](round187-make-public.json), [defaults](round187-defaults.json), [restored original C](round187-restored-c-image-matrix.json), [final identity](round187-final-source-match.json).

C181 field-only/184 field+integer+amount alter only GNU inlining attributes; every parser body statement/header/key/numeric/pipeline remains exact. Native3.9%/10.9% does not transfer to observed target K22.595417/22.726464 versus23.033578, so restore both. Each rejected source has fresh strict/race/full2027/2039/country/every topology/1MiB/pressure,144 GCC valid+30 errors and405 image valid+30 errors. Those proofs stay historical. Copied184 final captions said181 despite correct executed184 paths/source/input/output hashes; metadata captions were corrected explicitly with original logs/results intact and no runtime fix.

Native-only D180 tail1.015139,183 staging0.990132/0.998705/0.993385/0.994459/1.002234 and185 overwrite arrays1.004704 are flat/losing and unpromoted. Public hashes pass but no new broad primitive/coverage/sanitizer/GCC/image/actual proof. Larger188 one-direction CSR/search saves19,529,728 native RSS bytes but loses1.737101; its new termination/flag-race/full64/strict/GCC/image/default/actual proof was not executed or claimed. Original bidirectional D remains. Prior173 own-page hint passed full proof but lost actual K20.042317 versus20.248361 and remains removed. Earlier own62 allocator provenance/read-only re-evaluation is [documented](round144-event-provenance.json), not an organizer eligibility certificate. No competitor/private/pre-event implementation was imported.

Hourly local optimization stays active while Mac/app are available. Finish exact pending documentation-head records before new runtime pushes. No new reactions; emojis do not change machine ranking. Freeze **2 November2026 15:00UTC/20:30IST**, recorded public MIT source due **16:00UTC/21:30IST**. Repository stays private. Automatic review rejected future private→public publication without specific approval; explicit owner question remains pending. No visibility/grant/credential change is scheduled/performed. Recheck final frozen history before approved publication; heuristic privacy scans are not guarantees.

[Complete feed](round187-confirmed-board.json) · [Feed integrity](round187-feed-proof.json) · [Leader comparison](round187-confirmed-comparison.json) · [Entry audit](ENTRY-AUDIT.md) · [Live board](https://speeddemon.dev/board/#red-jones-00c4a7)
