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

A larger, separate prototype marks only reciprocal degree-two corridor interiors with two distinct non-self neighbors, pins every input query endpoint, and follows a corridor with exact full-width accumulated weights. Fresh tiny/adversarial,256 independent graphs and every full-public benchmark output pass. It is rejected before promotion or sanitizer/board testing: nine rotating native full-data trials measure original0.331499 s, filter0.333864 s, corridor+filter0.390198 s. Preprocessing/following cost exceeds the saved queue work. This second comparison also fails to reproduce a clear local filter gain; actual filter board K remains the decision point. Reports `round14-d-corridor-*.json`, reproducible patch `../docs/prototype-patches/round14-corridors.patch`. No official corridor score is claimed.

`run-033db19311ab` on `c75b6d5aa825c0305c14ece720c24d16675077d6` passed every official gate: T=0.334585 s, M=78,217,216 bytes, S=741, K=15.650968, points=59.727060. Record: `../docs/board-round13-filter.json`. It does not beat the retained60.051455-point best, and the second local comparison is inconclusive, so restore D's exact pre-filter runtime/build inputs. The rejected filter patch remains in docs/prototype-patches/round13-negative-filter.patch. A/C source was unchanged in that board comparison; their differences are repeat variation.

## Shared lookup layouts and current worker tradeoff

A merged12-byte union-of-frontiers table matches public outputs but grows the working set and slows native full runs (0.264826 s original versus0.329389 merged). An interleaved8-byte twin layout is also slower (0.292380 versus0.298664). Neither is promoted or claimed as independently validated. Reproducible patches preserve both.

On the current narrow-loader/compact-edge/band64 code, nine rotating trials measure six/eight/twelve workers at0.379554/0.370482/0.338913 s, with max native RSS177.26/182.55/192.48MB. This retests the current layout, not the older twelve-worker loader that lost on the board before later storage changes. Twelve is a time/memory tradeoff hypothesis; every algorithm remains exact and actual Intel/cgroup K decides retention. Default12 is validated separately from the benchmark's environment override. No native time is presented as an official improvement.

The unchanged algorithm with default12 passes fresh tiny/sample seeds839/853/857, full public outputs at1/6/12 workers, strict ASAN/UBSAN and TSAN,256 independent Floyd–Warshall graphs/85,871 answers, all boundary/high-degree/wide-ID/64-bit cases, and852 exact-image Linux replays. Actual native and Linux defaults without overrides pass. Reports: `../docs/round18-*.json`. Real board K decides the default; no Intel gain is claimed yet.

## Worker result and narrower-band hypothesis

Round18 commit b1388b0 passed all gates: run-2b15f6245ed9, T=0.297638 s, M=94,314,496, S=728, K=16.026845, points=60.242402. Twelve workers/band64 beats prior60.051455/K15.886532; retain it as the board comparison baseline. Record: ../docs/board-round18-compact-batch.json.

Next test six workers and band32 with the existing exact labels, queue fallbacks, edge/cursor storage and distance-bound proof. Nine rotating full-public native trials: band64/12=0.271934 s/191.27MB, band32/6=0.285759/176.54MB, band32/12=0.280890/191.04MB. Band32/12 is slower locally; only the memory-saving six-worker combination is submitted. Retain only if real total K improves.

Round22/23 exact D source passes fresh863/877 ASAN/UBSAN, TSAN887, all adversarial/high-degree/wide-ID/MAX-weight/64-bit tests, public outputs1/6/12 workers,256 independent Floyd–Warshall graphs/85,871 answers, strict GCC band32 primitive models,843 exact-image Linux replays and actual native/Linux six-worker defaults. Source identities and raw records are in ../docs/round23-*.json and ../docs/round22-d-independent.json.

Round23 commit44a902b6b7db427741a1bfd75c99dbee184ec909 passes every gate: run-cffa076b5858, T=0.326865 s, M=77,938,688, S=728, K=15.888141, points=60.053655. This is below twelve-worker/band64 K16.026845/60.242402; restore that exact b1388b0 runtime/build source. Record: ../docs/board-round23-lazy-quote-band.json.

Further direct-index32-bit/16-bit distance-array prototypes retain exact64-bit fallback and pass all full-public benchmark output hashes, but fail the local tradeoff. Nine rotating native trials: sparse6=0.232130 s/177.59MB, dense32/6=0.239245/247.46MB, dense32/12=0.234059/334.33MB. A separate rotation: sparse6=0.240822/177.90MB, dense16/6=0.260492/199.07MB, dense16/12=0.229717/245.20MB. The smaller twelve-worker direct table is only~4.6% faster than sparse6 for~67MB extra native peak, and it has not beaten the stronger sparse12 configuration. Reject both before broader sanitizer/board validation. Patches and raw round26/27 reports remain outside scored folders.

The exact restored twelve-worker/band64 runtime passes every gate again on1856d3937190d20e2b43dc49234e4d49238233b7: run-bc733425486b, T=0.396360 s, M=93,470,720, S=728, K=13.913228, points=57.171395. The historical best60.242402/K16.026845 uses byte-identical runtime/build source; this large repeat difference is recorded as variation, not an algorithm regression or an invented gain. Record: ../docs/board-round24-narrow-c-retained-d.json. Retain the proven sparse twelve-worker/band64 combination after the direct-array prototypes fail the local tradeoff.

The unchanged sparse12/band64 source repeats at59.060365/K15.177746 on2c6c51e452faf284f013fd6b12d7333c310dcecc, run-f1d22f209870, T=0.328814 s/M=96,522,240, every gate passed. Historical best60.242402/K16.026845 remains separate. This is repeat variation. Record: ../docs/board-round30-cutoff-parity.json.

