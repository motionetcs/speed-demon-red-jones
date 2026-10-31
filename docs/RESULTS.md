# Results — 31 October 2026

Complete public feed: **2026-10-31 19:25:13 UTC**. Red Jones is **39th of85** teams with three scored tracks. The best-three machine mean is **68.754000**, up from68.600513 at the prior complete snapshot. Overall leader Cause Of Death has81.805732. We are not number one. Team counts changed, and practice-board best records are separate from final holdout scoring and judging.

| Track | Before retained gains | Best now | Track rank | Track leader |
| --- | ---: | ---: | ---: | --- |
| A | 72.924546 | **73.371413** | 48/101 | Kirk Mates 87.104329 |
| C | 67.750087 | **67.916082** | 44/87 | NickTrapp 83.814878 |
| D | 64.570088 | **65.222044** | 22/89 | Cause Of Death 73.008704 |

Three changes are retained:

- **A:mapped record storage with the accepted endpoint cache.** Actual145 raises72.924546 to73.371413 and K28.740275 to29.337848. Charged memory35,426,304→27,340,800B falls22.82%, while time0.044513→0.046329s is4.08% slower and source424→457 grows. The net K improves2.08%. This is a memory/source/time tradeoff, not a runtime-speed claim or a precise causal estimate from one observation. Completed hour owners return fully consumed record pages directly to the OS. The exact4096 cache/canonical views, four-byte records/full32 escapes, quantiles and original generic/sample PGO stay. Earlier allocator62 used the older interner and64 also changed scalar/native flags; this combination has fresh strict/reference/image proof.
- **C:eight-byte owner entries.** Full length/byte equality follows a32-bit rejection fingerprint; checked indices address stable64KiB word blocks, with dedicated oversized-key blocks. Full64 hashes still route owners. Actual128 raises67.750087 to67.875642, K22.646534 to22.777856; charged memory13,045,760→12,378,112B falls while time0.062192→0.062444s and source660→672 grow. Unchanged137 later measures67.916082/K22.820315; that small extra best is variation, not another algorithm change.
- **D:32-entry query batches.** Same exact64-distance bands, full-width distances, packed labels and conservative stopping rule; only batch8→32 changes. Actual104 raises64.570088 to65.222044, K19.561482 to20.157695. Later identical-source results vary materially; the best observation and native controls support retention without a precise causal timing estimate.

A uses original generic GCC/sample104729+130363 PGO and its original method scanner; failed139 method dispatch is removed. C retains the original parser,8-reader/4-owner512-event dedicated pipeline and full1000003/sample130363 PGO. D retains12 atomic loaders, original cursors/prefixes, exact packed/full64 fallbacks and arena cap2; failed139 weight-map reserve is removed. The owner briefing describes these algorithms without claiming that the owner has read or understood them.

Every28 current runtime/build/metadata input and complete file set exactly matches **348257e4c7f15befbb0cc848e2373d6bad140bd8**, which has all-gates-passing records for every track. The inputs also match each current best-track source. [Source/local-image proof](round145-final-source-match.json) separates exact replayed local image IDs from organizer images, whose IDs are not exposed. Documentation heads are not individually claimed scored without exact records.

| Selected145 track | Actual run | Time | Charged memory | S | K | Points |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| A | run-1fc76115f2d9 | 0.046329s | 27,340,800B | 457 | 29.337848 | 73.371413 |
| C | run-32bb1ce1e233 | 0.062142s | 12,443,648B | 672 | 22.809036 | 67.905347 |
| D | run-3adeecd27501 | 0.204620s | 77,193,216B | 827 | 19.738399 | 64.765597 |

All pass check/build/correctness/timeout/sandbox. A is a confirmed total-K gain. C/D are lower same-source repeats; historical bests remain separate. [Raw selected combination](board-round145-mapped-cache.json).

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

Each historical row passes all five gates. Unchanged tracks are repeated observations, not additional algorithms. Lower outliers remain honest; one observation does not establish statistical causality. Exact time/memory/S/K/source/run identities are in JSON and PERF logs.

