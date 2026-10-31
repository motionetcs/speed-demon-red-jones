> D173 passes gates but loses K20.042317 versus20.248361; all original165 runtime inputs are restored exactly. Fresh17529-input/public/default/old-image996-reference proof passes; real175 confirmation pending. No new algorithm gain this heartbeat; A173/C167 higher bests are variation.

# Results — 31 October 2026

Complete public feed: **2026-10-31 22:05:22 UTC**. Red Jones is **39th of87** teams with three scored tracks, versus40th/87 at21:28. The best-three machine mean is **69.246615**, up from68.768396. Overall leader Cause Of Death has82.388283. We are not number one. A163 confirms a measured total-K algorithm gain; later A/C/D same-source best increases are variation. Practice-board best records remain separate from final holdout scoring and judging.

| Track | Before retained gains | Best now | Track rank | Track leader |
| --- | ---: | ---: | ---: | --- |
| A | 72.924546 | **74.747885** | 45/104 | Kirk Mates 87.283533 |
| C | 67.750087 | **68.007047** | 44/88 | NickTrapp 83.814878 |
| D | 64.570088 | **65.319494** | 23/91 | Cause Of Death 73.040674 |

Four changes are retained:

- **A:mapped record storage with the accepted endpoint cache.** Actual145 raises72.924546 to73.371413 and K28.740275 to29.337848. Charged memory35,426,304→27,340,800B falls22.82%, while time0.044513→0.046329s is4.08% slower and source424→457 grows. The net K improves2.08%. This is a memory/source/time tradeoff, not a runtime-speed claim or a precise causal estimate from one observation. Completed hour owners return fully consumed record pages directly to the OS. The exact4096 cache/canonical views, four-byte records/full32 escapes, quantiles and original generic/sample PGO stay. Earlier allocator62 used the older interner and64 also changed scalar/native flags; this combination has fresh strict/reference/image proof.
- **A:ordered completion with directly mapped output and bounded prefix8 decoding.** All12 aggregation workers remain. Each completed hour publishes under a mutex; that publisher writes consecutive completed hours and releases mapped output strings. Empty hours also publish, and no worker waits for a missing hour. Final close follows joined workers. A bounded8-byte digit-prefix decoder preserves exact fulluint32/scalar tails. First actual163 raises73.371413 to74.448567, K29.337848 to30.829845 (+5.09%); memory27,340,800→20,787,200B falls23.97%, time0.046329→0.045650s is1.47% lower, and source457→497 grows8.75%. This is the combined design's measured tradeoff, not separate component effects or a precise causal timing estimate. Exact-source165 later reaches74.747885/K31.257749; that extra repeat increase is variation.
- **C:eight-byte owner entries.** Full length/byte equality follows a32-bit rejection fingerprint; checked indices address stable64KiB word blocks, with dedicated oversized-key blocks. Full64 hashes still route owners. Actual128 raises67.750087 to67.875642, K22.646534 to22.777856; charged memory13,045,760→12,378,112B falls while time0.062192→0.062444s and source660→672 grow. Unchanged137 later measures67.916082/K22.820315,147 measures67.958752/K22.865201, and restored165 measures68.007047/K22.916113; these extra bests are variation, not additional algorithm changes.
- **D:32-entry query batches.** Same exact64-distance bands, full-width distances, packed labels and conservative stopping rule; only batch8→32 changes. Actual104 raises64.570088 to65.222044, K19.561482 to20.157695. Unchanged163 later reaches65.319494/K20.248361; that extra best is variation. Later identical-source results vary materially; the best observation and native controls support retention without a precise causal timing estimate.

A uses original generic GCC/sample104729+130363 PGO, original method scanner and the new163 digit-prefix/output path; failed139 method dispatch is removed. C retains the original parser,8-reader/4-owner512-event dedicated pipeline and full1000003/sample130363 PGO. D retains12 atomic loaders, original cursors/prefixes, exact packed/full64 fallbacks and arena cap2; failed139 weight-map reserve is removed. The owner briefing describes these algorithms without claiming that the owner has read or understood them.