Next prefer the lower conservative frontier minimum except when one queue has more than four times the other's entries; then expand the smaller queue. Only the choice of side changes. Both queues still retain exact distances, stale-label checks, requeue improvements, the whole-batch stopping test and the same conservative lower-bound proof. Limiting queue imbalance also avoids abandoning a frontier whose initial weights are very large. The ratio affects work order only, not the computed answer or a distance cutoff.

Nine rotating native full-public trials: count-balanced0.288196 s/191.63MB, alternating0.278778/198.12MB, balanced minimum0.267934/192.87MB. Every output SHA matches. Select balanced minimum for a real test; alternate remains rejected outside scored folders. Fresh971/977 strict ASAN/UBSAN,983 TSAN, all adversarial/large-degree/wide-ID/64-bit cases,256 independent Floyd–Warshall graphs/85,871 answers, public outputs1/6/12,843 exact-image restricted Linux replays and actual default entrypoints pass. Independent graph execution now explicitly halts on undefined-behavior diagnostics; the strict report is round32-d-independent-strict.json. Real K must beat16.026845 to retain this policy.

Round32 ce5ad53ee45296595a6eab2c9ac74d77fa4c61e7 passes every official gate: run-4a977412640c, T=0.322779 s, M=96,276,480, S=734, K=15.307933, points=59.245827. It fails to beat the retained16.026845/60.242402. Reject balanced minimum despite the local7% timing gain; restore every D runtime/build/metadata input to2c6c51e, which itself matches the best-scored b1388b0 D. Patch ../docs/prototype-patches/round32-balanced-minimum.patch preserves the rejected event source. Record: ../docs/board-round32-balanced-frontier.json.

## Final restored-combination confirmation

Exact commit 71a023706495a99867f32a3e1856317f0d9e73bb passes check/build/correctness/timeout/sandbox for all A/C/D. This track's run run-4dba3dfffd2a: T=0.303599 s, M=94,232,576 bytes, S=728, K=15.871484, points=60.030877. Record: ../docs/board-round32-retained-final.json. Every one of the27 retained runtime/build/metadata inputs matches this scored commit in round32-final-source-match.json. All weaker runtime experiments are removed. This repeated-source result confirms the combination; historical best and latest confirmation remain separate, and repeat deltas are not called algorithm gains. Further updates are documentation/evidence only.

## Round38: batched graph-loader memory access

Native phase diagnostics show substantial degree/scatter cost. Keeping decoded edges avoids a text pass but adds about40MB peak RSS; ordered query batches are slower. Prefer a bounded16-row loader pipeline: decode and prefetch degree/cursor addresses, claim the exact atomic slots, prefetch the resulting edge addresses, then scatter every row. Both text passes, exact wrap/spill handling, wide cursors/IDs/weights, query algorithm and output order remain. Extra scratch is only16 rows per loader. No file-order or seed-specific assumption is introduced.

Eleven rotating public-hash-checked native trials: baseline0.339602 s/192.45MB, loader8=0.343298/191.59MB, loader16=0.324033/192.72MB, loader32=0.332808/191.59MB. Select16 as a modest total-score hypothesis with essentially unchanged memory; Apple time is not Intel K.

Fresh1009/1013 strict ASAN/UBSAN,1019 TSAN, complete public1/6/12 outputs, partial batches and all high-degree/wide-ID/MAX-weight/64-bit adversarial cases,256 independent Floyd–Warshall graphs/85,871 answers, strict GCC loader/edge models,843 exact-image Linux replays and actual defaults pass. Reports ../docs/round38-*.json. Retain only if real K improves.

Round38 f378b2e51c3a9e3236a37bd0424317b633befa42 passes every official gate, run-11357e4c51be: T=0.282954 s/M=93,233,152/S=771/K=16.334185/60.654874 points. This beats60.242402/K16.026845 including source cost; retain the16-row prefetch loader. D source is unchanged in round43. Record: ../docs/board-round38-parser-groups-loader.json.

Validation harness note: the original round38 native sanitizer/race jobs could share adversarial output folders. Generated sample seeds were separate. The suites were rerun with unique run IDs, all passed, and1047 image-matched Linux replays passed. These isolated reports are authoritative for per-binary adversarial attribution. Original reports are preserved with that limitation; no runtime fix was required. Round43 uses isolated names/output paths from the start.

Next isolated runtime hypothesis: cap process-local glibc arenas at2 via the final image ENV. C++ code and trained executable are unchanged from the retained16-row loader. No host/harness setting is changed. Full restricted Linux output, actual default entrypoint and906 exact-image independent/adversarial replays pass; native source sanitizer/race/graph proofs remain byte-identical. This setting previously lost on an older A layout, so no transfer of that result or predeclared D gain is assumed. Real total K must beat16.334185/60.654874. Reports ../docs/round44-d-*.json.

Round44 1ed8388a7ff03ab05c5aac5d864b2c6fdff886aa passes all gates: run-3b0ef5177bf0, T=0.285467 s/M=90894336/S=772/K=16.341793/60.664986 points. This is a very small improvement over60.654874/K16.334185, with2.34MB less charged memory; retain the process-local arena cap provisionally, without claiming a large effect beyond run variation. Record: ../docs/board-round44-d-arenas.json.

