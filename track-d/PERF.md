# Track D optimization log

These are local macOS ARM whole-process measurements including launch, not official scores. Raw runs and source fingerprints are in `../docs/experiments-local.json` and `../docs/experiments-d-full.json`. First scored board run: **run-3e323bfac066**.

| Experiment | Dataset / workers | Binary-heap median | Radix-heap median | Decision | Board run ID |
| --- | --- | ---: | ---: | --- | --- |
| Monotone integer queue | sample seed 1 / 3 | 0.06862 s | 0.05427 s | Keep for wider validation | Unavailable |
| Independent-seed check | sample seed 19 / 3 | 0.08294 s | 0.05812 s | Keep for wider validation | Unavailable |
| Full public check | full seed 1 / 6 | 1.00991 s | 0.65914 s | Keep; about 34.7% less time | Unavailable |

The hypothesis was that integer distances and monotone extraction could avoid comparison-heap work. Every configuration was warmed, then baseline/candidate order alternated across seven measured runs apiece. Every output matched its reference or the published full-data SHA-256.

For the radix candidate on full public data, three workers had a 0.87391 s median and 198.4 MB maximum process RSS across the measured runs; six had 0.65914 s and 245.6 MB. The default is six, with an environment override retained for board tuning. Native RSS includes mapped pages and is not the official cgroup counter; no official K is inferred from these numbers.

Baseline source is archived under `../tools/experiment-baselines`; the original flag name in those snapshots is translated by the experiment runner. The final source includes only the adopted radix implementation. The organizer's formatter/scc measured the adopted track at 272 source lines. Full public differential checks, independent random graphs, sanitizer checks, and restricted Linux x86-64 container checks verify the adopted candidate. The first real board record is retained below.

## First official live-board run

The organizer's full-public-seed-1 run passed check, build, correctness, timeout, and sandbox gates. This is one live-board run, not the final holdout/judging result.

| Field | Observed value |
| --- | --- |
| Run ID | `run-3e323bfac066` |
| Commit | `788ae3b205928ca2bc3d60100703d5660123d0f0` |
| Finished UTC | 2026-10-31T03:57:25Z |
| Process wall time | 0.995951 s |
| Cgroup peak memory | 146,251,776 bytes |
| Measured source size S | 272 lines |
| Dependency weight D | 1 |
| K | 9.302573 |
| Live machine points | 48.430154 |

