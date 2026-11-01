# Results — 1 November 2026

Complete ordinary public feed **2026-11-01T02:14:50Z**: Red Jones remains **41st of 90** with best-three machine mean **69.436015**. Leader Cause Of Death has **82.832135**. We are not number one. No supported new score gain this cycle: C204 shifted home passes every gate but K23.020854 loses23.033578. It is fully restored, and selected206 passes all three tracks. Public bests and final holdout/judging remain separate.

| Track | Best points | K | Rank | Leader |
| --- | ---: | ---: | ---: | --- |
| A | 75.240074 | 31.974332 | 43/107 | Cause Of Death 87.660386 |
| C | 68.118071 | 23.033578 | 46/91 | NickTrapp 83.814878 |
| D | 65.319494 | 20.248361 | 26/93 | Cause Of Death 73.226910 |

Four changes are retained:

- **A:mapped record storage with the accepted endpoint cache.** Actual145 raises72.924546 to73.371413 and K28.740275 to29.337848. Charged memory35,426,304→27,340,800B falls22.82%, while time0.044513→0.046329s is4.08% slower and source424→457 grows. The net K improves2.08%. This is a memory/source/time tradeoff, not a runtime-speed claim or a precise causal estimate from one observation. Completed hour owners return fully consumed record pages directly to the OS. The exact4096 cache/canonical views, four-byte records/full32 escapes, quantiles and original generic/sample PGO stay. Earlier allocator62 used the older interner and64 also changed scalar/native flags; this combination has fresh strict/reference/image proof.
- **A:ordered completion with directly mapped output and bounded prefix8 decoding.** All12 aggregation workers remain. Each completed hour publishes under a mutex; that publisher writes consecutive completed hours and releases mapped output strings. Empty hours also publish, and no worker waits for a missing hour. Final close follows joined workers. A bounded8-byte digit-prefix decoder preserves exact fulluint32/scalar tails. First actual163 raises73.371413 to74.448567, K29.337848 to30.829845 (+5.09%); memory27,340,800→20,787,200B falls23.97%, time0.046329→0.045650s is1.47% lower, and source457→497 grows8.75%. This is the combined design's measured tradeoff, not separate component effects or a precise causal timing estimate. Exact-source165 later reaches74.747885/K31.257749,17374.858990/K31.418092 and17575.112009/K31.786315; these extra repeat increases are variation.
- **C:eight-byte owner entries.** Full length/byte equality follows a32-bit rejection fingerprint; checked indices address stable64KiB word blocks, with dedicated oversized-key blocks. Full64 hashes still route owners. Actual128 raises67.750087 to67.875642, K22.646534 to22.777856; charged memory13,045,760→12,378,112B falls while time0.062192→0.062444s and source660→672 grow. Unchanged137 later measures67.916082/K22.820315,147 measures67.958752/K22.865201, restored165 measures68.007047/K22.916113,16768.028087/K22.938327 and17568.118071/K23.033578; these extra bests are variation, not additional algorithm changes.
- **D:32-entry query batches.** Same exact64-distance bands, full-width distances, packed labels and conservative stopping rule; only batch8→32 changes. Actual104 raises64.570088 to65.222044, K19.561482 to20.157695. Unchanged163 later reaches65.319494/K20.248361; that extra best is variation. Later identical-source results vary materially; the best observation and native controls support retention without a precise causal timing estimate.

A178 changes only the first build-time training104729/sample→1000003/full, keeping130363/sample, generic GCC flags and every C++/header byte unchanged. First actual raises75.112009→75.240074 and K31.786315→31.974332 (+0.59%); T0.042786→0.042474s, M20,979,712→20,746,240B, S497 unchanged. Later same-build repeats are mixed and mostly lower. Retain the modest observed best-build choice without a robust causal timing estimate or promised holdout gain. This is not another algorithm gain. Only the executable enters the final image; public seed1 is never trained.

A retains163 ordered mapped-output/prefix8/exact4096 cache. C is fully original std::hash/low32 offset/eight-reader/four-owner/512-event with original16-byte quote scan. A/C/D use full1000003/sample130363 offline PGO. D retains12 atomic degree/cursor workers, bidirectional CSR/band64/query32 and arena2. Every new native-ISA/CRC/AVX-quote/radix/weight-skip/query-order prototype is absent. OWNER-BRIEFING describes actual techniques without claiming personal understanding.