Retest loader concurrency on the retained narrow counter/cursor,16-row prefetch and compact-edge layout. Nine rotating full-public hash-checked native trials at12 query workers:2/4/6/8/12 loaders =0.311961/0.296097/0.297816/0.267278/0.264735 s, RSS191.77/191.61/191.14/193.99/191.55MB. Select12, bounded by the requested worker count. Degree wraps/spills, atomic cursor ownership, wide fallbacks, exact query algorithm and output order are unchanged. Retain process-local arena cap2 from its small positive real test.

Fresh1079/1087 strict ASAN/UBSAN,1091 TSAN, all degree/cursor/wide-ID/MAX-weight/64-bit/partial-batch adversarial cases at1/6/12 workers,256 independent Floyd graphs/85,871 answers, full-public hashes,909 exact-image Linux replays and actual native/Linux defaults pass. Primitive headers are byte-identical to the prior GCC-sanitized source. Reports ../docs/round50-*.json, combined identities ../docs/round51-candidate-source-match.json. Real K must beat16.341793/60.664986.

Round51 c4f966f2d0e6f0602fac16f0eb8218b8f16499fd passes all gates: run-9f2217b19cd8, T=0.248728 s/M=88686592/S=772/K=17.593454/62.267555 points, build163.371 s. D12 loaders improves the prior60.664986/K16.341793 to62.267555/K17.593454; retain. Record ../docs/board-round51-prefault-counters-loaders.json.

## Selected-combination real confirmation

Exact commit 07c31360af938e391c3e09e3d21f969a1709b092 passes check/build/correctness/timeout/sandbox for every entered track. This track run-ec2238f1c6b2: T=0.272721 s/M=90984448/S=772/K=16.715998/61.156615 points. The current historical best is62.267555/K17.593454 atc4f966f2d0e6f0602fac16f0eb8218b8f16499fd, with byte-identical runtime/build/metadata inputs. This repeat is not an additional algorithm gain. All27 selected inputs match the scored source and each current best record in ../docs/round55-final-source-match.json.1056 current-image Linux replays and actual defaults pass. A/C additionally pass fresh isolated1109/1117 ASAN/UBSAN,1123 TSAN and all-country-width checks; D's exact round50 isolated strict sanitizer/race/independent source is retained. No unscored prototype remains in a track folder. Further documentation updates change no compiled input. Record ../docs/board-round55-selected-final.json.

## Source-identical baseline repeat and rejected screens

Documentation-only57cc23e repeats the retained D source at run-f851ad71c6a0: T0.210424 s/M88,657,920/S772/K19.129071/64.084694, all gates passed. This higher observation is source-identical repeat variation, not a new algorithm gain. Record ../docs/board-round56-baseline-repeat.json. The new pass starts from that best observation. D stays unchanged in round60 and its current Linux image passes909 fresh exact-output independent/adversarial replays plus true defaults.

An eight-byte staged-edge prototype preserves full weights through22-bit-tag escapes and retains text decoding for node spaces above21 bits. It is slower and rejected after public-hash screening: baseline0.347924 s/191.35MB versus staged0.359238/200.26MB. Lazy and stdlib wide-map variants also fail the local tradeoff (0.272643 baseline versus0.274495/0.282264), and are not promoted or generally sanitizer/Linux/board validated. All source patches and raw reports preserve the screening limits.

Round60 a5887ec541782b0ad141ecd878f1c7b04280ccde passes every gate: run-a073d40c4fee, T=0.248516 s/M=89231360/S=772/K=17.579412/62.250218 points. D code is unchanged; this is repeat variation. Record ../docs/board-round60-intel-c-allocator-a.json.

## Bounded mandatory endpoint-edge normalization

If the current source has exactly one outgoing edge, every source-to-target path must begin with it; the symmetric fact holds for a target's unique incoming edge. At most one such edge per endpoint is removed when its weight exceeds half UINT32_MAX, accumulating its exact uint64 cost. Search then solves the remaining directed query and adds that fixed cost. Meeting endpoints are checked immediately after each removal, preventing double counting a direct edge. Other edges/queries use the original exact search. The threshold selects an optimization, never an answer cutoff. The preprocessing is bounded, so cycles remain ordinary unreachable/cyclic queries for the existing algorithm. This can keep relative search labels in the compact32-bit format instead of carrying a large mandatory offset in every label. No graph catalogue or precomputed result is used.

Full forced-chain/large-chain variants with constant-space cycle detection are slower locally and are not promoted. Eleven rotating public-hash-checked native trials: retained0.273129 s, full chains0.277319, large chains0.277737, bounded one-large0.266474; max RSS189.51/189.96/193.20/190.78MB. Select the modest bounded hypothesis for actual total K, including source/memory cost.

Fresh1163/1171 strict ASAN/UBSAN,1181 TSAN,256 independent Floyd graphs/85,871 answers, new all-pairs direct-meeting/prefix+suffix/duplicates/cycles/self-loop/half/MAX-weight fixtures, wide IDs/cursors/64-bit chains, full-public/defaults and945 exact-image Linux replays pass.28 combined source identities are proved in round62-candidate-source-match.json. Real K must exceed retained19.129071/64.084694.


## Round62 real result and restoration

Commit9933500b9335ab4866a21ac96990dac5fa2f8cb5, run-fe5461d995e1 passes every gate: T0.223902 s/M91,029,504/S798/K18.355312/63.188089 points. This does not beat retained64.084694/K19.129071, so remove the bounded mandatory-edge query transform and restore exact57cc23e runtime/build/metadata. That retained source's57cc D best is a repeat of the same earlier algorithm, not a new gain. Preserve both records.