Source: [official board JSON](https://s3.amazonaws.com/raptors.dev/speeddemon.dev/2026/board/board.json); exact records are retained in `../docs/first-board-run.json`. The board time includes parsing, preprocessing, queries/aggregation, and output. Compare future changes on this same machine rather than interpreting differences from Apple ARM development timings as an optimization result.

## Bidirectional search, parallel loading, and compact exact labels

A first bidirectional prototype reduced explored nodes from 23,227,082 to 7,123,694, but reverse-graph construction and private sparse-map overhead limited the whole-process benefit. Phase measurements are in `../docs/opt-d-phase-profile.json`; these are instrumented local measurements, not board timings. No isolated official improvement is claimed for that prototype.

The refined candidate parses once with up to four workers, constructs both CSR directions by disjoint parallel scatter, and uses query-owned shared atomic labels with private exact fallback for overlap and large distances. A lossless six-byte edge representation stores exceptional weights in an exact side table. Local five-trial medians at six workers were 0.966000 s original versus 0.529270 s candidate; at twelve, 0.902310/0.521800 s. All outputs matched. Report: `../docs/opt-d-packed-shared-native.json`.

An unpacked shared-label prototype measured faster locally (about 0.503 s at six workers) but uses more graph memory. Packing is submitted as a score tradeoff hypothesis; only actual board K can resolve it. Reports preserve both experiments rather than claiming packing itself was a speedup.

The final candidate passes generated tiny data, independent sample seeds 23/41, full public hashes at 1/6/12 workers, independent all-pairs graphs including sentinel-boundary weights, and the long-chain/64-bit path case. Address/undefined-behavior and thread sanitizer reports are `opt-d-packed-final-*.json`; full Linux output passed in `opt-c-compact-d-packed-container.json`. Linux GCC15 caught a packed-field forwarding error during local validation; copying the destination to an aligned local fixed it before submission. All final checks pass. The first real board result for this algorithm is pending.

## Refined candidate: actual board record

`run-b6c7076da0ce` on `072ce9b9046484a76c7e98aebd1e998e0d440d17` passed every gate: T=0.547406 s, M=191,918,080 bytes, S=491, K=10.876457, machine points=51.824372. Record: `../docs/board-opt-refined-acd.json`.

Next experiment: `-march=native` in the Docker build. The official harness explicitly builds native-targeted submissions on the scoring CPU. Offline emulated Linux full-data and tiny hashes pass for all three tracks; reports `opt-native-cpu-containers-{public,tiny}.json`. Emulated timings are not performance evidence for Intel. Source algorithms are unchanged for this compilation experiment.

## Second parse versus retained edge tuples

The next loader candidate counts degrees first and reparses the same immutable input into disjoint CSR ranges, eliminating the temporary edge-tuple vectors. Five alternating full-data trials at six workers measured 0.405384 s one-pass versus 0.494863 s two-pass; at twelve, 0.382537/0.434677 s. Peak local process RSS fell from about 296.6 MB to 264.4 MB at six workers. These local RSS numbers include file pages and are not board memory. Record: `opt-d-two-pass-native.json`.

This is a runtime/memory tradeoff, not a claimed local speedup. Only the actual board K can justify it. Both variants retain exact bidirectional radix search and lossless weights. The candidate passes independent seeds, the public hash at 1/6/12 workers, sentinel-boundary all-pairs cases, long-chain paths, memory/UB and race sanitizers, and offline Linux checks. Reports: `opt-d-two-pass-*` and `opt-c-borrowed-d-two-pass-*`.

## Native compilation: actual board record

`run-d7993624646f` on `f6b17e3b4d532d0dec3952df9da6d8d4297323de` passed every gate: T=0.546072 s, M=192,245,760 bytes, S=491, K=10.886019, machine points=51.843455. Record: `../docs/board-opt-native-cpu.json`.

Native targeting is effectively flat versus K=10.876457; the tiny difference is not claimed as a demonstrated compiler gain. It remains enabled for the separately tested next loader experiment.

## Memory experiment: actual board record

`run-f813e2d591b2` on `28402fefb8136c3db205d3e312c87eef3b87b29f` passed every gate: T=0.55419 s, M=131,211,264 bytes, S=489, K=11.670991, machine points=53.355387. Record: `../docs/board-opt-memory-cd.json`.

Reparsing reduced board memory from 192,245,760 to 131,211,264 bytes. Despite a small runtime increase, K rises from 10.886019 to 11.670991, so the lower-memory loader is retained.

The next comparison changes only the query-worker default from six to twelve. Prior full-data, sample, memory/UB and race tests exercise both counts. The new build additionally passed full public output with the environment override absent and offline Linux validation. Local two-pass medians at six/twelve workers were 0.494863/0.434677 s; actual board K decides the default. Reports: `opt-d-twelve-*.json`.

## Parser / D-worker comparison: actual board record

`run-4b7dcbc9bc49` on `c21563dbfc44b1504bf8cc5d05f7fceaa8cbf1dd` passed every gate: T=0.606544 s, M=131,170,304 bytes, S=489, K=11.15663, machine points=52.376652. Record: `../docs/board-opt-parser-a-d12.json`.

Twelve workers scored lower than six (K11.156630 versus 11.670991), despite the opposite local timing preference. Restore six. The retained source matches the earlier passing six-worker loader and has been rechecked with full native and Linux hashes. No score increase is claimed for twelve.

## Retained source confirmation

`run-9da2b9e55b4a` on `07f2ac73092f64d98e40825809e88ce7010dca9f` passed every gate at 2026-10-31T04:57:45Z: T=0.59086 s, M=131,555,328 bytes, S=489, K=11.297109, machine points=52.648366. Full record: `../docs/board-opt-retained-acd.json`.

This confirms the retained source rather than a new optimization. A/C algorithms are unchanged from the prior parser comparison; D restores the earlier tested six-worker loader. The spread between unchanged-source practice runs is real, so best observed values and the latest confirmation are reported separately. Final holdout and judging remain separate.

## Second optimization round

A forward-only graph/compact-queue prototype was exact on tiny/adversarial/full hashes but slower locally:1.400753 s versus0.757233 s for the retained bidirectional code. It is rejected without submission. The compact queue passes independent model tests with monotonic observations; an initial test wrongly inserted keys below a previously peeked minimum and was corrected to mirror Dijkstra's peek-then-extract contract. D remains the already-scored six-worker bidirectional source for the next A/C board comparison.

Local phase intervals and alternating trials are in `../docs/round2-phase-profile.json` and `round2-layout-native.json`. They are Apple ARM development evidence, not official times.

## Hour-layout / compact-lookup board result

`run-56672466bea0` on `d2fd0b53b6cf42a8786845b5d40c21e30865a8ce` passed all gates: T=0.6646 s, M=131,371,008 bytes, S=489, K=10.654945, machine points=51.377561. Exact record: `../docs/board-round2-ac.json`.

D source is unchanged here; its slower repeat is measurement variation, not an algorithm change. The next candidate preserves bidirectional search while replacing large shared query labels with compact private labels and using atomic CSR loaders without per-loader degree arrays. Local median0.714331→0.542431 s, about24% lower. Fast queue/labels preserve exact uint32-boundary and 64-bit fallback cases. Reports `round2-d-compact-*`, `round2-cd-final-*`, `round2-c-delimiter-d-private-native.json`; all primitive-model, sample, full hash, memory/UB, race, and Linux checks pass.

## Allocator / delimiter / private-D board result

`run-b1e5e524a029` on `b5df2af979bda869c0827b4dd59fda40f5a1ebe8` passed all gates: T=0.545416 s, M=97,906,688 bytes, S=536, K=12.303438, points=54.501325. Record: `../docs/board-round2-private-d.json`.

Private compact bidirectional labels/queues and shared atomic loading improve observed K from11.670991 to12.303438, with memory falling from131.21 MB to97.91 MB. This D design is retained.

## Offline profile-guided compiler experiment

Next experiment changes only the build: GCC profile generation with atomic counters, two sample datasets generated at seeds104729/130363, then profile-use recompilation with missing-profile errors enabled. The training generator is a byte-identical official copy, explicitly exempt from source size by the published harness; only `/solution` enters the final runtime stage. No public seed1 input, training dataset, cached result, or profile file enters that runtime image. The current algorithms/worker counts are unchanged from the preceding board comparison.

Offline Linux full-public/tiny outputs and129 untrained sample/adversarial runs across1/6/12 workers pass collectively. Reports: `round2-pgo-containers-{public,tiny}.json`, `round2-pgo-untrained-containers.json`. Untrained cases include name-table growth, quoted seams/EOF, percentile boundaries, and full-width graph distances. Actual board K decides retention; no compiler speedup is claimed in advance.

## PGO: exact board result

`run-ce8ecbc13319` on `18896fe59b2dfd93036b023388f29dd0a4108449` passed every gate: T=0.512696 s, M=95,293,440 bytes, S=538, K=12.751689, points=55.278386. Record: `../docs/board-round2-pgo.json`. This improves the preceding private-label build, so D retains PGO.

Next hypothesis: retain exact labels while grouping queue keys into64-distance bands and prefetching batches of8 entries. Five alternating full-data trials measured0.620287 s exact queue,0.528679 s bands and0.501935 s batches on Apple ARM; these are local selection evidence only. Independent Floyd–Warshall checks cover256 graphs/85,871 answers; queue/map/guard-page models, sanitizers, new seeds, full hashes and Linux replay pass. Actual board K is pending. No answer or edge weight is rounded.

## Canonical CSV / banded queue: real board result

`run-ca3be2d2ada3` on `a5394d33e9058b843422529374362b00adbc0ecb` passed all gates: T=0.416137 s, M=97,943,552 bytes, S=573, K=13.94412, points=57.219555. Exact record: `../docs/board-round2-canonical-band.json`. Exact64-distance bands and8-entry batches improve the prior55.278386-point best to57.219555. Private compressed-loader counters/cursors are exact but slower locally (0.440324 s at4 loaders and0.535121 s at2 versus0.411218 s atomic); rejected. Five alternating band-setting trials measured b6/n8=0.539978 s, b5/n8=0.514654, b7/n8=0.499970, b8/n8=0.556723 and b6/n16=0.551302. Next board candidate changes only the band width to128, preserving exact labels, batching, fallback and conservative stopping. These Apple ARM times select experiments; they are not official speedup claims.

## Isolated compiler /128-band board result

`run-024164da6ce1` on `46504cbb5cda9e3df890ffe202dab4e3f7587393` passed all gates: T=0.439985 s, M=96,825,344 bytes, S=573, K=13.592135, points=56.664384. Record: `../docs/board-round3-pgo-band.json`. The wider128-distance band scores below the64-band best57.219555; restore64. Next hypothesis: lossless four-byte adjacency entries reduce edge storage from60 MB to40 MB on the full graph. Wider weights use a full uint32 side table; node spaces above24 bits retain six-byte entries. A five-trial local comparison at128 bands measured0.444167 s old versus0.447287 s packed, with process RSS203.31/184.22 MB. This is a memory tradeoff, not a claimed runtime gain. A sanitizer caught reference binding to an unaligned packed fallback field; copying that field to aligned scalar locals fixes it. Fail-fast sanitizer settings and explicit fallback models are required before submission. Earlier output-only prototype checks do not constitute sanitizer approval.

## Variable-width packing: real board result

`run-12d12491dcd8` on `bba4fe03074368db5bb0bc0b49af917306e9bdb2` passed every gate: T=0.513509 s, M=77,611,008 bytes, S=617, K=13.005473, points=55.706308. Record: `../docs/board-round4-edgepack.json`. Lower memory does not offset slower runtime/source cost; variable-width decoding is rejected. A refined candidate selects a21-bit/11-bit specialization once from the graph header, with exact six-byte fallback for larger nodes, constant shifts, and no inner representation branch. Local five-trial medians: stronger six-byte0.362916 s, variable packed0.320407 s, specialized packed0.324607 s; local memory203.08/183.27/182.75 MB. These Apple ARM gains are not accepted as Intel improvement.

Next compiler hypothesis: full-scale training at independent seed1000003, plus sample130363, better represents the scored workload than two samples. In C, sample and full use the same name-pool size, so new-key frequency differs materially. All input/output/profile files remain in builder stages. Public seed1 is not a training input. Validate on other seeds and real board K; retain only measured overall gains.

## Full-scale training / specialized decoder: real result

`run-e3e91f5f3cec` on `eb16c07b177d5213110083063d4b38e50548714c` passed all gates: T=0.423052 s, M=76,783,616 bytes, S=641, K=14.277374, points=57.732417. Record: `../docs/board-round5-full-pgo.json`. Specialized decoding and full training improve beyond57.219555 to57.732417, with76.78MB cgroup memory. Build time160.596 s stays within the published600-second limit. This combination is retained; the lower-scoring variable-width decoder is not.

## Dense C dictionary: exact board result

`run-138c7d1ae27d` on `cb8cbedcd20a28153ebe790bb58f6b4c9bcc5f26` passed all gates: T=0.404073 s, M=78,094,336 bytes, S=641, K=14.559454, points=58.157255. Record: `../docs/board-round6-dense-c.json`. Runtime/build inputs are unchanged from the retained configuration; this small higher observation is repeat variation, not an algorithm gain.

Next loader hypothesis: shared byte degree counts plus exact256-wrap spills, then shared16-bit block-relative cursors with exact32-bit wide-block fallback. Counters remain atomic; each wrap and edge slot has one owner. Five alternating full-public trials measured0.305556 s /182.39MB RSS old versus0.269400 s /175.19MB narrow; Apple ARM development evidence only. Full/new-seed outputs, independent Floyd graphs, high-degree/65535/65536/wide-ID fixtures, strict sanitizers, concurrent exact-slot models and846 Linux cases pass. Actual board K pending.

## Narrow graph-loader board result

`run-3898322cf5d1` on `61e345f753f6011b6ecd66c6cbba86030d72fa28` passed every gate: T=0.329751 s, M=76,771,328 bytes, S=728, K=15.866278, points=60.023752. Record: `../docs/board-round7-narrow-d.json`. The narrow byte degrees/relative cursors improve beyond58.157255 to60.023752, runtime0.329751 s; retained.

## Flat/streaming A: exact board result

`run-f53c4e4a6ec9` on `2917982a9d0d26a813aacd1f2065331f6866016c` passed all gates: T=0.328593 s, M=76,972,032 bytes, S=728, K=15.885913, points=60.050609. Record: `../docs/board-round8-flat-a12.json`. Runtime/build source is unchanged; differences are repeat variation.

A bounded eight-byte numeric-prefix parser passes std::from_chars/all-byte/guard-page, tiny and full-hash checks. Five alternating trials give0.315130 s old versus0.311449 s eight-byte, about1.2% local improvement. This is too small to establish a worthwhile total-score gain against added code/variation, so it is not promoted or board-submitted. Reports: round9-d-eight-*.json.

## SIMD CSV comparison: exact board result

`run-9f77334ae44a` on `1b21266eeee60232176372208d6c4120465ad988` passed all gates: T=0.326739 s, M=78,053,376 bytes, S=728, K=15.886532, points=60.051455. Record: `../docs/board-round10-simd-c.json`. Source/build inputs are unchanged from the retained configuration; the result is repeat variation.

Neighbor-label prefetch prototypes pass fresh reference/adversarial and full-public outputs, but five alternating native trials measure0.345373 s without hints,0.349500 s locality1 and0.351072 s locality3. Both are slower and rejected before sanitizer/board promotion. Reproducible patches and raw round11-d-prefetch reports are retained outside scored folders.

## Final retained-source confirmation

`run-f169e16c8fde` on `d28fe2590101b6b9a362e71b7bd8ee8f379f0741` passed all gates at 2026-10-31T07:14:42Z: T=0.348996 s, M=78,278,656 bytes, S=728, K=15.362752, points=59.323451. Exact record: `../docs/board-retained-final.json`. Runtime/build inputs match 61e345f byte for byte. This confirms the selected combination; historical best observations remain separate, and no repeat delta is called an algorithm gain. Subsequent documentation updates change no runtime/build/metadata input.

## Exact opposite-frontier negative filter

Each private distance map keeps an8192-byte bit filter keyed by a16-bit multiplicative node hash. Every improve attempt sets its bit, including wide-distance labels; reset clears both map and filter. A missing bit proves the opposite map has no label; a present bit still performs the complete exact lookup, so collisions only cost time. Own-frontier lookups remain unchanged.

Nine alternating full-public Apple runs measured median0.435521 s baseline versus0.417454 s filtered, with every output hash verified. This is local evidence, not an Intel score. Fresh sample/tiny and full-public1/6/12-worker outputs, strict ASAN/UBSAN and TSAN, random map/filter models (missing nodes, resets, growth, wide distances),256 independent Floyd–Warshall graphs/85,871 answers and846 restricted Linux replays pass. The replay image ID matches the exact Linux build report. Reports: `../docs/round13-d-filter-*.json`. Actual board K decides retention; the larger corridor prototype is not in this submission.