All29 inputs and complete runtime/build file sets match real all-gates selected206/e3140e077305a38dec3e5262047b4247c2f04e3e and current best sources(A178,C175,D163). [Final source/local-image proof](round206-final-source-match.json) distinguishes replayed local IDs from unexposed organizer IDs. Later documentation heads are not individually claimed scored.

| Selected206 | Run | Time | Charged memory | S | K | Points |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| A | run-0a6037d481be | 0.042878s | 21,123,072B | 497 | 31.708979 | 75.059113 |
| C | run-5334e2cb1c9b | 0.062146s | 12,095,488B | 672 | 22.938120 | 68.027891 |
| D | run-8aafc980cbd1 | 0.195398s | 76,959,744B | 827 | 20.211057 | 65.279451 |

All check/build/correctness/timeout/sandbox gates pass. [Raw selected record](board-round206-selected-confirmation.json). Latest points remain below bests. Earlier original-C1870.098959s/62.982725 outlier is preserved without an invented regression or target-phase explanation.

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
| [189 /ceb78f8](board-round189-evidence-head.json) | 74.830719 | 68.012076 | 65.217619 | Lower unchanged repeats |
| [190 /1cd2a7b](board-round190-avx2-quote.json) | 74.798766 | 68.018544 | 64.676878 | Reject AVX2 quote C on total K |
| [195 /10e3ade](board-round195-native-a-crc-c.json) | 74.896922 | 67.638157 | 65.138504 | Reject native A and Intel CRC C |
| [197 /8003961](board-round197-selected-confirmation.json) | 74.807361 | 68.089996 | 65.106296 | Confirm complete original runtime restoration |
| [199 /d4027c9](board-round199-evidence-head.json) | 75.067694 | 67.869194 | 65.068289 | Lower unchanged repeats |
| [204 /0112b33](board-round204-shifted-offset-home.json) | 74.476487 | 68.106072 | 65.196098 | Reject shifted home C on total K |
| [206 /e3140e0](board-round206-selected-confirmation.json) | 75.059113 | 68.027891 | 65.279451 | Confirm complete original-source restoration |

Every historical row passes all five gates. Unchanged tracks are repeated observations; higher repeats are variation. Exact time/memory/S/K/source/run IDs remain in JSON and PERF logs.

Current selected local images have **A81/C501/D996=1,578** regular reference invocations, with overlapping semantics explicitly not independent timing samples. Original A81 independent194 references/full2221 remains exact. Restored original C freshly replays501 independent204 references/full2281/all requested workers+30 errors. Synthetic CRC-pair inputs do not activate CRC on std::hash. Original A163 output/prefix/cache/mapped-char, C127 offset/full-key/country/SPSC/quote strict/race and D104 band/Floyd/race/full64 proofs remain source-bound, with D175996 image cases. Older original-C193501/C135228+24/C15748 and D1080 cases remain valid, not extra independent timings. Fresh206 Make/public1/6/12 and actual native/Linux defaults pass. [Combined public](round206-make-public.json), [defaults](round206-defaults.json), [restored original C](round206-restored-c-image-matrix.json), [identity](round206-final-source-match.json).

Rejected190 C AVX2 quote search has fresh all-byte/logical-end/protected-page models on actual AVX2/SSE2/scalar and native NEON/scalar, strict/race/full2129/country/topology/pressure/errors,144 GCC valid+30 errors and405 exact-image valid+30 errors. Actual K22.928248 loses23.033578 despite T0.061274s versus0.062531s; memory12,419,072 versus11,665,408B and S682 versus672 contribute. These are observations, not a precise causal decomposition.

Rejected193 Intel-only CRC hashes every byte and preserves full-key equality; its32-bit CRC state has32 bits of entropy even after64-bit mixing. Fresh polynomial/fallback/all-byte/tail/guard/offset/full-country/genuine CRC collision models, strict/race/full2203/every topology/pressure/errors,168 GCC valid+30 errors and501 exact-image valid+30 errors pass. Actual195 K22.530101/67.638157 loses23.033578/68.118071; M12,578,816B and S730 grow. No collisions are ignored. New194 native GCC A has fresh prefix/output/guard/strict/race/full2221/GCC54+3/image81+3/public/default proofs, but actual195 K31.473022/74.896922 loses31.974332/75.240074. Both complete changes are removed, including CRC header and Make dependency. Their instruction-path proofs are historical to rejected images. No ARM/emulated timing is called Intel timing.