A separate private-degree-only prototype removes shared degree atomics but keeps shared scatter cursors. Eleven rotating full-public exact hashes: retained0.282809 s/190.66MB, endpoint candidate0.291394/191.59MB, private degrees0.286491/211.14MB. It fails the local total tradeoff and is rejected before broad sanitizer/board validation. Full patch and limits: round63-64-prototype-index.json. No new D algorithm is submitted in round64. Exact restored D is rebuilt and replayed rather than relying on a no-longer-available historical image.


Round64 exact restored D repeat run-deaaea0d7ecd passes all gates: T0.221016 s/M88,694,784/S772/K18.663520/63.549678 points. Same selected57cc23e code; below historical64.084694 repeat. No new algorithmic gain or regression claimed.


Round67 unchanged D repeat run-d0de0cbd76d3 passes all gates: T0.235584 s/M90,849,280/S772/K17.990691/62.752392 points. This is variation of exact57cc23e, not a new algorithm.

Five current retained-source instrumented Apple runs, full hashes checked: degree counting53.702 ms, prefix/allocation7.123, scatter/release55.742, graph search154.350. Search is about57% of these local phase totals. No Intel phase timing is claimed. The next screen targets full node-bit mixing and reset locality. Eleven rotating full-public exact-hash trials: retained0.279381 s, folded hash0.288099, high-product hash0.317396, dense reset0.286384, fold+reset0.285505, shrinking logical tables+fold0.292981. All lose; the final variant saves about5.1MB native RSS but costs4.9% time plus source. Reject every variant before broad sanitizer/Linux/board promotion. Preserve patches and limits in round68-70-prototype-index.json; keep exact57cc23e.


Round70 7402c7f, run-121a8b2f038c passes all official gates: T0.289287 s/M91000832/S772/K16.229738/60.515575 points. Code is unchanged57cc23e. This lower repeat is retained honestly as variation, not described as an algorithm change. Exact report ../docs/board-round70-endpoint-crc.json.


Final selected combination 0008c8ae9868ebf4746fa228ec813ab2dda8ab6d, run-e3b408a1cd25 passes check/build/correctness/timeout/sandbox: T0.22984 s/M90148864/S772/K18.242324/63.054009 points. All27 current inputs match this exact commit and each best track source in ../docs/round71-final-source-match.json. A/C small new best observations are unchanged-source variation; the two real C algorithm improvements are recorded separately. Further updates are evidence/prose only. Report ../docs/board-round71-selected-final.json.


## Lossless bucketed32-bit labels with full64-bit fallback

A bucket supplies a node's low bits and the stored tag supplies every remaining bit of a21-bit node ID. This is exact identity reconstruction, not a probabilistic fingerprint. A nonzero low field stores distance+1. Values/node IDs that cannot fit, and full buckets, use the unchanged full-node64-bit distance map. On improvement, a compact label is always no greater than an old fallback value. Table growth reconstructs complete IDs and preserves every exact distance. Zero-distance/node-zero, packed UINT32_MAX words,31-bit shifts, full buckets, promotion, resets, wider IDs and distances all have independent reference coverage.

Eight-entry buckets use bounded128-bit SSE2 or NEON groups; other architectures have a scalar path. SIMD compares either matching exact tags or the first empty slot. Buckets have a dense occupied prefix because individual labels are not deleted within a query; whole-query reset clears all touched slots. Adjacent graph/CSR/queue logic and full-width path arithmetic are unchanged.

Initial four-way screens save about11MB native RSS but are slightly slower. Eleven rotating widened-bucket public trials: retained0.186116 s/190.55MB, four-way0.192328/178.52MB, eight-way bits9=0.193552/178.19MB, eight-way bits10=0.187594/179.06MB. Select eight-way10:0.8% slower locally but about11.5MB less peak RSS. Canonical source/memory/time cost must earn actual total K.

Fresh1283/1289 ASAN/UBSAN,1291 TSAN, full/default/degree/cursor/wide-ID/zero/MAX/64-bit tests,256 independent Floyd graphs/85,871 answers, strict native/GCC full-key reference/reconstruction/growth/fallback/promotion/reset/extreme-width and queue models pass.945 current-image Linux cases and all27 frozen/source/image identities pass. Real K must exceed19.129071/64.084694.


Round75 commit342c0aa, run-22b23e81f4d4, passes all five official gates: T=0.2113 s, M=76529664 B, S=827, K=19.457458, points=64.454305. Retain the lossless packed-label change; it exceeds prior64.084694/K19.129071. Raw result: ../docs/board-round75-cache-prefetch-labels.json. One observation does not remove timing/memory variation.


Round77 unchanged75 D source passes all gates again, run-e1b39207f577: T0.220476 s/M77164544/S827/K19.016806/63.956879. The lower repeat remains separate from the best64.454305. Raw ../docs/board-round77-owner-index.json.

## Smaller exact full-width fallback

The packed table already handles common IDs/distances exactly; its full-width fallback need not eagerly allocate4096 custom epoch labels for every direction/worker. Replace only that fallback with std::unordered_map<uint32_t,uint64_t>. Full node IDs are keys and all64 distance bits are values. Clearing at query boundaries and strict improvements preserve the same exact semantics. Hash collisions still require complete integer equality. This uses only the standard library, with no new runtime dependency. The packed tag/reconstruction/growth/slot protocol and all graph/search/queue logic remain unchanged.

Eleven rotating sequential full-public native trials:75 retained0.189305 s/179.60MB, lazy custom fallback0.187833/179.98MB, standard fallback0.188042/178.01MB. Select the standard fallback: similar0.7% time improvement, roughly1.6MB lower peak RSS, and substantially less custom source. The lazy variant is rejected at screening only. Intel total K must exceed19.457458/64.454305.