Every29 current runtime/build/metadata input and complete file set exactly matches **72b040a4b8673df2b0bb04286bb5583aed76befd**, which has all-gates-passing records for every selected track. Each track's inputs also match its current best source (A/C165, D163). [Source/local-image proof](round165-final-source-match.json) separates exact replayed local image IDs from organizer images, whose IDs are not exposed. Later documentation heads are not individually claimed scored without exact records.

| Selected165 track | Actual run | Time | Charged memory | S | K | Points |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| A | run-62e2cd1dd82a | 0.044266s | 20,955,136B | 497 | 31.257749 | 74.747885 |
| C | run-6843e7f296dc | 0.062469s | 11,997,184B | 672 | 22.916113 | 68.007047 |
| D | run-f74e3afdb0c8 | 0.199941s | 77,795,328B | 827 | 19.937016 | 64.983008 |

All pass check/build/correctness/timeout/sandbox. [Raw selected combination](board-round165-selected-confirmation.json).163's upper32 C fingerprint passed gates but lost K22.777075/67.874898 versus22.865201/67.958752 and is fully restored.165's higher A/C repeats and163's higher D repeat are source-identical variation; only the first changed-code A tradeoff is attributed to a new algorithm. Lower repeats remain honest.

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

Each historical row passes all five gates. Unchanged tracks are repeated observations, not additional algorithms. Lower outliers remain honest; one observation does not establish statistical causality. Exact time/memory/S/K/source/run identities are in JSON and PERF logs.

Selected explicit local images have **A51/C141/D1080 =1,272** regular reference invocations in the selected proof: new A, fresh restored-C cases and retained exact D. Fresh165 combined Make builds, full published input/output hashes at1/6/12 workers and actual native/Linux defaults pass. New A also returns normal errors for exact-production `/dev/full` at1/6/12. Restricted containers remain offline, unprivileged and read-only. [Combined public checks](round165-make-public.json), [defaults](round165-defaults.json) and [final identity proof](round165-final-source-match.json) are separate from official performance.

Current A163 has fresh1783/1787 strict ASAN/UBSAN,1789 TSAN, every method/hour/status/endpoint/escape/ID4095 reference, and every1..12-worker lagging-first-hour/empty-prefix/shuffled-output comparisons. New exact OrderedOutput models test ordered/reversed/shuffled/empty/lag hour publication, complete binary output, mapped char/string growth/NUL/terminator/direct release/cross-thread ownership and normal sink failures under native ASAN/UBSAN/TSAN and pinned GCC strict checks. New prefix8 models compare fulluint64 from_chars/scalar behavior, every byte/position/length/arbitrary suffix and protected-page boundaries. A zero digit count avoids a64-bit shift; for an all-digit word, countr_zero(uint64_t(0))/8 yields8. Original cache/canonical publication and mapped allocator header bytes retain145/75 provenance; char instantiation and combined integration are freshly proved.

Combined exact A/C GCC strict production123 integrations plus3 deferred sink errors pass. The initial wrapper checked cat-replayed messages in stderr although cat wrote stdout; it was corrected and the complete matrix rerun, with no runtime fix. Exact-image regular counts include overlapping configurations; they are correctness invocations, not independent timing samples.

C retains fresh127 offset-specific native/GCC strict models: low32 fingerprints0/1/2/42/deadbeef/MAX with different full64 hashes, forced full-key collisions, every country word through17577, table/block growth, exact full/partial/dedicated1MiB blocks, binary/UTF8 keys, saved indexed bytes, synthetic encoded maxima and arithmetic guards. Original parser/pipeline strict sanitizer/race/country/EOF/cancellation proof remains tied to its bytes. The original selected C image retains135's228 every-worker valid and24 normal-error invocations, including1MiB quoted keys. That same original image retains157's48 all1..12-worker one-owner pressure invocations (4095/4096/4097/262161 rows, escaped UTF8, LF/BOM, unmatched groups and exact cents), with input/reference hashes in round157-selected-pressure.json. The test-only Python CSV capacity is4MiB; frozen reference/harness source is unchanged. 165 also freshly replays141 reference configurations from new163 untrained/country/pipeline/topology/pressure fixtures on the restored original C image. The rejected upper32 model is not transferred to low32 placement. Some configurations repeat regular cases; these are actual correctness invocations, not statistically independent timing samples.