Native-only191 exact radix multi-selection thresholds512/1024/4096 has paired1.003608/0.994278/0.999865;192 D sort/reverse batches1.053645/1.002301;196 D first-pass unused-weight lexical skip1.003300. Public hashes pass, but all are flat/losing and rejected before broad new primitive/adversarial/strict/race/GCC/image/default/actual proofs. No generic correctness or target-K gain is claimed. Earlier rejected D180/183/185/188 and C181/184 remain documented with their original limits. Read-only198 C country-cardinality profiles show76.4% of two independent sample names in≤4 countries, but only0.515% on untrained full2203; naive four-inline plus full-bitmap fallback would add787,576 membership-payload bytes on full. It was not implemented. Payload estimates are not charged memory, timing or K.

Research includes primary Clang/GCC intrinsic/ISA documentation, MIT's own radix-sort lecture page and the official kickoff-video transcript's machine/build/scoring sections. No claim of playing video. Frozen specs take precedence over older transcript narration. Only fresh event-written code is used; own historical62/148 provenance is recorded, with no competitor/private/pre-event implementation imported. Heuristic checks and provenance are not organizer eligibility certificates.


204 changes only three home/grow/retry expressions on the newer128 eight-byte offset table, keeping original std::hash/full-key/country/parser/queue/PGO. The older77 sixteen-byte-table loss was not this combination. Native paired0.925304 motivates fresh204 proof: native/GCC strict offset/index std::set models with low2 aliases/MAX/wrap/all1..11 owner growth,2251/2267 ASAN/UBSAN/full2281,2273 TSAN, every country/topology/pressure/error case, GCC168+30 and exact-image501+30, public/defaults all pass. Actual204 T0.061410/M12,238,848/S672/K23.020854/68.106072 loses old T0.062531/M11,665,408/S672/K23.033578/68.118071. Lower observed time does not overcome memory in this total-K record; no precise causal decomposition is claimed. Restore complete names/README to d4027c9 and original C263 image. New shifted-home proofs remain historical, [scored identity](round204-scored-source-match.json).

200 read-only space-run key analysis saves only3400–3960 rounded bytes across independent samples/full2203, so no compression is implemented.201 bounded2/4/8 A cache probes paired1.005356/0.992900/0.994820 are flat;202 C event24 paired0.942004 is unselected;203 D from_chars1.154143/single-separator1.006474 lose. Public hashes pass but these source changes have no new broad generic/guard/strict/race/GCC/image/actual proof and remain absent. Single-separator may reject outside-grammar multiple whitespace and is not selected. Associativity research motivates examining conflicts, with no random-hash/LRU theorem claimed for the sampled cache.

[207 design](round207-radix-csr-plan.json) proposes a substantial parse-once/parallel stable-radix D CSR construction replacing degree/cursor atomics. It is design only, not implemented or measured. A rough memory/time sketch is explicitly not cgroup/K evidence. Typed MIT radix notes and C++20 vector-capacity semantics were read; no video-playback or imported code claim. Current bidirectional D remains selected.

Hourly local continuation remains active while Mac/app are available. Finish exact pending documentation-head records before new runtime pushes. No new reactions; emojis do not change machine ranking. Stop runtime edits at **2 November2026 15:00UTC/20:30IST** and preserve the last passing recorded source. The owner explicitly approved **only motionetcs/speed-demon-red-jones becoming public under MIT during15:00–16:00UTC/20:30–21:30IST**, after freeze preservation and final secret/privacy recheck. [Authorization](PUBLICATION-AUTHORIZATION.json) and the accepted automation update resolve the earlier missing-approval condition. Keep private before that window; no grants/credential changes or rejection bypass. Publication has not happened. Verify public MIT source by16:00UTC, pause heartbeat after deadline and report verified status. After freeze no runtime edits.

[Complete feed](round206-confirmed-board.json) · [Feed integrity](round206-feed-proof.json) · [Leader comparison](round206-confirmed-comparison.json) · [Entry audit](ENTRY-AUDIT.md) · [Live board](https://speeddemon.dev/board/#red-jones-00c4a7)