Fresh1319/1321 strict ASAN/UBSAN,1327 TSAN, full1/6/12, all degree/cursor/wide-ID/MAX-weight/64-bit cases,256 independent Floyd graphs/85,871 answers, strict native/GCC exact-map/reference/reconstruction/growth/full-bucket/promotion/reset/extreme-width/numeric/queue models pass. 1032 exact-current-image Linux cases and actual native/Linux defaults pass. All27 selected inputs match frozen79 and the corresponding exact source/image evidence. A reuses exact75 proof and C reuses exact restored71 source, freshly rebuilding its Linux image. Real board acceptance remains pending.


Round79/27dd74a standard fallback passes every official gate, run-175ad6688075: T0.240112 s/M76165120/S797/K18.371758/63.207536. It loses to19.457458/64.454305, so restore exact342c0aa D runtime/build/metadata and README. Raw ../docs/board-round79-small-wide-fallback.json.

Instrumented capacity-only diagnostic82 (on rejected79) finds most reset samples at bits13/14 despite average prior queries around2100/2641 labels; last live queries are omitted and initial empty resets included. No phase clock/performance claim applies to this diagnostic. This motivates independent reset variants on the stronger75 fallback. Eleven rotating full-public native trials all match hashes:75 retained0.190085 s/179.03MB, always base0.195404/175.51MB, cap11=0.191827/174.82MB, quarter-occupancy0.193604/174.29MB, one-step0.194164/175.75MB. None earns a convincing combined time/memory/source tradeoff; all are rejected at screening only. The restored75 image passes1032 independently checked Linux cases, including256 graphs/85,871 answers, and actual full output/default checks. No new D gain is claimed beyond the selected75 lossless packed-label change. Raw ../docs/round82-d-capacity-profile.json, ../docs/round83-packed-reset-bench.json.


Round81 restored75 source passes all gates, run-1295b6dc67f6: T0.223551 s/M76488704/S827/K18.918819/63.844702. Historical best64.454305 remains separate from this slower exact-source repeat. Keep the original full-width fallback and packed75 labels. Raw ../docs/board-round81-bounded-space.json.


Final selected combination b80c1ab98657ab4f5d4d6ce3ffe83b9012c2dcda, run-d906507c3974, passes check/build/correctness/timeout/sandbox: T0.240533 s/M77619200/S827/K18.185307/62.986032 points. All27 current runtime/build/metadata inputs and each current best source match the selected commit in ../docs/round87-final-source-match.json. Historical best and this latest same-source confirmation remain separate; a lower repeat is not hidden or labelled a new algorithm regression. Current A96/C147/D1032=1275 matching-image fixture replays, fresh combined Make/public1/6/12 and actual native/Linux defaults pass. Later updates are evidence/prose only. Raw ../docs/board-round87-selected-final.json.


Additional research-led screens are rejected. Independent2/4-stream graph parsing retains both exact passes and all CSR/search logic but loses locally: retained12=0.188235 s,2streams at6/12=0.220623/0.191449,4streams at6/12=0.219214/0.190418. A within-band min-heap, with either the original conservative boundary or tighter queued minimum, also loses: retained0.222627 s versus0.254634/0.261620. Every full-public hash passes. No broader sanitizer/independent-graph/Linux/official claim is made for these unselected prototypes. Exact75 D remains. Raw ../docs/round90-independent-stream-bench.json and ../docs/round92-heap-band-bench.json.


##32-entry exact same-band search batches

The accepted75 lossless packed-label SIMD layout materially changed lookup cost, so retest queue batching rather than transferring old broad-label timings. Change only work/range scratch and pop_batch limit8→32. Distances, conservative band64 stopping bound, full-width fallbacks, stale-label checks and count-balanced side choice are identical. More entries from one band may be processed before reconsidering the side; no distance or answer is rounded. Source complexity/storage is essentially unchanged apart from bounded per-worker scratch.

Eleven rotating full-public native screens100/101/102 all match hashes.100 retained0.188751 s versus batch16=0.183936, band32=0.185157, band128=0.194784 and packed-neighbor hints0.190731.101 retained0.189530,16=0.184204,32=0.182033,64-band/combined32-distance16-batch=0.185558.102 retained0.189103,32=0.185344,64=0.184149. Choose32 for smaller scratch and the repeated2–4% local hypothesis. These Apple numbers do not establish Intel K improvement; actual target must exceed19.561482/64.570088.

Fresh1451/1453 strict sanitizer,1459 TSAN, public1/6/12 and every wide-ID/weight/degree/cursor/64-bit reference case,256 independent Floyd graphs/85,871 answers, native/GCC exact queue model with actual32-entry extraction and unchanged packed-label/numeric models pass. Current image replay counts/defaults/hashes are in round104-candidate-source-match.json.

Block-owned98 loading is rejected. It gives every4096-node block one non-atomic degree/cursor owner and transfers exact forward/reverse events, but random labels route most edges twice. Native11 rotating medians retained0.186998 versus8-read/4-owner0.213110,6/6=0.202726,4/8=0.195477 and larger16384-node blocks0.203115. All public hashes pass; default8/4 also passes tiny1441/1447 and boundary references. No non-atomic concurrency/sanitizer/Linux proof or official gain is claimed for this discarded architecture.


Round104/252d75032-entry batches pass every official gate, run-deabebbc1efe: T0.195926 s/M77459456/S827/K20.157695/65.222044. This beats prior64.570088/K19.561482, with about5.7% lower measured time and3.0% higher K. Keep32-entry batching. Raw ../docs/board-round104-event24-batch32.json. This is one real observation and repeat variation remains possible.