Selected local images have **A96/C147/D1080 =1,323** regular fixture replays. Fresh145 combined Make builds, published full hashes at1/6/12 workers and actual native/Linux defaults pass. Each image ID and complete compiled input is checked directly; restricted containers run offline, unprivileged and read-only. [Combined public checks](round145-make-public.json), [defaults](round145-defaults.json) and [final identity proof](round145-final-source-match.json) are separate from official performance measurements.

New mapped/cache A has fresh1697/1699 strict ASAN/UBSAN,1709 TSAN, exhaustive methods×72hours×status×endpoint/escape cases, IDs through4095 and96 extra GCC sanitizer integrations. Fresh native ASAN/UBSAN/TSAN and pinned GCC allocator models assert exact values/growth/alignment/overflow/direct OS release/cross-thread destruction. The source-identical cache/publication/decimal headers retain selected75 provenance. Original Darwin mincore residency versus Linux unmap-error model correction remains recorded, not hidden.

C retains fresh127 offset-specific native/GCC strict models: low32 fingerprints0/1/2/42/deadbeef/MAX with different full64 hashes, forced full-key collisions, every country word through17577, table/block growth, exact full/partial/dedicated1MiB blocks, binary/UTF8 keys, saved indexed bytes, synthetic encoded maxima and arithmetic guards. Original parser/pipeline strict sanitizer/race/country/EOF/cancellation proof remains tied to its bytes. Exact selected C image additionally passes135's228 every-worker valid and24 normal-error invocations, including1MiB quoted keys. The test-only Python CSV capacity is4MiB; frozen reference/harness source is unchanged. Some configurations repeat regular cases; these are actual correctness invocations, not statistically independent timing samples.

D32 retains104 strict sanitizer/reference/native-GCC queue proof,1080 exact selected-image cases and independent Floyd/spread-ID graph references. Changed rejected scanner/loader/AVX2 proofs are not transferred to selected code.

139 A method-length dispatch and D reserve both pass correctness but lose total K and are fully removed. Cooperative133 also loses real K and is reverted despite its fresh cyclic-queue/native/GCC/race/reference proof. That transport proof is not claimed for the restored dedicated C pipeline. C140 lower load factors and142 grouped fingerprint masks are native-only rejects; group4's attractive global median crosses a host speed transition and its paired ratio1.01047 loses. D134 new-prefix compression loses;136 cursor-end variants remain unpromoted and lack independent final-end/lifetime/boundary/GCC/image proof.144 mapped-method has only a native screen; only mapped-cache145 is selected. Exact parents, patches and proof limits are archived. Native Apple timings/RSS and emulated Linux diagnostics are not official Intel/cgroup performance.

Public video and primary performance research remain documented. This pass reviewed Abseil's Swiss-table design note for entropy/filtering concepts; no dependency or implementation was imported. The reused allocator is our own event-written62 code in this fresh repository. An initial timing-command review rejected historical reuse as not demonstrably event-written; read-only root/first-addition timestamps and the actual62 board record established event provenance. The exact same command was then accepted on that evidence, with no alternate execution route. [Provenance/review record](round144-event-provenance.json) is not an organizer eligibility certificate.

Hourly local optimization remains active while this Mac/app is available. Finish outstanding exact head records before new runtime pushes. No new reaction actions occurred; emoji counters do not change machine ranking. Freeze is **2 November2026 15:00UTC/20:30IST**; recorded MIT source must be public by **16:00UTC/21:30IST**. The repository remains private. Automatic review rejected future private-to-public publication without specific approval; the explicit owner question remains pending. No visibility change is scheduled or performed. Recheck final frozen source/history before any approved publication; heuristic privacy scans are not guarantees.

[Complete current feed](round145-confirmed-board.json) · [Feed integrity](round145-feed-proof.json) · [Leader comparison](round145-confirmed-comparison.json) · [Entry audit](ENTRY-AUDIT.md) · [Live board](https://speeddemon.dev/board/#red-jones-00c4a7)
