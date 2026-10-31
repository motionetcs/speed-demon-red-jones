# Results — 31 October 2026

Complete public feed: **2026-10-31 18:45:00 UTC**. Red Jones is **40th of84** teams with three scored tracks. The best-three machine mean remains **68.600513**. The earlier pass raised it from68.328988; this heartbeat has no new confirmed algorithm gain. Overall leader Cause Of Death has81.805732. We are not number one. Practice-board best records are separate from final holdout scoring and judging.

| Track | Before earlier gains | Best now | Track rank | Track leader |
| --- | ---: | ---: | ---: | --- |
| A | 72.924546 | **72.924546** | 49/99 | Kirk Mates 87.104329 |
| C | 67.750087 | **67.875642** | 42/84 | NickTrapp 83.814878 |
| D | 64.570088 | **65.222044** | 21/88 | Cause Of Death 73.008704 |

The two earlier improvements remain selected:

- **D:32-entry query batches.** Same exact64-distance bands, full-width distances, packed labels and conservative stopping rule; only the batch rises from8 to32. Actual104 raises best64.570088 to65.222044, K19.561482 to20.157695. Run-deabebbc1efe uses0.195926s,77,459,456 charged bytes,S827. Later identical-source observations are lower; this is a real best observation with material variation, not a precise causal speed estimate.
- **C:eight-byte owner entries.** Full length/byte equality remains after a32-bit rejection fingerprint; checked block/word indices address stable64KiB name/country storage, with dedicated oversized blocks. Full64-bit hashes still route owners. Actual128 raises best67.750087 to67.875642, K22.646534 to22.777856. Runtime is roughly flat/slightly slower0.062192→0.062444s, charged memory13,045,760→12,378,112 bytes and S660→672. Retain the measured total-score tradeoff; no runtime speedup is claimed.

A retains the already scored exact4096-entry endpoint cache, canonical input views, lossless four-byte records, lazy hour storage and original generic GCC/sample104729/130363 PGO. C retains the original CSV/header/region/record-boundary parser,8-reader/4-owner512-event pipeline, canonical name encoding and full1000003/sample130363 PGO. D retains the original12-worker atomic compact loader, exact packed-label/full64 fallbacks, arena cap2 and32-entry search. The owner briefing describes the actual selected algorithms.

Every27 current runtime/build/metadata input and complete file set exactly matches **2b3834d73ef6f61ce1bc2bed43d8e9b75e07d300**, byte-identical to the selected128 runtime, which has real all-gates-passing records for every track. [Exact source/image identity](round135-final-source-match.json) ties the current selection to its own evidence. Further PERF/prose/report changes preserve compiled inputs; documentation heads are not claimed individually scored unless an exact run was captured.

| Selected135 track | Actual run | Time | Charged memory | S | K | Points |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| A | run-b611fb45a28d | 0.045414s | 35,229,696B | 424 | 28.485435 | 72.731143 |
| C | run-c71ee4a7dbf1 | 0.095021s | 12,017,664B | 672 | 18.574421 | 63.445764 |
| D | run-15059e2111e9 | 0.200157s | 77,668,352B | 827 | 19.932767 | 64.978380 |

All pass check/build/correctness/timeout/sandbox. All three are lower same-source repeats, including a slow C outlier; historical bests and this actual confirmation remain separate. [Raw selected restoration](board-round135-selected-confirmation.json).

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

Each row passes all five gates. Unchanged tracks are repeated observations, not extra algorithms. Lower outliers are preserved honestly; one observation does not establish statistical causality. Exact time/memory/S/K/source/run identities are in the JSON and PERF logs.

Selected images have **A96/C147/D1080 =1,323** independent Linux fixture replays. Fresh combined Make builds, full-public hashes at1/6/12 workers and actual native/Linux defaults pass. Each image ID and its complete compiled inputs are checked directly. Restricted containers run offline, unprivileged and read-only. [Combined public checks](round135-make-public.json), [defaults](round135-defaults.json) and [source/image/model proof](round135-selected-source-match.json) are separate from official performance measurements.

Restored C also passes **228 additional every-worker valid and24 normal-error production-image invocations** on the new independent black-box suite. It covers64/128/256/512 seams, empty/partial/EOF streams, skew/diverse names and1MiB quoted records at every1..12 worker topology. The test-only Python CSV oracle capacity is4MiB for the synthetic large key; official reference/harness source is unchanged. Some configurations repeat the regular suite; these are actual correctness invocations, not statistically independent timing samples.

The rejected133 cooperative pipeline received fresh1619/1621 sanitizer,1627 race checks and native/GCC independent fully primed cyclic queue transport/name/event models, plus261 regular/new-reference image runs and an every-worker matrix. It still loses actual K21.998877 versus22.777856: runtime0.067282 versus0.062444s and source S676 versus672 outweigh memory12,169,216 versus12,378,112. Every cooperative source byte is removed from the selection. Its callbacks/progress/race proof belongs to that rejected version.

C has fresh1607/1609 address/undefined-behavior sanitizer and1613 race checks, every country width/every1..12 worker EOF/progress/reference/cancellation test, and a new independent offset-specific model under native/GCC strict sanitizers. It covers low32 fingerprints0/1/2/42/deadbeef/MAX with distinct full64 hashes, full key collisions, every country word through17577, table/block growth, exact full/partial/dedicated1MiB blocks, long binary/UTF8 keys, saved indexed bytes, synthetic encoded maxima and arithmetic guards. The old private-model dispatch also executes under both compilers; its pointer-based assertions are not substituted for offset proof.

A's unchanged cache/publication/guard/collision/escape proof retains exact75 provenance. D32 has fresh104 strict sanitizer/reference/native-GCC queue proof plus explicit1080 selected-image cases and independent Floyd/spread-ID graph references. Rejected scanner/loader/AVX2 models stay tied to their own bytes; no changed-source evidence is silently transferred to selected code.

Additional native-only screens reject numeric SWAR, alternate parser streams, borrowed keys, output scheduling, percentile variants, raw record arrays, direct endpoint slabs, sampled name hashes, readonly-prefix compression and final-cursor/reserve variants. Exact parents/patches/proof limits are archived.129's sampled-hash global medians are misleading under a host speed-regime transition; within-rotation ratios are flat. No such prototype is submitted. Native Apple timings/RSS and emulated Linux diagnostics are not official Intel/cgroup performance. Public research covered the requested videos and primary performance literature; no competitor implementation or pre-event private solution was imported.

Hourly local optimization continuation is active. It requires this Mac/app to remain available, finishes outstanding exact runs before another runtime push and stops runtime edits at freeze. Cooperative reader+owner133 is fully tested but loses real K and is reverted. D136 final-cursor/reserve prototypes have only native screens and remain outside the entry; they need independent end/boundary/ownership/sanitizer/GCC/image/real-score proof. No new emoji actions occurred this pass; reactions do not affect machine ranking.

Freeze is **2 November2026 15:00UTC/20:30IST**. Recorded MIT source must be public by **16:00UTC/21:30IST**. The repository is private now. Automatic approval review rejected future private-to-public publication without specific approval; the explicit owner question remains pending. No visibility change is scheduled or performed. Privacy scans are heuristic and must be repeated on the final frozen history before any approved publication.

The observable entry audit passes; it is not an organizer eligibility certificate or an invented claim of owner understanding. Fresh event-written code, MIT attribution and AI disclosure remain intact.

[Complete feed](round135-confirmed-board.json) · [Leader comparison](round135-confirmed-comparison.json) · [Entry audit](ENTRY-AUDIT.md) · [Live board](https://speeddemon.dev/board/#red-jones-00c4a7)