## Exclusive block owners with split direction channels

The earlier16-byte flags loader98 lost. This independent revision sends full12-byte(u,v,weight) records on separate forward/reverse channels. The owner knows the direction for an entire vector, so its16-row loops need no per-edge flag checks. A4096-node block has one owner for degree counting and cursor claims.8 readers+4 owners at12 threads preserve the total limit. Each actual input row contributes one parsed count and two directed messages, never a guessed edge or cached answer. Both passes validate counts and retain all IDs/weights/full-width escapes. Ordered empty batches finish each stream; release/acquire transfers vector ownership and errors cancel peers. Only the block owner touches each non-atomic counter/cursor.

105 native11 rotating public-hash medians: retained atomics0.190931 s,4-reader/8-owner0.192651,6/6=0.192860,8/4=0.186723. Apple memory/time are not Intel scores. The hypothesis is fewer locked updates/cache-line transfers on the6-physical-P-core target, which the official rules identify as i5-13500. Intel's specifications list24MB shared cache and11.5MB total L2 (https://www.intel.com/content/www/us/en/products/sku/230580/intel-core-i513500-processor-24m-cache-up-to-4-80-ghz/specifications.html); a cache benefit here is an inference, not measured target phase data. Actual total K, including new source and queue memory, must beat20.157695/65.222044.

The106 prototype kept old batch8 and passed1471/1481 sanitizer,1483 TSAN and spread-ID independent graphs. Do not substitute that proof for107's combination with the actual104 winning32-entry search. Fresh1071487/1489 strict ASAN/UBSAN,1493 TSAN, public1/6/12 and all wide-ID/weight/degree/cursor/64-bit fixtures pass.256 Floyd graphs spread over65537 node IDs verify85,871 answers at all1..12 worker topologies;36 more TSAN runs verify13,013 answers. Additional reference/full-queue cases0/1/511/512/513/1025/4097/65544 rows and malformed number/node/truncation/count fixtures confirm progress, EOF and normal cancellation, including every1..12 workers under ASAN and1/2/6/12 under TSAN. Native/GCC ASAN/UBSAN and native TSAN owned-degree/cursor models for owners1..11 verify byte wraps,65535/65536,180000-entry full-width blocks, exact slot sequences, narrow/wide paths and partial final blocks. The107 owned header is byte-identical to that106 primitive proof. Queue/packed-label representations are unchanged from the validated32-entry/75 models.

Exact current Linux reference replay counts and actual defaults are in round107-candidate-source-match.json. The expanded test runner initially hit Linux's single-argument length limit before D execution; streaming its same quoted command list on standard input removes that harness limit without changing sandbox or cases. No runtime fix was required. A/C selected source stays exactcfd094c; C24 is removed after losing actual104 K. Real107 run is pending; retain the loader only on improved actual total K.


Round107/8182e42 block-owned split-direction loading passes every official gate, run-9243e0dccd39: T0.375677 s/M76898304/S974/K14.225028/57.652656. It loses badly to32-entry shared-atomic65.222044/K20.157695. Remove graph_pipeline.hpp, its Docker copy/Make dependency and every owned-method runtime change; restore every252d750 D runtime/build/metadata input and README, preserving this history. Mac's2.2% screen does not transfer to Intel; queue/handoff costs dominate despite eliminated degree/cursor atomics. Actual target phase breakdown is unavailable, so that last explanation is a hypothesis. Raw ../docs/board-round107-owned-loader.json.


Selected restoration109/6e5950c passes every official gate, run-c7cff86160b4: T0.208181 s/M77750272/S827/K19.540734/64.547044. It exactly matches the same runtime/build/metadata source as104's65.222044/K20.157695. Preserve both: this lower repeat is material measurement/scheduling variation, not another algorithm change. The two32-entry observations do not support a precise causal5.7% estimate. D32 remains the selected best-record source; the controlled native comparisons and initial real improvement are supporting evidence. Raw ../docs/board-round109-selected-confirmation.json. A/C restored originals also pass; no owned-loader code remains.


Round111 unchanged selected D32 passes every official gate, run-13f7fa4b0adb: T0.200718 s/M77692928/S827/K19.903632/64.946617. This third same-source observation lies between104 and109. Best65.222044 remains, without claiming another algorithm change. Raw ../docs/board-round111-native-a-arena-c.json.


Round118/ea8bfe3 unchanged selected D passes every gate, run-91280e5eebb6: T0.203297 s/M77336576/S827/K19.795174/64.827966. Same-source repeat, not a new algorithm gain; historical best remains separate. Raw ../docs/board-round118-calendar-a.json.


Selected restoration119/f69d4db, run-5a5fb39e3961, passes all five real gates: T0.205177 s/M77094912/S827/K19.716613/64.741616. All27 selected inputs exactly match6e5950c. This is a lower same-source confirmation, not an algorithm improvement; historical bests remain separate. C's unusually slow identical-source repeat is retained honestly, with no code regression asserted from one observation. Raw ../docs/board-round119-selected-confirmation.json.


Round121/e3eb08d unchanged selected source passes all five actual gates, run-14b7d1443699: T0.249066 s/M78090240/S827/K17.849466/62.581261. This lower repeat remains separate from the best; no additional algorithm regression is asserted from unchanged-source variation. Raw ../docs/board-round121-structural-c.json.


## One AVX2 comparison for an eight-label bucket