D32 retains104 strict sanitizer/reference/native-GCC queue proof,1080 exact selected-image cases and independent Floyd/spread-ID graph references. Changed rejected scanner/loader/AVX2 proofs are not transferred to selected code.

139 A method-length dispatch and D reserve both pass correctness but lose total K and are fully removed. Cooperative133 also loses real K and is reverted despite its fresh cyclic-queue/native/GCC/race/reference proof. That transport proof is not claimed for the restored dedicated C pipeline. C140 lower load factors and142 grouped fingerprint masks are native-only rejects; group4's attractive global median crosses a host speed transition and its paired ratio1.01047 loses. D134 new-prefix compression loses;136 cursor-end variants remain unpromoted and lack independent final-end/lifetime/boundary/GCC/image proof.144 mapped-method has only a native screen; only mapped-cache145 is selected. Exact parents, patches and proof limits are archived. Native Apple timings/RSS and emulated Linux diagnostics are not official Intel/cgroup performance.

151 and155 have their own fresh strict native/GCC/TSAN models, independent/adversarial/reference tests, all-topology/pressure cases, pinned offline images, defaults and exact source proofs.151 C had285 regular image replays and155 C/D285/1080, plus explicit extra invocations. These are historical candidate proofs, not replacements for the restored original pipeline/atomic-degree proofs.148's bounded whole-key hardware CRC32C also lost natively; independent polynomial/all-byte/guard-page ARM/SSE4.2/fallback checks pass, but no CRC code is selected. Primary CRC intrinsic and C++20 handoff/join references are recorded in round148-hash-models.json and candidate PERF logs; no external implementation was imported.

160 D prefix8 is effectively flat natively (paired0.996491).161 parallel private2 packed-low reduction adds only a small difference over already-losing155 serial control (paired0.902018 versus0.905690 relative to original); private8 parallel0.914875 is slower. They remain public-hash/native screens without broad changed-protocol proof or official promotion.162 separately screens ordinary/mapped ordered output and prefix8, then163's extracted exact header receives its own paired screen (A0.930811, C0.977752). C's global medians cross a host regime and are not read as a causal global speedup. No native RSS saving was asserted for A; its memory claim comes from actual163 charged memory.

Primary C++20 mutex and bit-counting references support the new protocol/count0 reasoning. MIT's public counting/radix lecture page and typed notes were read; its embedded YouTube fetch failed and no watched-video claim is made. Radix quantiles and Linux hugepage advice remain unimplemented hypotheses, with no measured gain or host/harness changes. References and exact limits are in round160-163-research.json.

Public video and primary performance research remain documented. Earlier work reviewed Abseil's Swiss-table design note for entropy/filtering concepts; no dependency or implementation was imported. The reused allocator is our own event-written62 code in this fresh repository. An initial timing-command review rejected historical reuse as not demonstrably event-written; read-only root/first-addition timestamps and the actual62 board record established event provenance. The exact same command was then accepted on that evidence, with no alternate execution route. [Provenance/review record](round144-event-provenance.json) is not an organizer eligibility certificate.

Hourly local optimization remains active while this Mac/app is available. Finish outstanding exact head records before new runtime pushes. No new reaction actions occurred; emoji counters do not change machine ranking. Freeze is **2 November2026 15:00UTC/20:30IST**; recorded MIT source must be public by **16:00UTC/21:30IST**. The repository remains private. Automatic review rejected future private-to-public publication without specific approval; the explicit owner question remains pending. No visibility change is scheduled or performed. Recheck final frozen source/history before any approved publication; heuristic privacy scans are not guarantees.

[Complete current feed](round165-confirmed-board.json) · [Feed integrity](round165-feed-proof.json) · [Leader comparison](round165-confirmed-comparison.json) · [Entry audit](ENTRY-AUDIT.md) · [Live board](https://speeddemon.dev/board/#red-jones-00c4a7)