Candidate123/combined124 changes only FastDistances.slot on AVX2: load the bucket's exactly8 allocated uint32 words in one32-byte unaligned load, shift each full tag logically, compare exact tag or empty and select the first set lane. This returns the same first matching/empty slot as the two4-lane SSE2 loop. Dense occupied prefixes, complete node reconstruction,31-bit shifts, low distance bits, overflow/full-bucket/full64 fallbacks, growth, touched reset, band64,32-entry search and loader are unchanged. Other architectures retain the original implementation. Standard intrinsic semantics were checked in primary LLVM docs: https://clang.llvm.org/doxygen/avx2intrin_8h.html . Native Apple executes unchanged NEON, so no native speedup is claimed. Only actual Intel total K can justify this conditional8-line source increase.

Fresh1583/1597 strict ASAN/UBSAN,1601 TSAN, full1/6/12 public outputs, all wide-node/MAX-weight/degree/cursor/64-bit fixtures,256 independent spread-ID Floyd graphs/85871 answers and36 TSAN graphs/13013 answers pass. Strict native/GCC SSE2 and explicitly compiled/executed AVX2 exact packed-label/reference/last-bucket/full-bucket/growth/promotion/reset/31-bit/boundary-word models pass. GCC AVX2 numeric/queue models extract actual32-entry batches. The exact new native-GCC Linux image passes1080 independently checked graph replays and actual defaults. Restored original C has147 rebuilt-image cases; original A retains96 explicit-image cases. Every27 combined runtime/build/metadata input/image is proved in round124-candidate-source-match.json. Retain only if actual D K>20.157695/65.222044; otherwise restore distance_map.hpp exactly to f69d4db and preserve all losing evidence.


Round124/b3d0cef AVX2 complete-bucket lookup passes every actual gate, run-4861bf277cca: T0.197888 s/M77504512/S840/K20.008319/65.06053. It fails K20.157695/65.222044; restore every original D distance-map/README byte to f69d4db, preserving the losing result and32-entry search. Raw ../docs/board-round124-avx2-d.json.


Selected128/93fc9c9 unchanged selected source passes all five real gates, run-62e275dfaa18: T0.204523 s/M78336000/S827/K19.685137/64.706922. This lower same-source repeat stays separate from historical best and is not a new algorithm change. Raw ../docs/board-round128-offset-c.json.


Documentation-only head130/83a5f9c, run-5323d85905cc, passes every real gate with identical selected128 runtime inputs: T0.23099 s/M77987840/S827/K18.539577/63.404992. Lower same-source repeat, not a new algorithm regression; best records remain separate. Raw ../docs/board-round130-evidence-head.json.


Round133/16bedd2 unchanged selected source passes all five real gates, run-fc68729f503a: T0.19669 s/M76726272/S827/K20.156812/65.221092. Same-source repeat; do not label the delta a new algorithm improvement. Raw ../docs/board-round133-cooperative-c.json.


Round134 newly allocated readonly CSR prefix compression is rejected at native screen. A block base+uint16 deltas replace full offsets only when every span fits; any wide block keeps the full32 vector. Construction/freeing after wide-weight merge is included. Eleven rotating full-public hashes pass: retained0.180995s/RSS179945472; block5120.181254/179093504, block40960.181207/180092928, block163840.182125/179781632. Paired ratios1.00031/1.00428/1.00497 are flat/slower, with at most0.85MB RSS saving and added source. No independent boundary/fallback/model/sanitizer/GCC/official proof; not promoted. Earlier peak lifetime and reusing already-final cursor arrays are distinct future hypotheses, not measured explanations. Patches/flags/limits are in round134-prototype-index.json.


Restored selected135/2b3834d, run-15059e2111e9, passes every real gate with exact selected128 runtime bytes: T0.200157 s/M77668352/S827/K19.932767/64.97838. Lower same-source confirmation, not another algorithm change. Current regular-image1323 cases, additional selected-C228 every-worker/24 normal errors, fresh combined public/defaults and all27 inputs match round135-final-source-match.json. Raw ../docs/board-round135-selected-confirmation.json.


Round136 final-cursor reuse and wide-weight reserve remain unpromoted native screens. After all scatter workers join, each cursor should equal its node's original exclusive CSR end; a query start can use the prior node end or0. The prototypes retain exact narrow/wide cursor storage, free full prefixes early/before wide-map merge or late, and use readonly prefetch with existing32-entry search. A separate reserve-only variant sizes wide_weights from complete local escape counts. Eleven rotating full-public hashes pass: retained0.183952s/RSS179453952; ends-early0.185301/178765824 (paired1.01905); ends-late0.182566/178749440 (0.99687); reserve-only0.182996/178765824 (0.98869); combined0.184372/179568640 (0.98465). Global medians are not causal estimates; native RSS does not show the hypothesized7MB reduction and is not target cgroup memory. No broad final-end/boundary/spill/ownership/sanitizer/GCC/image/official proof yet. Exact source/patches/limits are in round136-prototype-index.json. Current D stays selected128/32-entry source.


Evidence-head137/715dcc6, run-5c922d880bab, passes all five real gates on identical selected128 runtime: T0.207223s/M77234176/S827/K19.611956/64.626046 points. C has a slightly higher same-source best67.916082/K22.820315; that is variation, not another algorithm improvement. Raw ../docs/board-round137-evidence-head.json.


139 promotes only136's reserve-only hypothesis for real measurement. After scatter workers join, sum every local wide-escape vector size in size_t and reserve that many wide_weights entries before the same emplace loop. This includes both forward/reverse full-width weights and is bounded by twice the actual edge count. No loader cursor, prefix release, graph/weight/queue/label/search semantics change. All primitive header bytes remain exact selected128. Native136 paired0.98869 is a modest timing hypothesis, not a cgroup or Intel gain.

Fresh1637/1657 strict ASAN/UBSAN,1663 TSAN, full1/6/12 and all wide-ID/weight/degree/cursor references pass. Independent256 spread-ID Floyd graphs/85871 answers and36 TSAN graphs/13013 answers plus0/1/511/512/513/1025/4097/65544 row, block seams, EOF and normal malformed cancellation pass. Exact GCC image has1080 reference replays and actual defaults; old unchanged header models remain tied to the same bytes. Exact all27 source/image proof is round139-candidate-source-match.json. Retain only if actual K>20.157695/65.222044; otherwise restore main.cpp exactly715dcc6. Final-cursor-end variants remain unpromoted and lack broad proof.


139/184778c run-ba85567b5bf6 passes all five gates: T0.239163s/M77258752/S831/K18.241096/63.052547 points. Exact reserve fails best20.157695/65.222044; restore main.cpp/README to715dcc6. Raw ../docs/board-round139-method-reserve.json.


145/348257e run-3adeecd27501 passes every real gate: T0.20462s/M77193216/S827/K19.738399/64.765597 points. Unchanged selected source: preserve this lower repeat separately from historical best; no new algorithm gain. All28 inputs match round145-final-source-match.json. Raw ../docs/board-round145-mapped-cache.json.


Evidence147/69322d0 run-6aba70749f25 passes all real gates on identical selected145 inputs: T0.204022s/M77721600/S827/K19.740355/64.767748 points. C67.958752/K22.865201 is a slightly higher same-source best; A/D lower repeats remain separate. No new algorithm gain is claimed. Raw ../docs/board-round147-evidence-head.json.


151/9e5d342 run-2be7e41af16f passes every real gate: T0.209894s/M76746752/S827/K19.511461/64.514489 points. Unchanged-source lower repeat; historical best remains separate. Raw ../docs/board-round151-spsc-windows.json.


## Parser-private packed degree counts

155 changes only degree counting/reduction/lifetime: each parser has2-bit lows and private spill totals, every wrap contributes4, and joined main sums all lows/spills into the original full CSR prefixes. Anonymous mapped count arrays/spills release before existing atomic cursors and edges allocate. The original scatter,16-row prefetch, full weights/IDs, exact labels, band64/batch32 search and PGO stay. The unused legacy DegreeBytes declaration remains charged; its old atomic proof is not substituted for new private counters.

152 screens2/4/8-bit variants; exact15511 alternating full hashes measure retained0.183736791s/RSS180322304 versus private2=0.165434458/179503104, paired0.90031243. This9.97% local time hypothesis and noisy RSS delta are not Intel/cgroup evidence. NEW independent models cover packed neighbors/tails, exact wraps/spills/180000 degree, synthetic UINT32 endpoint, every1..12 private-owner reduction/prefix, direct mapped release/RAII move/cross-thread lifetime under native ASAN/UBSAN/TSAN and GCC strict checks. Fresh1753/1759 ASAN/UBSAN,1777 TSAN, full1/6/12, every wide-ID/weight/degree/block/EOF/error case,256 independent Floyd graphs/85871 answers and36 TSAN graphs/13013 answers pass. New D image has1080 reference replays and actual defaults. All29 candidate inputs/images bind in round155-candidate-source-match.json. Only actual K>20.157695/65.222044 permits retention.4/8-bit main variants have native screen only, though the shared generic primitive model instantiates all widths.


155/4191767 run-87d31cc24612 passes all five real gates: T0.21688s/M77340672/S888/K18.961572/63.893717 points. Reject private2 D: K18.961572/63.893717 fails20.157695/65.222044; time0.216880 versus0.195926s and S888 versus827 grow, memory77,340,672 versus77,459,456 roughly flat. Restore main.cpp/Dockerfile/README/Makefile exactly69322d0 and remove private_degrees.hpp. Native9.97% gain did not transfer; no target phase explanation is measured. Raw ../docs/board-round155-pooled-private.json.


157/34293c2 run-e91a4732b13e passes all five real gates after exact selected145 restoration: T0.253388s/M76582912/S827/K17.765703/62.479120 points. Lower unchanged-source repeat; historical best 65.222044 stays separate. All28 inputs and complete file sets match current best-track sources; fresh157 combined public/defaults and original C48 pressure replays pass. Rejected151/155 code is absent. Raw ../docs/board-round157-selected-confirmation.json and round157-final-source-match.json.


159/0882828 run-6a9b5c62c143 passes all five real gates on identical selected145 source: T0.199552s/M77021184/S827/K19.996396/65.047586 points. Lower same-source repeat; no new algorithm gain. Raw ../docs/board-round159-evidence-head.json.


160's new single-word prefix decoder is flat on current D: paired0.996491 versus retained, despite passing strict primitive models; no broader D integration/image/actual promotion.161's distinct disjoint-range parallel packed-low reduction measures original0.181292542, losing155 serial-private2=0.164014083 (paired0.905690), parallel-private2=0.163056750 (0.902018), parallel-private8=0.165848667 (0.914875). The tiny extra gain over already-losing serial155 does not justify added source/memory/new protocol proof. Both remain full-public native screens only, with exact patches archived; no private-degree code enters163. Original12 atomic loaders/band64/D32 stay byte-identical to selected104 best source.


163/d0bf708 run-d86cb628f914 passes all five real gates: T0.194716s/M76922880/S827/K20.248361/65.319494 points. Unchanged-source slightly higher best65.319494/K20.248361 versus65.222044/K20.157695 is repeat variation, not a new algorithm change. Raw ../docs/board-round163-ordered-high.json.
