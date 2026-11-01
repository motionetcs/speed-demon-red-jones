# Track A optimization log

## Current retained result

The retained implementation parses disjoint input ranges into four-byte records, compares complete endpoint names after hashing, computes exact nearest-rank percentiles, and publishes completed hours in output order. Wide latencies keep all32 bits. Mapped buffers are released when their hour is consumed.

The two material retained layout changes are mapped records (real145, run-1fc76115f2d9) and ordered mapped output with bounded prefix8 decoding (real163, run-271fd6ddf3b9; exact actual ID is preserved in the linked raw record). The final full/sample PGO recipe is actual178. Each choice pays its measured source cost. Later better observations of identical source are kept separate from algorithm changes. Rejected spans, output windows, calendars and method dispatch remain in the historical log.

| Record | Run ID | T seconds | Charged memory bytes | S | K | Machine points |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Best observed | run-004bfb2aafff | 0.042474 | 20746240 | 497 | 31.974332 | 75.240074 |
| Passing original281 | run-623d051300f1 | 0.042998 | 21250048 | 497 | 31.626769 | 75.002741 |

These are real public-board records, not final holdout or judging totals. All five gates pass for both rows. Local native timing/RSS and emulated Linux checks are labeled separately throughout this log. The observed best is not a promise of repeatable timing or victory. [Current source and decisions](../docs/RESULTS.md), [exact passing source proof](../docs/round281-final-source-match.json), [latest raw record](../docs/board-round281-selected-confirmation.json).

## Historical experiments

All numbers here are local macOS ARM development evidence, including process launch, not official scores. Raw runs, hashes, and source fingerprints are in `../docs/experiments-local.json`. First scored board run: **run-c76f845b747a**.

| Experiment | Dataset | Baseline median | Candidate median | Decision | Board run ID |
| --- | --- | ---: | ---: | --- | --- |
| Exact selection for groups of at least 64 instead of sorting | sample, seed 1 | 0.04432 s | 0.04546 s | Reject; slower | Unavailable |
| Same independent-seed check | sample, seed 19 | 0.04379 s | 0.04924 s | Reject; slower | Unavailable |

Hypothesis: selecting only the required ranks would save comparisons in large groups. Each candidate was warmed once, then baseline/candidate runs alternated for seven measured runs apiece. Every run matched the official reference hash. The extra selection overhead did not pay on either sample, so that original serial-layout baseline retained full sorting. Selection was later retested after the parallel memory-layout change, as recorded below.

The fresh baseline already uses mapped input, endpoint interning, fixed hour buckets, and integer arithmetic. No earlier measured board baseline is claimed. Full public and container correctness are recorded in `../docs/validation-public-full.json` and `../docs/validation-containers-full.json`. The first actual board record is retained below; local run names are not substitutes for board IDs.

## First official live-board run

The organizer's full-public-seed-1 run passed check, build, correctness, timeout, and sandbox gates. This is one live-board run, not the final holdout/judging result.

| Field | Observed value |
| --- | --- |
| Run ID | `run-c76f845b747a` |
| Commit | `788ae3b205928ca2bc3d60100703d5660123d0f0` |
| Finished UTC | 2026-10-31T03:57:20Z |
| Process wall time | 0.539201 s |
| Cgroup peak memory | 47,161,344 bytes |
| Measured source size S | 188 lines |
| Dependency weight D | 1 |
| K | 8.810248 |
| Live machine points | 47.249407 |

Source: [official board JSON](https://s3.amazonaws.com/raptors.dev/speeddemon.dev/2026/board/board.json); exact records are retained in `../docs/first-board-run.json`. The board time includes parsing, preprocessing, queries/aggregation, and output. Compare future changes on this same machine rather than interpreting differences from Apple ARM development timings as an optimization result.

## Parallel aggregation candidate

Hypothesis: parse disjoint newline-aligned chunks, reduce exact counts and errors, scatter into disjoint contiguous ranges, then sort and format per hour concurrently. Local medians at six workers changed from 0.272663 s to 0.068589 s, about 4x faster; twelve workers took 0.073818 s. These are local timings, not official improvement claims. Raw alternating trials are in `../docs/opt-a-parallel-native.json`.

The candidate passes tiny/adversarial cases, sample seeds 7 and 19, full public hashes at 1/6/12 workers, address/undefined-behavior and thread sanitizers, and the restricted offline Linux x86-64 full-data check. Reports are `../docs/opt-a-parallel-*.json`. The first Intel board experiment uses twelve workers; six will be compared on the actual board. The first real parallel run is recorded below.

### Official parallel-A result

`run-ca62e267fa82` on `7bb8c67d6d7f8ddf063885a82dfe86e4f5fb5343` passed every gate. Wall time was 0.081951 s, cgroup peak 60,215,296 bytes, S=316, K=19.908239, machine points 64.951642. Against the original 0.539201 s / 47.249407-point board run, runtime fell about 6.58x and points rose about 17.70. This includes the memory and source-size tradeoffs. Full record: `../docs/board-opt-a12.json`.

The next board comparison changes only A's worker count from twelve to six; all output and sanitizer tests already exercise both counts. The exact six-worker full-data native/container checks are `opt-a-six-*.json`.

## Six workers and parallel-layout selection

The six-worker board run `run-b768e98565d3` on `835148746ad0da7f69d93a9f72f80cb710f1b52a` passed every gate: T=0.091654 s, M=49,655,808 bytes, S=316, K=19.565079, points=64.574080. Twelve workers had the higher observed K, so twelve is restored. The 1.7% K difference is small and may include run variation; it is not a statistical claim. Record: `../docs/board-opt-c12-a6.json`.

The original serial-layout selection rejection remains valid for that layout. After contiguous parallel scattering, selection was retested on full data with seven alternating, hash-checked trials after warmup. At twelve workers, medians were 0.062149 s sorting versus 0.058430 s selection; at six, 0.062985 versus 0.060846 s. Reports: `opt-a-parallel-selection-native.json`. The candidate passed tiny/adversarial, independent sample seeds 23/41, full public hashes at 1/6/12 workers, address/undefined-behavior and thread sanitizers, and offline Linux full-data validation. Reports: `opt-a-parallel-selection-*.json`. Its board result is pending.

## Refined candidate: actual board record

`run-3e1350a66528` on `072ce9b9046484a76c7e98aebd1e998e0d440d17` passed every gate: T=0.076981 s, M=60,006,400 bytes, S=327, K=20.449888, machine points=65.534547. Record: `../docs/board-opt-refined-acd.json`.

Next experiment: `-march=native` in the Docker build. The official harness explicitly builds native-targeted submissions on the scoring CPU. Offline emulated Linux full-data and tiny hashes pass for all three tracks; reports `opt-native-cpu-containers-{public,tiny}.json`. Emulated timings are not performance evidence for Intel. Source algorithms are unchanged for this compilation experiment.

## Native compilation: actual board record

`run-720ad9c54841` on `f6b17e3b4d532d0dec3952df9da6d8d4297323de` passed every gate: T=0.083108 s, M=59,158,528 bytes, S=327, K=19.737736, machine points=64.764867. Record: `../docs/board-opt-native-cpu.json`.

Observed K is below the generic-CPU build (20.449888), so generic targeting is restored. One practice run does not establish statistical significance. The restored Docker/source inputs match the already-passed generic Linux validation.

## Direct latency parsing and endpoint delimiters

Hypothesis: endpoint scanning and scanning latency twice waste parsing work. A bounded `memchr` finds endpoint delimiters; the latency loop now consumes digits once, checks at most ten digits and uint32 range, and requires the final newline. Every full-data output hash remains exact.

Seven alternating local trials after warmup measured six-worker medians of 0.084737 s prior selection version versus 0.078298 s direct parser; at twelve, 0.082032/0.069035 s (about 16% lower). These launch-inclusive Apple ARM results are not board scores. Report: `opt-a-direct-parse-native.json`. Targeted new-seed, full-data, sanitizer, race, and Linux checks precede submission. The next actual board K decides retention.

## Memory experiment: actual board record

`run-c5403082db13` on `28402fefb8136c3db205d3e312c87eef3b87b29f` passed every gate: T=0.079162 s, M=58,077,184 bytes, S=327, K=20.298444, machine points=65.373137. Record: `../docs/board-opt-memory-cd.json`.

## Parser / D-worker comparison: actual board record

`run-bbd53e3cc9e6` on `c21563dbfc44b1504bf8cc5d05f7fceaa8cbf1dd` passed every gate: T=0.069874 s, M=59,830,272 bytes, S=328, K=21.467492, machine points=66.589066. Record: `../docs/board-opt-parser-a-d12.json`.

The direct parser raises observed K from 20.449888 to 21.467492, so it is retained. Against the original board baseline it is about 7.72x faster.

## Retained source confirmation

`run-c70da1f28b23` on `07f2ac73092f64d98e40825809e88ce7010dca9f` passed every gate at 2026-10-31T04:57:41Z: T=0.069571 s, M=60,276,736 bytes, S=328, K=21.482224, machine points=66.603962. Full record: `../docs/board-opt-retained-acd.json`.

This confirms the retained source rather than a new optimization. A/C algorithms are unchanged from the prior parser comparison; D restores the earlier tested six-worker loader. The spread between unchanged-source practice runs is real, so best observed values and the latest confirmation are reported separately. Final holdout and judging remain separate.

## Second optimization round

Hour-owned workspaces replace whole-input packed records and per-worker72-hour tables. A fresh line-offset prepass preserves every request, then each hour is processed and released independently. Local five-trial median changes from0.085521 s to0.080075 s, while temporary memory is expected to fall; only the board can confirm the cgroup/score benefit. Four-digit parsing is retained here. The exact new-seed, full-hash, memory/UB, race, primitive-model and Linux checks pass. Reports: `round2-layout-*`, `round2-ac-*` and `round2-swar-*`.

Local phase intervals and alternating trials are in `../docs/round2-phase-profile.json` and `round2-layout-native.json`. They are Apple ARM development evidence, not official times.

## Hour-layout / compact-lookup board result

`run-f246379b9c4d` on `d2fd0b53b6cf42a8786845b5d40c21e30865a8ce` passed all gates: T=0.061805 s, M=42,344,448 bytes, S=342, K=24.306889, machine points=69.286469. Exact record: `../docs/board-round2-ac.json`.

The hour-owned layout improves the previous best score to69.286469 and reduces measured memory to42.34 MB. Next isolated runtime hypothesis: limit glibc allocation arenas to2; only the Linux process environment changes and full restricted-container output passes. Actual K will decide retention.

## Allocator / delimiter / private-D board result

`run-430c039bf3c7` on `b5df2af979bda869c0827b4dd59fda40f5a1ebe8` passed all gates: T=0.068332 s, M=35,889,152 bytes, S=343, K=23.883918, points=68.905279. Record: `../docs/board-round2-private-d.json`.

The arena cap lowers measured memory but did not beat the preceding no-cap K24.306889. It is not accepted as a standalone score gain.

## Offline profile-guided compiler experiment

Next experiment changes only the build: GCC profile generation with atomic counters, two sample datasets generated at seeds104729/130363, then profile-use recompilation with missing-profile errors enabled. The training generator is a byte-identical official copy, explicitly exempt from source size by the published harness; only `/solution` enters the final runtime stage. No public seed1 input, training dataset, cached result, or profile file enters that runtime image. The current algorithms/worker counts are unchanged from the preceding board comparison.

Offline Linux full-public/tiny outputs and129 untrained sample/adversarial runs across1/6/12 workers pass collectively. Reports: `round2-pgo-containers-{public,tiny}.json`, `round2-pgo-untrained-containers.json`. Untrained cases include name-table growth, quoted seams/EOF, percentile boundaries, and full-width graph distances. Actual board K decides retention; no compiler speedup is claimed in advance.

## PGO: exact board result

`run-2ae41917013b` on `18896fe59b2dfd93036b023388f29dd0a4108449` passed every gate: T=0.063857 s, M=39,718,912 bytes, S=345, K=24.189551, points=69.18139. Record: `../docs/board-round2-pgo.json`. This is below the preceding best, so PGO and the weaker arena/delimiter experiment are removed from this track.

Next isolated hypothesis: keep hour-owned workspaces and generic GCC, replacing the rejected arena cap with process-local mmap threshold4096. Offline Linux/full/default checks pass; the actual board K remains pending.

## Canonical CSV / banded queue: real board result

`run-73368f11a068` on `a5394d33e9058b843422529374362b00adbc0ecb` passed all gates: T=0.077115 s, M=28,233,728 bytes, S=343, K=23.587787, points=68.63436. Exact record: `../docs/board-round2-canonical-band.json`. The4096-byte mmap threshold lowers memory but scores below the prior best, so it is rejected. Next: isolate PGO on the original hour-owned algorithm with the original allocator environment.

## Isolated compiler /128-band board result

`run-7b5e46ea09f2` on `46504cbb5cda9e3df890ffe202dab4e3f7587393` passed all gates: T=0.061706 s, M=39,182,336 bytes, S=344, K=24.685326, points=69.621943. Record: `../docs/board-round3-pgo-band.json`. Isolated PGO improves the preceding best69.286469 to69.621943; retained.

## Variable-width packing: real board result

`run-9c7fc0032577` on `bba4fe03074368db5bb0bc0b49af917306e9bdb2` passed every gate: T=0.061931 s, M=40,112,128 bytes, S=344, K=24.525137, points=69.480572. Record: `../docs/board-round4-edgepack.json`. Runtime build inputs are unchanged from the retained configuration; the score difference is repeat variation.

Next compiler hypothesis: full-scale training at independent seed1000003, plus sample130363, better represents the scored workload than two samples. In C, sample and full use the same name-pool size, so new-key frequency differs materially. All input/output/profile files remain in builder stages. Public seed1 is not a training input. Validate on other seeds and real board K; retain only measured overall gains.

## Full-scale training / specialized decoder: real result

`run-96c43d019bcc` on `eb16c07b177d5213110083063d4b38e50548714c` passed all gates: T=0.064078 s, M=39,161,856 bytes, S=344, K=24.226658, points=69.214675. Record: `../docs/board-round5-full-pgo.json`. Full-scale training is below the prior69.621943-point best, so restore the sample104729/130363 build.

## Dense C dictionary: exact board result

`run-1f9a7602cf67` on `cb8cbedcd20a28153ebe790bb58f6b4c9bcc5f26` passed all gates: T=0.060856 s, M=39,796,736 bytes, S=344, K=24.779894, points=69.704972. Record: `../docs/board-round6-dense-c.json`. Runtime/build inputs are unchanged from the retained configuration; this small higher observation is repeat variation, not an algorithm gain.

## Narrow graph-loader board result

`run-3412a3d7b27a` on `61e345f753f6011b6ecd66c6cbba86030d72fa28` passed every gate: T=0.061427 s, M=41,316,352 bytes, S=344, K=24.480291, points=69.440829. Record: `../docs/board-round7-narrow-d.json`. Runtime/build inputs are unchanged; the observation is repeat variation.

Next memory hypothesis: replace hour line offsets/packed records with two input passes, shared exact endpoint IDs and four-byte local count cells reused as scatter cursors. Stream bounded per-hour buffers in token order. Five alternating full-data native medians: old12=0.073678 s /289.08MB RSS, new12=0.089378 s /264.13MB, new6=0.091219 s /259.56MB. This is slower locally and saves about25–30MB; no runtime gain is claimed. New independent samples, exact full outputs, count/error-wrap cases, table growth, strict sanitizers/concurrency models and Linux checks pass. A /dev/full integration test returns nonzero within25 s and does not deadlock. Actual cgroup memory, canonical S and time jointly determine K; board result pending.

## Flat/streaming A: exact board result

`run-26d56b69b86e` on `2917982a9d0d26a813aacd1f2065331f6866016c` passed all gates: T=0.076989 s, M=32,235,520 bytes, S=504, K=21.69994, points=66.822927. Record: `../docs/board-round8-flat-a12.json`. Memory falls to32.24MB, but runtime/source cost lowers K below24.779894. Reject this exact layout and restore the hour-owned sample-PGO configuration from61e345f. The six-worker local variant is not submitted; no six-worker board result is claimed. Reproduce the rejected source at2917982.

## SIMD CSV comparison: exact board result

`run-e84f4acc4192` on `1b21266eeee60232176372208d6c4120465ad988` passed all gates: T=0.061959 s, M=40,357,888 bytes, S=344, K=24.489659, points=69.449137. Record: `../docs/board-round10-simd-c.json`. Source/build inputs are unchanged from the retained configuration; the result is repeat variation.

## Final retained-source confirmation

`run-4055dcf05865` on `d28fe2590101b6b9a362e71b7bd8ee8f379f0741` passed all gates at 2026-10-31T07:14:38Z: T=0.061166 s, M=40,898,560 bytes, S=344, K=24.582383, points=69.531199. Exact record: `../docs/board-retained-final.json`. Runtime/build inputs match 61e345f byte for byte. This confirms the selected combination; historical best observations remain separate, and no repeat delta is called an algorithm gain. Subsequent documentation updates change no runtime/build/metadata input.

## Small-group selection comparison

An isolated round12 candidate applied the existing progressively restricted exact nth_element sequence to every group, removing the small-group sort branch. Nine alternating full-public native runs per configuration all matched the official SHA. At six workers baseline0.068864 s versus candidate0.069446 s; at twelve0.057893 versus0.058582. Reject before promotion: the candidate is slightly slower at both counts. Raw measurements: `../docs/round12-local-bench.json`. No board run or gain is attributed to this rejected A prototype.

## Lossless line-offset deltas

Retain the hour-owned algorithm but store a uint16 delta from the preceding line position in each worker/hour list. Delta65535 is an escape followed by the full uint32 absolute position in a side vector; larger gaps use the same escape. Decoding begins at zero and reconstructs every position exactly. The existing input-size guard makes all absolute positions representable. First offsets of zero, exact65534/65535/65536 gaps, repeated escapes, larger gaps, worker partitions and both vector lifetimes are covered.

Nine alternating full-public Apple trials measure0.063860 s original versus0.061182 s compressed, with max process RSS290,226,176 versus280,608,768 bytes. Every hash matches. Fresh sample seeds821/823/827, full public1/6/12-worker hashes, strict memory/UB and race sanitizers, exact-gap reference cases and48 restricted Linux replays pass. The replay image ID matches the exact Linux build. Reports: `../docs/round15-a-offsets-*.json`. These are local selection evidence; actual board K decides retention.

## Compressed offsets: real board result

`run-c26f23dfdc36` on `11e467385c4d8869a4afbcc7bb8a80d42ff99e98` passed every official gate: T=0.060625 s, M=34,947,072 bytes, S=362, K=25.286579, points=70.144504. Record: `../docs/board-round15-offsets.json`. Compared with the previous best69.704972/K24.779894, the measured total K improves about2.04%; peak memory falls12.19% from39,796,736 bytes while runtime is approximately unchanged. The source-size increase is included in K. Retain compressed offsets. Current A/C/D runtime/build inputs match this exact all-gates-passing commit in round15-final-source-match.json; further documentation changes do not alter scored inputs.

## Fresh round16–18 screening

Sampled endpoint hashing is flat on the old layout (0.053813 s standard versus0.054103 sampled). Ordered output publication with a mutex, preserving the hour algorithm, passes full output hashes but is slower (0.071252 s baseline versus0.087064 streaming) for only2.87MB lower native RSS; rejected before broader validation or board promotion. The first round16 pass overlapped some browser activity and is screening evidence only. A phase diagnostic attributes about0.014 s to line indexing and0.027 s to hour processing, plus output/launch overhead; it is instrumented Apple evidence.

A fresh shared exact dictionary lets parsing produce compact records directly, avoiding a second text visit. The six-byte form measures0.053506 s versus0.062961 baseline but adds8.52MB native RSS. A four-byte form uses12 endpoint-ID bits,1 error bit and19 latency-tag bits; the all-ones latency tag consumes the next full uint32 from that worker/hour's side list. Equal-to-sentinel and larger values both use the side list; no latency is rounded. Exact full names are compared after a48-bit hash fingerprint, so collisions never identify names. IDs are assigned from this run's input only. The published catalogue has1,842 paths;4,096 IDs leave spare room and the model exercises ID4095 and controlled overflow. The standard-hash four-byte form measures0.052359 s and279.63MB RSS versus0.062961/280.56MB baseline over nine rotating, hash-checked trials. Sampling a few name bytes only saves another2.4% locally, with extra source cost, so the simpler full hash is selected. These are selection hypotheses; real board K decides retention.

Selected four-byte records pass fresh tiny/sample seeds839/853/857 and full public hashes at1/6/12 workers, strict ASAN/UBSAN and TSAN, simultaneous full-hash collisions and unique-ID models, reserved-state/ID4095 boundaries, exact latency escapes at524286/524287/524288/MAX_UINT32 across partitions, and48 restricted GCC15/Linux cases. GCC15 ASAN/UBSAN additionally passes the endpoint model. Actual native and Linux default entrypoints pass without thread/path overrides. Reports: `../docs/round18-*.json`. Every replay image matches the exact offline build ID. A model initially used a non-coprime key sequence that did not visit its assumed700 keys; changing the test count to701 corrects coverage before model acceptance. No runtime fix was needed for that test setup error. No Intel score is claimed before the exact-commit board run.

## Compact parse: exact board result and next memory refinement

Round18 commit b1388b098fc6ffd4fb8471b7cdd9d8c146fd9564 passed every official gate: run-0e5b98b8a59a, T=0.051629 s, M=38,772,736, S=376, K=26.685422, points=71.313704. This beats the preceding70.144504/K25.286579. Record: ../docs/board-round18-compact-batch.json. Retain fused exact four-byte records.

Next refine allocation: reserve only the worker/hour vectors that receive records, shrink the exact endpoint hash table from32768 to8192 slots (maximum4096 distinct IDs, full equality retained), and release table metadata after copying views into the still-mapped input. Nine rotating public-hash-checked native trials: current eager32k0.048259 s/279.27MB, eager8k0.048967/278.35MB, lazy8k0.047546/264.32MB. Memory drops about14.94MB locally; Intel/cgroup K is still decisive.

Round23 exact source passes fresh samples881/883, adversarial1/6/12-worker ASAN/UBSAN, TSAN seed887, full public hashes, exact latency escapes/ID4095, strict GCC15 endpoint collision/capacity models,45 Linux fixture replays, and actual native/Linux defaults. Reports ../docs/round23-*.json. No precomputed answers or seed-dependent runtime is introduced.

Round23 commit44a902b6b7db427741a1bfd75c99dbee184ec909 passes every gate: run-0eb126695b0c, T=0.053847 s, M=34,705,408, S=378, K=26.694417, points=71.321022. The lower-memory layout produces a tiny0.007318-point new best; this is effectively level within run variation, not proof of a speedup. Retain the measured lower-memory exact layout. Record: ../docs/board-round23-lazy-quote-band.json. Eleven rotating native comparisons of this layout at6/8/12 workers measure0.052462/0.047105/0.046265 s; retain12. No separate worker-change gain is claimed.

The unchanged lazy/8k runtime repeats at71.545464/K26.971760 on1856d3937190d20e2b43dc49234e4d49238233b7, run-ffa95844e6e4, T=0.052903 s/M=34,447,360, all gates passed. This is repeat variation, not an additional algorithm gain. Record: ../docs/board-round24-narrow-c-retained-d.json.

Next test only the small-group sort cutoff64→32. Eleven rotating native full-public trials: cutoff64=0.045893 s,16=0.045224,32=0.044710,128=0.045277; all exact hashes match and memory is effectively unchanged. Select32 as a modest local hypothesis without additional code/storage. Fresh929/937 ASAN/UBSAN,941 TSAN, adversarial and escape/ID boundary references, full public1/6/12-worker hashes,39 exact-image Linux replays and actual default entrypoints pass. Reports ../docs/round28-a-sort-threshold-bench.json and ../docs/round29-a-*.json. Actual K decides retention.

Round30 commit2c6c51e452faf284f013fd6b12d7333c310dcecc passes every official gate: run-982572415f2b, T=0.050484 s, M=34,037,760, S=378, K=27.676524, points=72.105578. This beats the preceding71.545464/K26.971760; retain cutoff32 on the fused/lazy layout. The exact total-score difference is recorded; a single run does not remove observed timing/memory variation. Record: ../docs/board-round30-cutoff-parity.json.

Round32 ce5ad53ee45296595a6eab2c9ac74d77fa4c61e7 repeats unchanged A source at71.826222/K27.322752, T=0.051646 s/M=34,291,712, run-33b64ac59910; every gate passed. Historical72.105578 remains the best observation; no A algorithm changed. Record: ../docs/board-round32-balanced-frontier.json.

## Final restored-combination confirmation

Exact commit 71a023706495a99867f32a3e1856317f0d9e73bb passes check/build/correctness/timeout/sandbox for all A/C/D. This track's run run-aea59f5857c9: T=0.051652 s, M=34,152,448 bytes, S=378, K=27.343411, points=71.842634. Record: ../docs/board-round32-retained-final.json. Every one of the27 retained runtime/build/metadata inputs matches this scored commit in round32-final-source-match.json. All weaker runtime experiments are removed. This repeated-source result confirms the combination; historical best and latest confirmation remain separate, and repeat deltas are not called algorithm gains. Further updates are documentation/evidence only.

## Round38: repeated-hour and fixed-method parser

Fresh native diagnostics place most A time in parsing, not selection. Block/deque buffers, larger reservations, front endpoint caches and isolated hour caching do not establish a better local total; their raw hash-checked results and patches remain outside scored folders. Exact method-width parsing alone is modestly faster. The combined parser caches the eight timestamp bytes containing month/day/hour and its record-vector pointers, recomputing whenever that prefix changes. It never assumes a bound on input disorder. The seven method spellings and their widths come directly from the frozen grammar; all legal minimum-length40-byte rows are supported.

Eleven rotating public-hash-checked Apple trials: baseline0.053022 s/264.52MB, method-only0.050976, hour-only0.056285, combined0.048550/264.34MB. Select the combined hypothesis for a real K test; no Intel gain is claimed from these values. Fresh1009/1013 strict ASAN/UBSAN,1019 TSAN, full-public1/6/12, all method×72-hour×endpoint×status×latency combinations in ordered and arbitrarily shuffled data, exact escapes/ID4095,45 exact-image Linux replays and actual defaults pass. Reports ../docs/round38-*.json. Retain only after genuine board comparison.

Round38 f378b2e51c3a9e3236a37bd0424317b633befa42 passes every gate, run-3a899e2f4eec: T=0.051818 s/M=34,263,040/S=404/K=27.011064/71.577084 points. It does not beat retained72.105578/K27.676524, so the hour cache and larger fixed-method dispatch are not retained. Next use only a bounded64-bit separator mask, with the original hour calculation. A legal row is at least40 bytes and the method begins at28, so the8-byte load is in range; all seven methods place their separator within that word. Byte order is asserted for the specified amd64 target. The first-space mask retains the exact delimiter; scalar latency/endpoint handling is unchanged.

Thirteen rotating native trials: retained0.047507 s, round38=0.046994, lean word=0.045102, cached word=0.044784; memory similar. Choose the lean form to avoid the source-size cost of caching for the small extra local difference. Fresh isolated1049/1051 ASAN/UBSAN,1061 TSAN, full-public1/6/12, minimum/maximum endpoints and all method/hour/status/latency combinations in ordered/shuffled data, exact escapes/ID4095,69 image-matched Linux cases and actual defaults pass. Only real K decides retention. Reports ../docs/round43-*.json.

Validation harness note: the original round38 native sanitizer/race jobs could share adversarial output folders. Generated sample seeds were separate. The suites were rerun with unique run IDs, all passed, and1047 image-matched Linux replays passed. These isolated reports are authoritative for per-binary adversarial attribution. Original reports are preserved with that limitation; no runtime fix was required. Round43 uses isolated names/output paths from the start.

Round43 273c7094c1ca4a1594486abdc45e52427cbdaae8 passes every official gate: run-687fbe77e4eb, T=0.052015 s/M=34492416/S=385/K=27.119162/71.663813 points. Neither the lean A word scanner nor aligned C groups beats the previous best. Restore exact bf75194 runtime/build/metadata for this track. The validated losing candidates remain in commit273c709 and raw reports; no gain is claimed. Record: ../docs/board-round43-word-alignment.json.

Further ordered output writer screening uses thirteen rotating full-public trials with every output SHA checked. A baseline0.048363 s versus writer0.049008 s, almost unchanged RSS. Reject before broader sanitizer/Linux/board promotion; no general correctness or official gain is claimed. Source patch ../docs/prototype-patches/round45-ordered-writer.patch applies tobf75194; raw report ../docs/round45-46-writer-split-bench.json.

Current-layout worker retest, nine rotating full-public hash-checked native trials:4/6/8/10/12 workers =0.063911/0.055665/0.048701/0.047119/0.046557 s. Keep12; lower concurrency does not justify a board change. Report ../docs/round47-worker-loader-bench.json.

Next Linux-only hypothesis: request MAP_POPULATE for the current read-only input mapping when the platform defines it. The kernel can populate page tables/read ahead before parallel parsing, potentially reducing first-touch stalls. This is ordinary process-local input I/O; it neither changes the sandbox/host nor recognizes a dataset. The mapping remains read-only/private and every row is still computed. The mmap call tolerates partial prefaulting normally. No Mac time is claimed for this Linux feature. API reference: https://man7.org/linux/man-pages/man2/mmap.2.html .

Fresh1093/1097 strict ASAN/UBSAN,1103 TSAN, all adversarial/full1/6/12 outputs,69 exact-image Linux replays (including minimum rows/all methods/hours/escapes/ID4095), actual native/Linux defaults and a separate69-run GCC15/Linux strict ASAN/UBSAN integration suite with MAP_POPULATE availability asserted pass. Source identity: ../docs/round51-candidate-source-match.json. Real K must beat27.676524/72.105578.

Round51 c4f966f2d0e6f0602fac16f0eb8218b8f16499fd passes all gates: run-5775bb61c3d7, T=0.059545 s/M=33251328/S=383/K=25.552896/70.372006 points, build16.268 s. This loses to the retained best; revert to exactbf75194 runtime/build/metadata. Record ../docs/board-round51-prefault-counters-loaders.json.

Minimal library-delimiter retest on the restored parser is rejected before broader sanitizer/Linux/board promotion. Thirteen paired full-public native trials all match hashes; A baseline0.060293 s/method memchr0.063072 s. Neither is faster. Background desktop activity is not isolated; only paired screening is claimed. Raw round54-delimiter-bench.json and reproducible bf75194 patch in docs/prototype-patches preserve the experiment.

## Selected-combination real confirmation

Exact commit 07c31360af938e391c3e09e3d21f969a1709b092 passes check/build/correctness/timeout/sandbox for every entered track. This track run-7263989cd59b: T=0.064861 s/M=33828864/S=378/K=24.447324/69.411566 points. The current historical best is72.105578/K27.676524 at2c6c51e452faf284f013fd6b12d7333c310dcecc, with byte-identical runtime/build/metadata inputs. This repeat is not an additional algorithm gain. All27 selected inputs match the scored source and each current best record in ../docs/round55-final-source-match.json.1056 current-image Linux replays and actual defaults pass. A/C additionally pass fresh isolated1109/1117 ASAN/UBSAN,1123 TSAN and all-country-width checks; D's exact round50 isolated strict sanitizer/race/independent source is retained. No unscored prototype remains in a track folder. Further documentation updates change no compiled input. Record ../docs/board-round55-selected-final.json.

## Current-layout allocator retest

The earlier arena cap lost on a different hour-owned/line-offset layout. Retest process-local MALLOC_ARENA_MAX=2 on the retained fused four-byte/lazy-vector implementation, where parse workers allocate record vectors and hour workers later release them. Only final-image ENV changes. No Mac allocator timing is offered for glibc. A code is byte-identical to the strict selected-source sanitizer/race context; public Linux output,69 current-image boundary/reference replays and actual defaults pass. Real K must exceed27.676524/72.105578. Proof ../docs/round60-candidate-source-match.json.

Endpoint early prefetch and8/16/32-row pipelines are screened in eleven rotating full-public native trials: baseline0.051907 s, prefetch0.051403, batch8/16/32=0.053076/0.053962/0.053308. All hashes pass, but no worthwhile total gain is established; no broader sanitizer/board acceptance is claimed for those variants. Sources and raw round57 reports are archived.

Round60 a5887ec541782b0ad141ecd878f1c7b04280ccde passes every gate: run-b48e70de9e1a, T=0.065967 s/M=30167040/S=379/K=24.793544/69.71693 points. The candidate does not beat the retained best and is reverted to exact57cc23e runtime/build/metadata. Record ../docs/board-round60-intel-c-allocator-a.json.

## Direct ownership of compact record pages

Related high-level inspiration: the public [Gigatron A performance log](https://raw.githubusercontent.com/coreyjlord-dev/speed-demon/speed-demon/track-a/PERF.md) discusses releasing completed storage. No implementation was viewed/copied; this allocator is independently event-written for our existing std::vector representation. A stateless POSIX mapped allocator backs only the compact request-record vectors. Capacity growth preserves all elements; the hour owner unmaps the old record buffers only after scattering every exact latency. Large-latency escape vectors, mapped input/path lifetimes, grouping and quantile arithmetic are unchanged. This avoids retaining cross-thread-freed record pages in glibc arenas. Arena cap2 from the losing round60 is removed.

Eleven paired full-public native trials: retained0.048677 s/264.31MB process RSS, mapped0.049202/259.00MB. Slightly slower locally, about5.3MB less peak RSS; only actual Intel/cgroup K can decide. The extra allocator source is charged. Models cover values/growth/alignment/overflow, cross-thread destruction, Darwin physical residency and Linux unmapped-address verification. Initial model incorrectly assumed Darwin mincore returns an error after unmap; diagnostics show successful munmap with residency cleared. The observer was corrected without changing production code, preserved in round62-allocator-model-correction.json. Both native and GCC/Linux strict models pass.

Fresh1163/1171 ASAN/UBSAN,1181 TSAN, all A adversarial/full-public/default checks, exact escapes/ID4095/method-hour Linux cases, and69 current-image Linux replays pass. All28 combined build inputs match round62-candidate-source-match.json. Real K must beat27.676524/72.105578.


## Round62 real result and smaller/native compilation follow-up

Commit9933500b9335ab4866a21ac96990dac5fa2f8cb5, run-b063bfc456d2 passes all five gates: T0.055207 s/M26,333,184/S411/K27.512520/71.976519 points. The mapped vectors lower charged memory22.63% versus the historical34,037,760-byte best, but source/time cost leaves total K0.59% below27.676524. No A gain is claimed. Record ../docs/board-round62-mapped-splits-endpoints.json.

Next isolated combined candidate preserves that directly mapped layout, uses a bounded scalar latency digit loop with the same10-digit/full-uint32/newline validation, removes the unused four-digit helper and unused Output::save utility, and compiles/trains with -march=native. The remaining decimal primitive model includes D's identical still-used helper. This is ordinary removal of unused code; no formatter suppression, answer storage or protocol change is used. The official harness routes native CPU builds to the scoring host.

Thirteen rotating full-public native trials, all hashes checked: retained0.049346 s, mapped0.051628, scalar-retained0.049942, scalar-mapped0.051011. No native Intel-feature gain is claimed. Both scalar allocator combinations pass fresh1193/1201 strict ASAN/UBSAN,1213 TSAN, full1/6/12 and adversarial suites. Only mapped/scalar/native proceeds to exact Linux/default/replay/GCC integration validation. Unselected inline/prefetch/degree prototypes and limits are preserved in round63-64-prototype-index.json. Real K must beat27.676524.


Round64 44d8c63, run-3620a71d60a0, all gates pass: T0.059905 s/M25,292,800/S382/K26.919313/71.503199 points. Exact run ID is in ../docs/board-round64-native-scalar-sse.json. It fails27.676524, so restore all57cc23e A inputs, including decimal.hpp, and remove the mapped allocator. The native/lean combination saves charged memory but does not improve total score. No gain claimed.


## Search-directed full-name hardware hash

Retained A on round67 is unchanged57cc23e: run-71111a1ff019, T0.054356 s/M34,086,912/S378/K26.664862/71.296967 points, all gates passed. This is repeat variation; historical72.105578/K27.676524 remains the threshold.

Five instrumented full-public Apple runs, every hash checked, median phases: opening2.160 ms, parsing25.000, dictionary0.174, aggregation/selection/formatting7.665, writing10.519. These are local diagnostics; output storage/CPU differ from Intel. Parsing is the largest local phase. Exact raw report ../docs/round68-retained-phase-profile.json.

The new candidate uses hardware CRC32C over every endpoint byte in bounded8-byte loads, with zero-padded tail and length seed, then a64-bit multiplication to spread the hash. Full string length/byte equality still decides identity, so32-bit CRC collisions never merge endpoints. No endpoint catalogue or input recognition is used. On amd64 the build explicitly enables only SSE4.2 rather than all native CPU optimizations; ARM retains standard hashing. The scoring i5 supports the instruction. This is a target-specific hypothesis, not an Apple timing claim.

Fresh1237/1249 ASAN/UBSAN,1259 TSAN, full1/6/12 outputs, all methods/hours, exact escapes/ID4095 pass. GCC15/Linux explicitly executes the SSE4.2 path: a separate bit-polynomial CRC reference matches every byte/length/random/protected-page case and4096 IDs. Deliberate full-hash collisions, publication/reserved states and overflow models pass.69 exact-image Linux replays plus69 extra -msse4.2 GCC ASAN/UBSAN integration runs and actual defaults pass. Legacy/shared and current/private name-model API dispatch both pass native/GCC checks; model bodies remain independent exact references. Real K must exceed27.676524.


Round70 7402c7f, run-67c43ed0dfc4 passes all official gates: T0.066032 s/M34426880/S405/K23.89623/68.916469 points. The hardware CRC version loses to27.676524, so restore every57cc23e A source/build/metadata input and README. No A algorithm gain is claimed. Actual final compilation uses the standard full-byte hash and full equality. Exact report ../docs/board-round70-endpoint-crc.json.


Final selected combination 0008c8ae9868ebf4746fa228ec813ab2dda8ab6d, run-15bb24b2ed98 passes check/build/correctness/timeout/sandbox: T0.050478 s/M33771520/S378/K27.721673/72.140972 points. All27 current inputs match this exact commit and each best track source in ../docs/round71-final-source-match.json. A/C small new best observations are unchanged-source variation; the two real C algorithm improvements are recorded separately. Further updates are evidence/prose only. Report ../docs/board-round71-selected-final.json.


## Exact per-worker cache with globally published stable views

The earlier256-entry front caches did not help. This candidate uses4096 direct-mapped16-byte cache entries per parser and shares the first globally interned view of each endpoint through an ID-indexed canonical array, published before the existing release state. Full byte equality guards every local hit; collisions evict and call the original full-hash/full-equality global interner. Cache identity is never a sampled hash alone. Long keys beyond the local16-bit length use the original full-view fallback; no truncation occurs. Global ID capacity/overflow and full uint32 latency escapes remain exact. After parser joins, output paths copy the dense canonical views instead of scanning hash slots.

Eleven rotating full-public native trials: retained0.042613 s, growable4096=0.041343, growable8192=0.040753, direct4096=0.040901. Choose direct for smaller memory/source versus the tiny extra8192 speed. Its peak native RSS264.65 versus264.27MB is slightly larger. This4.0% local speed hypothesis must earn its actual source/memory cost on Intel.

Fresh1283/1289 ASAN/UBSAN,1291 TSAN, public/default1/6/12, exact method/hour/escape/ID fixtures and69 current-image Linux cases pass. Dedicated byte/guard/eviction/long-key/4096-ID models deliberately collide all sampled bytes while retaining distinct full keys; concurrent canonical publication passes separate native TSAN and native/GCC strict ASAN/UBSAN. Frozen75 source proof matches every built input. Real K must exceed27.721673/72.140972.


Round75 commit342c0aa, run-74e8fa2d125f, passes all five official gates: T=0.047604 s, M=34332672 B, S=424, K=27.966381, points=72.331814. Retain the exact local-cache/canonical-view change; it exceeds prior72.140972/K27.721673. Raw result: ../docs/board-round75-cache-prefetch-labels.json. One observation does not remove timing/memory variation.


Round77 unchanged75 A source passes every gate again: run-defe2eced259, T0.045519 s/M34893824/S424/K28.507127/72.747672 points. The better observation is repeat variation, not another algorithm change. Round78 screens reject cache2048 (0.042615 versus0.040629 s), cache8192 (0.040539, larger RSS for0.2%) and parallel pwrite output (0.040315, only0.8% and more source/RSS). Every trial matches the full public hash. No broad sanitizer/Linux/board claim applies to these unselected prototypes. Raw ../docs/round78-cache-output-wide-bench.json.


Round79 unchanged75 cache/canonical-view source passes every gate, run-5414758103a4: T0.045287 s/M34283520/S424/K28.681090/72.879783. This new best observation is same-source variation, not an additional algorithm. Raw ../docs/board-round79-small-wide-fallback.json.

## Bounded word endpoint delimiter scan

Only endpoint-space search changes from library memchr to bounded8-byte loads on little endian. XOR with spaces, then the zero-byte expression locates the first matching byte. Borrowed higher mask bits cannot precede the first real zero; only the least set byte is returned. Complete loads are range-checked and a library tail handles remaining bytes; other endian layouts retain library search. Full endpoint cache/global equality, every field/parser/record/escape/quantile/output rule and generic GCC flags are unchanged. This contains no endpoint catalogue.

Eleven rotating sequential native full-public trials: retained0.041698 s, word0.039742 (4.7% faster),128-bit vector0.040039. Word81 additionally wins in a later paired context0.039136 versus retained0.041404. Both are local screens, never an Intel score. C from_chars loses0.068693 versus0.059145; four-digit C adds source for only1% improvement and is not promoted.

A larger in-place raw-record permutation prototype reuses the largest parsed hour buffer, collects exact full32-bit escape values per endpoint and interprets raw-tag percentile ranks against independently sorted full-width escapes. Full-public output hashes match, but it loses locally: original0.041404 s/264.37MB, word0.039136/264.55MB, in-place0.042392/263.88MB, combined0.040769/263.95MB. The roughly0.5MB RSS change does not justify slower code/more source. Both in-place variants are rejected before broader sanitizer/Linux/board claims.

The selected word scan passes fresh1333/1337 strict ASAN/UBSAN,1361 TSAN, full1/6/12 outputs, all methods/hours/escapes/4096-ID cases,96 exact-current-image Linux replays and actual defaults. New native and GCC15 strict protected-page/scalar-reference models cover every byte/offset,100000 random buffers, empty/no-match/short tails. Existing unchanged cache/canonical-publication/decimal models remain tied to exact75 header bytes; no altered model is substituted. All28 selected inputs match frozen81 and current images; C restores71 and D restores75 with147/1032 current-image independent fixture replays. Real total K must exceed28.681090/72.879783.


Round81/576feb0 bounded space scan passes every official gate, run-59d6c4c4deb0: T0.046072 s/M34525184/S444/K28.200137/72.512561. It loses to28.681090/72.879783. Restore every342c0aa A runtime/build/metadata input and README; remove space_scan.hpp, its Docker COPY and Make dependency. The native/GCC protected-page model and fresh integration passes remain evidence for the rejected scanner, not a selected Intel gain. Raw ../docs/board-round81-bounded-space.json.


Final selected combination b80c1ab98657ab4f5d4d6ce3ffe83b9012c2dcda, run-bcec1deb5817, passes check/build/correctness/timeout/sandbox: T0.046913 s/M34394112/S424/K28.16152/72.482805 points. All27 current runtime/build/metadata inputs and each current best source match the selected commit in ../docs/round87-final-source-match.json. Historical best and this latest same-source confirmation remain separate; a lower repeat is not hidden or labelled a new algorithm regression. Current A96/C147/D1032=1275 matching-image fixture replays, fresh combined Make/public1/6/12 and actual native/Linux defaults pass. Later updates are evidence/prose only. Raw ../docs/board-round87-selected-final.json.


## Full-size independent profile training on the retained cache algorithm

A still trains on two310k-row samples while the full task has3.1M rows, so group-size/quantile/allocation branch frequencies can differ. Change only the first training invocation to independent seed1000003/full, keeping sample130363, generic GCC flags, exact algorithm and all fallback paths. This follows the official permitted synthetic PGO rule; public seed1 is not used for training and no input/output/profile enters the final image. No Mac timing is claimed for a GCC build-only change.

A's complete runtime C++/headers/metadata/generator are byte-identical to selected75; only Docker training changes. The newly compiled pinned offline Linux image passes full-public,96 independent boundary/method/hour/escape/ID cases and actual defaults. The unchanged algorithm's75 strict native/GCC/sanitizer/race proof remains, explicitly distinguished from the new image checks. Actual K must beat the current observed A best in88 start feed.

Independent2/4-stream parser prototypes90 are slower in eleven rotating hash-checked native trials: retained12=0.040942 s;2streams at6/12=0.047337/0.041113;4streams at6/12=0.047888/0.041907. RSS also does not earn a useful tradeoff. Reject before broad sanitizer/Linux/board claims. Raw ../docs/round90-independent-stream-bench.json.


Round95/13e3224 full-size PGO passes gates, run-c26dc17888a8: T0.045529 s/M34897920/S424/K28.503327/72.744778. It does not beat the88 same-source best; restore exactcfd094c training/runtime/build/metadata and README. No full-training gain is claimed. Raw ../docs/board-round95-full-pgo-pause.json.


Rounds101/102 native full-public screens reject a dedicated12-total-thread ordered writer and alternate small-group nearest-rank selection. Writer0.040871 versus0.041513 s saves only0.41MB native RSS for added synchronization/source, so no promotion. Median-plus-exact-largest-tail selection below20/32/64 measures0.041232/0.041256/0.041646 versus0.040912; all output hashes pass but no gain. Neither received broad sanitizer/race/Linux or official proof. A restores exact selected75 runtime/build/metadata and original sample104729/130363 PGO after95 full-profile training loses actual K. Restored exact image passes current reference/default checks.


Round107 unchanged75 source passes all5 gates, run-1e5dd8fec7f1: T0.051471 s/M34615296/S424/K26.851256/71.448230. This lower repeat is variation, not a new algorithm regression; best72.924546/K28.740275 source remains byte-identical. Raw ../docs/board-round107-owned-loader.json.


## Native CPU targeting isolated on current exact endpoint cache

Earlier f6b17e3 native targeting used the old parallel layout;64 combined a scalar parser, mapped allocation and native compiler. Neither isolates native targeting on the accepted75 exact4096 cache/canonical-view algorithm. This candidate changes only both GCC profile-generation/use passes to-march=native. Original sample104729/130363 training, generic source algorithm, full-key fallback,32-bit escapes, grouping/quantiles and metadata are byte-identical to selected109. The official harness explicitly routes native builds to the scoring CPU. No Mac timing is offered for an Intel compiler experiment, and no public seed1 training or runtime answer/profile file is introduced.

The new pinned offline Linux image passes full-public,96 independently solved method/hour/escape/ID/reference cases and actual defaults. Exact75 runtime source retains its strict sanitizer/race/native-GCC model proof; no changed-source sanitizer pass is fabricated. All27 candidate111 source/image/config inputs match in round111-candidate-source-match.json. Keep only if actual K exceeds28.740275/72.924546; otherwise restore exact6e5950c A Dockerfile.


Round111/cc66c82 native-only compilation passes all5 gates, run-b8ec4dc26d9b: T0.047929 s/M34766848/S424/K27.801439/72.203363. It loses to28.740275/72.924546. Restore exact6e5950c A Dockerfile, preserving original generic GCC/sample training. No gain is claimed from the allowed target-specific compiler change. Raw ../docs/board-round111-native-a-arena-c.json.


## Calendar identity over the frozen72-hour range

The frozen A specification guarantees every seed/scale timestamp is between2026-10-30T18 and2026-11-02T17 inclusive. On Oct30/31 and Nov1/2, the last month digit plus last day digit gives0/1/2/3. Replace full two-digit month/day parsing and the month-dependent adjustment with that exact day index, then the same24*day+hour-18 calculation and0..71 range check. Every row's actual bytes are still parsed; this is a calendar-domain algebraic identity, not seed/input recognition or a stored answer. No ordering bound is assumed. Standard vectors, exact cache,32-bit escapes, counts/errors/quantiles/output and original generic/sample PGO remain unchanged.

11711 rotating native full-public hash checks: retained0.041321 s; bounded0.041388; date0.040664; date+bounded0.041250. Within-rotation median ratios are1.00452/0.98213/0.99828. Choose date alone: modest1.8% native hypothesis, no additional memory or buffer code. No Intel speedup is claimed before real K.

Fresh1543/1549 strict ASAN/UBSAN,1553 TSAN, full1/6/12, independent all72-hour×method×endpoint×status×full-latency combinations in ordered/shuffled inputs, exact19-bit escape/4095-ID cases,96 actual-image Linux reference replays and actual defaults pass. All27 inputs/images are tied in round118-candidate-source-match.json. Unchanged helper/cache/decimal/guard/collision models retain exact75 proof; the changed calendar mapping has exhaustive independent reference coverage. Actual K must exceed28.740275/72.924546.

Bounded-array114/116 prototypes remain unselected. Uninitialized capacity is derived conservatively from chunk bytes; only an appended prefix is read, and arrays release after scatter.114 native0.041621 versus0.041034 is1.37% slower with4.72MB more RSS. A local unprivileged unshipped wrapper verifies its own8GiB cgroup limit and reads memory.peak after each full-output run:5 alternating medians281698304 retained versus276619264 raw bytes. This includes shell/emulation/kernel/cache and is not official scoring memory. A missing old image prevented the initial observer run; it was rebuilt from exact source and both images pinned without pulling before comparison.116 declaration-level nonmovable ownership receives separate fresh1517/1523 sanitizer,1531 TSAN and method/hour/escape proof; no exact116 GCC/official pass is invented. Extra source/virtual headroom and uncertain target tradeoffs do not justify including buffers in118.


Round118/ea8bfe3 calendar-only arithmetic passes all five real gates, run-a27c5733986a: T0.047234 s/M34418688/S422/K28.081565/72.421065. It does not beat K28.740275/72.924546. Restore every A runtime/build/metadata input and README to all-gates selected6e5950c; preserve this losing record. The date identity is correct but no score gain is confirmed. Raw ../docs/board-round118-calendar-a.json.


Selected restoration119/f69d4db, run-60e972fc1217, passes all five real gates: T0.04751 s/M34570240/S424/K27.955452/72.323326. All27 selected inputs exactly match6e5950c. This is a lower same-source confirmation, not an algorithm improvement; historical bests remain separate. C's unusually slow identical-source repeat is retained honestly, with no code regression asserted from one observation. Raw ../docs/board-round119-selected-confirmation.json.


Round122 direct per-endpoint full32-bit latency buckets are rejected at native screening only. Stable per-parser slabs link15- or31-latency nodes, store exact counts/errors in per-hour/key buckets and gather each endpoint directly for unchanged nearest-rank selection. This removes packed-record count/scatter passes and escapes but adds metadata, small-node allocation and random writes. Eleven rotating full-public hashes all pass: retained0.041205083 s/264454144 RSS;15-value0.043750834/275824640;31-value0.044085916/283475968. Paired median ratios1.05204/1.08271. Neither earns broader pool/sanitizer/race/GCC or actual-board validation. Source patches/parents and scope are in round122-prototype-index.json. No new A gain is claimed.


Round121/e3eb08d unchanged selected source passes all five actual gates, run-98fa1c2391cc: T0.047312 s/M34545664/S424/K28.017872/72.371758. This lower repeat remains separate from the best; no additional algorithm regression is asserted from unchanged-source variation. Raw ../docs/board-round121-structural-c.json.


Round124/b3d0cef unchanged selected source passes every actual gate, run-30aa1bd91a8c: T0.048031 s/M35139584/S424/K27.712734/72.133969. Same-source repeat only; preserve historical best separately. Raw ../docs/board-round124-avx2-d.json.


Selected128/93fc9c9 unchanged selected source passes all five real gates, run-5e48e479beb7: T0.045148 s/M35340288/S424/K28.551323/72.781312. This lower same-source repeat stays separate from historical best and is not a new algorithm change. Raw ../docs/board-round128-offset-c.json.


Documentation-only head130/83a5f9c, run-a0d9f4fa93c6, passes every real gate with identical selected128 runtime inputs: T0.056743 s/M34115584/S424/K25.647959/70.45264. Lower same-source repeat, not a new algorithm regression; best records remain separate. Raw ../docs/board-round130-evidence-head.json.


Round133/16bedd2 unchanged selected source passes all five real gates, run-c1f07fdd811b: T0.048175 s/M35315712/S424/K27.643629/72.079753. Same-source repeat; do not label the delta a new algorithm improvement. Raw ../docs/board-round133-cooperative-c.json.


Restored selected135/2b3834d, run-b611fb45a28d, passes every real gate with exact selected128 runtime bytes: T0.045414 s/M35229696/S424/K28.485435/72.731143. Lower same-source confirmation, not another algorithm change. Current regular-image1323 cases, additional selected-C228 every-worker/24 normal errors, fresh combined public/defaults and all27 inputs match round135-final-source-match.json. Raw ../docs/board-round135-selected-confirmation.json.


Evidence-head137/715dcc6, run-ef33912695a8, passes all five real gates on identical selected128 runtime: T0.049508s/M35635200/S424/K27.219866/71.744299 points. C has a slightly higher same-source best67.916082/K22.820315; that is variation, not another algorithm improvement. Raw ../docs/board-round137-evidence-head.json.


## Grammar-based method length dispatch

139 replaces the ignored method's byte-by-byte space scan with its exact3..7-byte length from the first two method bytes. The frozen grammar lists all seven methods; every input row still supplies its actual method bytes. A32-byte lower bound makes both dispatch bytes in-range, and the computed delimiter is bounds/space checked. Endpoint/record/escape/quantile/output logic, exact4096 cache and generic/sample PGO are unchanged. This uses no endpoint catalogue, seed recognition or ordering bound.

13811 rotating full-public hashes: retained0.040810s/RSS264617984, skip-three0.040207/264601600 paired0.984124, method-length0.039733/264503296 paired0.967400. Only method-length gets broader139 validation. Fresh1637/1657 strict ASAN/UBSAN,1663 TSAN, every method×72hour×status×1..125-byte endpoint×escape combination ordered/shuffled, full1/6/12 and compact-ID4095 references pass. New pinned offline GCC production image passes96 reference replays and actual defaults;96 extra GCC ASAN/UBSAN integrations also pass. All unchanged primitive/cache/publication header bytes retain selected75 proof. Exact inputs/images in round139-candidate-source-match.json. Native3.26% paired hypothesis is not an Intel gain; retain only on actual K>28.740275/72.924546.


139/184778c run-b010640c4e1d passes all five gates: T0.044837s/M34922496/S432/K28.637988/72.847125 points. Method dispatch fails best28.740275/72.924546; restore main.cpp/README to715dcc6. Raw ../docs/board-round139-method-reserve.json.


## Mapped records with the accepted exact endpoint cache

145 retests our own event-written62 mapped allocator on the materially newer75 exact4096 front cache/canonical-view layout, keeping original generic GCC/sample104729+130363 training. The older62 interner lacked that cache and64 additionally changed scalar/native flags.145 deliberately excludes failed139 method dispatch. Only record vectors change allocator; exact four-byte tags, wide escapes, counts/scatter/selection and lifetimes are unchanged. Completed hour owners unmap fully consumed record buffers.

14411 rotating full-public hashes: retained0.041378s/RSS264568832; mapped-cache0.041055/259735552, paired0.980571. Method-only139 paired0.948855 and mapped-method0.953124 remain different source combinations; mapped-method is unvalidated beyond this screen. Native saving4.83MB and paired1.94% timing are hypotheses, not target/cgroup gains. Fresh1697/1699 ASAN/UBSAN,1709 TSAN, public1/6/12, every method/hour/status/escape/ID4095 reference pass. Fresh native/GCC strict allocator models verify exact values, growth/alignment/overflow, direct OS release and cross-thread destruction; native TSAN also passes. Header matches62; current combined integration proof is separately fresh. Production96 exact reference replays,96 extra GCC ASAN/UBSAN integrations and actual defaults pass. Every28 source/image input is recorded in round145-candidate-source-match.json. Keep only on actual K>28.740275/72.924546.

The initial144 timing-command review rejected historical reuse as not demonstrably fresh. Read-only fresh-repository root and allocator-first-add timestamps plus actual62 all-gates evidence established both occurred during this event. The exact same command was then accepted with that evidence; no alternate execution route was used. Source/event evidence is in round144-event-provenance.json and is not an organizer eligibility certificate.


145/348257e run-1fc76115f2d9 passes every real gate: T0.046329s/M27340800/S457/K29.337848/73.371413 points. Keep mapped/cache A: K28.740275→29.337848, points72.924546→73.371413. Charged memory35,426,304→27,340,800B falls22.82%; time0.044513→0.046329s is4.08% slower and source424→457 grows. This is a measured total-score tradeoff, not a runtime-speed claim or precise causal estimate from one run. All28 inputs match round145-final-source-match.json. Raw ../docs/board-round145-mapped-cache.json.


Evidence147/69322d0 run-ed5a0130bc00 passes all real gates on identical selected145 inputs: T0.057393s/M25169920/S457/K26.79854/71.405557 points. C67.958752/K22.865201 is a slightly higher same-source best; A/D lower repeats remain separate. No new algorithm gain is claimed. Raw ../docs/board-round147-evidence-head.json.


151/9e5d342 run-eab015fc2b17 passes every real gate: T0.049201s/M26775552/S457/K28.587904/72.809116 points. Unchanged-source lower repeat; historical best remains separate. Raw ../docs/board-round151-spsc-windows.json.


155/4191767 run-0afa6a51692a passes all five real gates: T0.051638s/M26624000/S457/K27.93686/72.30888 points. Unchanged mapped/cache A lower repeat; best73.371413 remains separate. Raw ../docs/board-round155-pooled-private.json.


157/34293c2 run-9f25c3c6faac passes all five real gates after exact selected145 restoration: T0.057580s/M25456640/S457/K26.694446/71.321046 points. Lower unchanged-source repeat; historical best 73.371413 stays separate. All28 inputs and complete file sets match current best-track sources; fresh157 combined public/defaults and original C48 pressure replays pass. Rejected151/155 code is absent. Raw ../docs/board-round157-selected-confirmation.json and round157-final-source-match.json.


159/0882828 run-0bb06676148a passes all five real gates on identical selected145 source: T0.052376s/M25358336/S457/K28.010873/72.366333 points. Lower same-source repeat; no new algorithm gain. Raw ../docs/board-round159-evidence-head.json.


## Ordered completion with directly mapped output and a bounded prefix decoder

163 retains all12 existing aggregation workers. A worker finishes exactly one hour, then publishes its Output under a mutex. The publisher flushes every consecutive completed hour in byte order and swaps its mapped character string empty. Empty hours also publish. No worker waits for a missing hour, and no extra/dedicated writer thread is created. Mutex unlock/lock publishes completed payload; stream access is serialized, and final close happens only after joined workers. Exceptions release the mutex and parallel() joins all workers before propagating; no output waiter can be stranded. This is tested reasoning, not a formal verifier certificate. Frozen input disorder semantics, exact grouping/quantiles/ID4095/latency escapes remain unchanged.

Output bytes now use the same source-identical event-written145 mapped allocator instantiated for char; new char/string models test growth, embedded NUL/terminator, direct OS release and cross-thread destruction on libc++ and libstdc++. Earlier16's old-layout mutex and45/101's extra/dedicated writers did not combine this exact12-worker record/output mapping.162 isolates ordinary mutex, mapped mutex, combined-prefix variants. Peak native RSS stays effectively flat; do not claim a measured memory saving.

The prefix decoder validates a bounded8-byte word with XOR/high-nibble and digit-overflow masks, counts only leading digits, zero-pads them by a defined0..56-bit shift, reduces exact decimal pairs and keeps a scalar tail. count0 avoids a64-bit shift. This differs from own event-written9's repeated subtraction/powers loop on an older D layout; no outside implementation is imported. New scalar/from_chars/all-byte/arbitrary-suffix/protected-page models pass strict native/GCC checks, including fulluint64 cases; production still checks fulluint32 and10-digit latency bounds.

Frozen16311 paired full-public hash trials: retained0.041741292s/RSS259522560, candidate0.039266000/259489792, paired0.930810731 (6.92% local hypothesis). No Intel/cgroup gain is claimed. Fresh1783/1787 strict ASAN/UBSAN,1789 TSAN, public1/6/12, every method/hour/status/endpoint/escape/ID4095, all1..12 lagging-first-hour/empty-prefix/shuffled-output references and normal open errors pass. Exact OrderedOutput native ASAN/UBSAN/TSAN and pinned GCC models pass. New A image has51 regular reference replays, actual native/Linux defaults and3 exact-production/dev/full errors at1/6/12. Combined GCC strict production A/C123 integrations+3 deferred sink errors pass. The initial GCC wrapper checked cat-replayed messages in the wrong output channel; corrected and reran the full matrix, with no runtime fix. All29 candidate inputs/images are bound in round163-candidate-source-match.json. Keep only if actual A K exceeds29.337848/73.371413; otherwise restore complete A inputs/README/Makefile to0882828 and original image0ee2c256....


163/d0bf708 run-271fd6ddf3b9 passes all five real gates: T0.045650s/M20787200/S497/K30.829845/74.448567 points. KEEP combined ordered mapped-output/prefix8 A: points73.371413→74.448567, K29.337848→30.829845. Charged memory27,340,800→20,787,200B drops23.97%, time0.046329→0.045650s is1.47% lower, and S457→497 grows8.75%. This measures the combined design, not individual component effects or a precise causal timing estimate. Raw ../docs/board-round163-ordered-high.json.


165/72b040a run-62e2cd1dd82a passes all five real selected-combination gates: T0.044266s/M20955136/S497/K31.257749/74.747885 points. Higher repeat of exactly the winning163 A source: extra74.448567→74.747885 is variation, not another algorithm. First changed-source gain remains73.371413→74.448567. Every29 inputs/file set and local image matches selected/best sources in round165-final-source-match.json. Fresh Make/public/defaults and restored-C141 new-reference replays pass. Raw ../docs/board-round165-selected-confirmation.json.


167/b693b45 run-609a8e322aca passes all five real gates on unchanged selected165 inputs: T0.044835s/M21049344/S497/K31.030919/74.589732 points. C68.028087/K22.938327 is a slightly higher same-source best; A/D are lower repeats. No new algorithm gain. Raw ../docs/board-round167-evidence-head.json.


168 new compact canonical ownership keeps all retained163 output/prefix/cache logic but copies specified<=125-byte keys before release publication into fixed125-byte/ID slots or a packed atomic byte arena; longer model-only keys borrow as before. Eleven rotating public hashes all match. Fixed/packed paired0.987245/0.989759 versus retained0.038641208s, with flat RSS. The tiny local difference does not pay for added source/memory/new ownership proof. Reject before broader collision/lifetime/sanitizer/GCC/image/actual promotion. Exact patches/limits in round168-prototype-index.json. No such ownership code enters173; selected165 A stays byte-identical.


173/7e77576 run-c2db1706a5b4 passes all five real gates: T0.043747s/M21037056/S497/K31.418092/74.858990 points. Unchanged selected165 A higher best74.858990/K31.418092 is repeat variation, not a new algorithm. Raw ../docs/board-round173-adjacency-pages.json.


175/e8a5109 run-7fb1c0ca32f8 passes all five real restoration gates: T0.042786s/M20979712/S497/K31.786315/75.112009 points. Higher unchanged selected165 source best75.112009/K31.786315 is variation, not another algorithm gain. Every29 input/file set matches current selected and best-track sources; fresh Make/public/defaults and original D996 new-reference cases pass. Raw ../docs/board-round175-selected-confirmation.json and round175-final-source-match.json.


177/5bf3ee3 run-bd218b3d1b82 passes all five real gates, unchanged selected175 runtime: T0.048126s/M21147648/S497/K29.923242/73.800432 points. Lower same-source variation; best retained separately. Raw ../docs/board-round177-evidence-head.json.


## Full-scale independent training on the ordered-output runtime

178 changes only the first build-time PGO workload from104729/sample to1000003/full. Second130363/sample, generic GCC15 flags and every C++/header byte are unchanged selected175/A163. Published seed1 is never trained; only the executable enters the final image. This revisits95's losing full-PGO experiment on a materially newer output/prefix layout. Native compilation is identical, so no native speed screen is claimed; emulated Linux checks establish correctness, not Intel timing.

Pinned offline allowlisted A build/public1/6/12 passes, followed by81 exact-image reference invocations: new strict ASAN/UBSAN1913/1931+full1951, TSAN1973, adversarial/method/hour/ID4095/latency escapes and ordered/lag/empty-hour fixtures. Fresh pinned GCC strict production54 valid+3 deferred sink errors pass; new PGO image3 sink errors at1/6/12 and actual native/Linux defaults also pass. Original exact OrderedOutput/prefix/cache/mapped-char model/race proofs remain bound by unchanged bytes. All29 inputs/full file sets and explicit new A + original C/D image identities are recorded in round178-candidate-source-match.json. Keep only if actual A total K improves31.786315/75.112009; otherwise restore Dockerfile/README exactly5bf3ee3 and imagee0eb6eee..., retaining honest candidate records. No algorithm or score improvement is claimed before the real run.


178/42c50ce run-004bfb2aafff all real gates pass: T0.042474s/M20746240/S497/K31.974332/75.240074 points. Changed first full-PGO build observed0.59% higher K versus prior31.786315/75.112009. Provisionally retain pending repeat; within historical variation, no precise causal or meaningful algorithm gain claimed. Raw ../docs/board-round178-full-pgo.json.


181/95c75c7 run-e45f04177283 all real gates pass: T0.044236s/M20955136/S497/K31.268346/74.755246 points. A178 same-build repeat is lower:31.268346 vs first31.974332; do not infer a causal PGO improvement. Provisionally retained only through the next independent C trial, then decide with full record set. Raw ../docs/board-round181-inline-field.json.


184/2a228b4 run-8dbc52563984 all real gates pass: T0.042414s/M21045248/S497/K31.905497/75.193276 points. Same full-PGO build31.905497 is0.375% above previous original17531.786315, below first17831.974332. Two of three changed-build observations exceed prior best, one is lower. Retain this modest measured build choice without a precise causal gain claim; later higher repeats are variation. Raw ../docs/board-round184-inline-parsers.json.


187/d6cea74 run-d3e26c39a872 all five real gates pass: T0.043080s/M21213184/S497/K31.607629/74.989596 points. Unchanged178 build lower repeat;75.240074/K31.974332 stays best. Mixed repeats limit causality. All29 inputs/full file sets match current selected and best-track sources, round187-final-source-match.json; fresh original-C405 references/30 errors and combined public/defaults pass. Raw ../docs/board-round187-selected-confirmation.json.


189/ceb78f8 run-9c865e71a863 passes all five real gates on unchanged selected187 runtime: T0.043933s/M20951040/S497/K31.377215/74.830719 points. Lower same-source variation; C0.061886s here versus1870.098959s is not a new algorithm gain or causal explanation. Raw ../docs/board-round189-evidence-head.json.


190/1cd2a7b run-f7a75967a6e6 all real gates pass: T0.043922s/M21118976/S497/K31.331076/74.798766 points. Lower unchanged selected187 source variation; best separate. Raw ../docs/board-round190-avx2-quote.json.


191 shared-prefix radix multi-selection for large groups512/1024/4096 is rejected before promotion. Each byte pass refines exact nearest-rank offsets, sharing identical prefixes; all values including fulluint32 are read. Public hashes pass, but paired1.003608/0.994278/0.999865 is flat and cannot justify added helper/source. No independent full-sort/rank/prefix/overflow/guard/strict/GCC/image/default/actual proof is claimed for those prototypes; original sort/nth_element stays. Exact patches/index/report preserve scope.

194 changes only both GCC PGO passes to-march=native, retaining full1000003/sample130363 and every C++/header. Losing111 used pre163 output/prefix and sample-only training; current163 bounded prefix8/ordered mapped output and178 full training materially alter compiler context, so this is not a blind unchanged repeat. Defined count-zero/rotate operations may compile differently; no ARM/emulated speed claim. New2237/2243 strict ASAN/UBSAN/full2221 and2249 TSAN pass. Fresh pinned GCC-native prefix/output all-byte/from_chars/guard/ordered/mapped-lifetime models and54 production strict+3 sinks pass. New exact ISA/PGO image81 references+3 sinks, public1/6/12 and composite195 actual defaults pass. All30 composite source/context/images are bound. Keep only if actual A K>31.974332/75.240074; otherwise restore Dockerfile/README exactlyceb78f8 and imageb57c3ff9..., preserving independent C choice. Official native build routing is used; no host/harness feature or identity override.


195/10e3ade run-bd204a738692 all five real gates pass: T0.043456s/M21204992/S497/K31.473022/74.896922 points. Reject native ISA on newer context:31.473022 loses31.974332; restore complete Docker/README toceb78f8 and original full-PGO B57 image. No target improvement claimed. Raw ../docs/board-round195-native-a-crc-c.json.


197/8003961 run-291f7705fa6e all five real gates pass: T0.043935s/M21061632/S497/K31.343480/74.807361 points. Original generic/full-PGO A restored; lower same-source repeat, best31.974332 remains. All29 source/build/metadata inputs/full file sets match selected and current best-track sources. Fresh original A81/C501+30 errors, combined public/defaults pass; round197-final-source-match.json. Raw ../docs/board-round197-selected-confirmation.json.


199/d4027c9 run-df1f3d713f80 all five real gates pass on unchanged selected197 runtime: T0.042801s/M21176320/S497/K31.721512/75.067694 points. Lower same-source repeat, historical best kept separately. Raw ../docs/board-round199-evidence-head.json.


201 bounded2/4/8 adjacent front-cache probes preserve exact full-key comparison and global fallback. All full-public hashes pass in11 rotating native runs, but paired1.005356/0.992900/0.994820 is flat against added comparisons/source. Reject before new collision/eviction/wrap/guard/canonical-publication/strict/race/GCC/image/actual proof. Original4096 direct cache remains. Primary associativity paper2304.04954 motivates conflict analysis only; its random-hash/LRU theorem does not apply to this sampled-hash/home-eviction design. No imported implementation.


204/0112b33 run-0e889b96ee08 all five real gates pass: T0.045522s/M20799488/S497/K30.869510/74.476487 points. Unchanged selected197 source lower repeat; historical best separate. Raw ../docs/board-round204-shifted-offset-home.json.


206/e3140e0 run-0a6037d481be all five real restoration gates pass: T0.042878s/M21123072/S497/K31.708979/75.059113 points. Original selected197/187 runtime restored; lower unchanged repeat, historical best separate. All29 inputs/full file sets match selected and current best-track sources, round206-final-source-match.json. Fresh original C501 independent204 references/full2281/all workers+30 errors and combined Make/public/defaults pass. Raw ../docs/board-round206-selected-confirmation.json.


208/8acb692 run-0ff50ccc1a86 all five real gates pass on unchanged selected206 source: T0.044548s/M21176320/S497/K31.093294/74.633337 points. Lower repeat variation; historical best separate. Raw ../docs/board-round208-evidence-head.json.


211/212 remove only unused nonvirtual Output.save; actual A main/OrderedOutput never calls it. Every data member and used function/algorithm/header/build/PGO statement remains exact206. No minification, source hiding or exemption change. Both isolated211 and exact212 native Make binaries are byte-identical to selected206; this is not assumed for Intel/GCC. Fresh current-output mapped-char/ordered sink models pass native ASAN/UBSAN/TSAN and generic pinned GCC, with unchanged prefix all-byte/guard models freshly re-executed on GCC. Generic strict production54 reference runs+3 deferred sink errors, exact new PGO image81 references+3 sink errors, full-public1/6/12/combined Make and actual defaults pass. Independently rebuilt local GCC executable is NOT byte-identical to B57; do not infer runtime identity or a speed gain from native proof. Thus the predeclared source-only identical-GCC retention branch is unavailable: retain A only if real K>31.974332/75.240074, else restore complete io.hpp and B57 image. All29 inputs/images in round212-candidate-source-match.json; real S/K pending. No new runtime protocol.


212/e65b2b0 run-887f6d41948b all five real gates pass: T0.043655s/M20877312/S490/K31.566256/74.961153 points. SourceS490 versus497 is lower, but K31.566256 loses31.974332 and local GCC ELF differs; predeclared source-only branch is unavailable. Restore complete io.hpp/B57. No causal slowdown or target gain claimed. Raw ../docs/board-round212-unused-a-c6.json.


213/4e41c96 run-c0d1e219b0d9 all five real gates pass: T0.044261s/M20692992/S497/K31.338317/74.803783 points. Unchanged original selected206 source lower repeat; best separate. Raw ../docs/board-round213-c8.json.


214 isolated mapped-record vector growth1.5/4/8 retains every value/order/escape and allocator flag; only standard reserve-on-full policy changes, with existing file-size/64-bit arithmetic guards.11 rotating public hashes pass but paired1.037363/0.984085/1.013302 with essentially flat RSS259.4–259.7MB does not establish a worthwhile total-K case. Grow8 global0.039642 versus0.040247 is misleading against paired1.013302. Unused virtual capacity is not resident memory; no accounting APIs or mmap flags are changed. Reject before new capacity-boundary/overflow/allocator-lifetime/strict/race/GCC/image/default/actual proof. Original vector policy remains; exact patches/index/report preserve screening scope.


217/3f3cff4 run-fa996bb6e176 all five real restoration gates pass: T0.048738s/M21037056/S497/K29.765974/73.686005 points. Full original selected206/187 runtime restored after unused-A method removal and C6/C8 default-worker losses. All29 root/frozen/scored/best inputs and complete file sets match, round217-final-source-match.json. Fresh combined public1/6/12 and native/Linux actual default12 pass; exact206 native executables reused, immutable A81/C501/D996 image/strict/race references retained by source/binary identity, no fresh whole-bank217 replay or compilation claimed. Best/latest and variation separate. Raw ../docs/board-round217-selected-confirmation.json.


220/0e5f1aa unchanged selected217 runtime, run-e3c66b946472, all five actual gates pass: T0.050295s/M21311488/S497/K29.225757/73.288289 points. Lower unchanged repeats, not new gains; bests separate. Raw ../docs/board-round220-evidence-head.json.


221/3611979 run-7f00e22060b9 all five actual gates pass: T0.044034s/M20910080/S497/K31.353478/74.814286 points. C matched6 build/runtime loses K20.682353 versus23.033578; fully restore original C Docker/README. A/D unchanged lower repeats. New strict177/image510/default59+errors proofs remain historical to candidate. No target phase/cause claim; raw ../docs/board-round221-matched-six.json and round221-scored-source-match.json.


222 unchanged current217/206 binary total-worker screen6/8/10 versus12: paired elapsed{'12': 1.0, '6': 1.1466410711947166, '8': 1.0429915566153687, '10': 0.9909907008601615}. All full-public input/output hashes pass,11 rotating sequential trials after warmup. Six/eight slower; ten effectively flat. Keep12 before any new default/GCC/PGO/image/actual proof; Mac RSS/time are not cgroup/Intel K. Raw ../docs/round222-a-workers-screen.json.


224/bdbdcb5 run-411623e51471 all five actual gates pass: T0.045155s/M20852736/S497/K30.978858/74.553270 points. C matched8 build/runtime loses18.287870 versus23.033578; fully restore original C Docker/README/C263 image. A/D unchanged lower repeats. Source-identical221 strict/race/GCC stays relevant to original C++,224 production510/default59+errors proof is historical to rejected PGO/config. No target phase/cause claim. Raw ../docs/board-round224-matched-eight.json.


227 isolated current-input last timestamp-key reuse copies8 safe bytes at offsets5..12 after original28-byte guard, recomputes exact month/day/hour for every changed key and retains range check. Full-public11 alternating hashes pass, paired1.009866/RSS flat, reject before new shuffled-key/truncation/guard/strict/race/GCC/image/actual proof. No root parser change or precomputed/cached output/seed catalogue. Raw ../docs/round227-hour-key-screen.json and exact prototype patch.


225/2d71679 run-507737200352 all five actual restoration gates pass: T0.042640s/M20922368/S497/K31.858122/75.161009 points. Full original217/187 runtime restored after221/224 matched6/8 PGO losses. All29 inputs/file sets/Make match scored/current best sources, round225-final-source-match.json. Fresh original C510+30 image references, actual no-argument/no-worker-override59+4 and native/Linux default12/public checks pass. Source-identical221 strict/race/GCC177+30 retained; original A81/D996 immutable proofs remain, no new A/D whole-bank replay. Native executables/images reused, no225 compilation/training claimed. Best/latest/variation separate. Raw ../docs/board-round225-selected-confirmation.json.


229/c47cf0b run-5f8e0dfd6c53 all five actual gates pass, unchanged225 runtime: T0.044326s/M21196800/S497/K31.165034/74.683380 points. Lower repeats, not new gains; bests separate. Raw ../docs/board-round229-evidence-head.json.


230/f7b2913 run-431a24a03674 all five real gates pass: T0.042573s/M21266432/S497/K31.779341/75.107244 points. C amount prefix loses21.858223 versus23.033578; source699 versus672 grows, native3.56% screen did not produce supported target totalK gain. Fully restore original C main/Docker/README/Make and remove C decimal.hpp. A/D unchanged lower repeats. Fresh numeric/guard/strict/race/GCC216+50/image630+50/default72+9/source proof stays historical to230, not original scalar model proof. No target phase/cause claim. Raw ../docs/board-round230-amount-prefix.json.


231 isolated bounded std::memchr for method delimiter loses paired1.014461 despite slightly lower global median/RSS flat; reject before broad new proof or board run.233 unscored native joined-phase diagnostics have full output/control hashes; parse23.112ms, aggregate/selection/publication9.401ms and finish7.656ms are instrumented local medians, not Intel/causal timings.235 read-only public/full2221/full1951 profiles find1065/1063/1057 contiguous same-hour spans across3.1M records: raw index8520/8504/8456B versus12.4MB compact-record payload, estimated4KiB mapped index348160B. Not charged peak/time/K; motivates isolated236 indexed-hour memory layout before any generic/strict/race/image/actual claim. Runtime A unchanged.


234/75348f2 run-52c4a4381040 all five real restoration gates pass: T0.052512s/M20901888/S497/K28.713396/72.904228 points. Complete original225/187 runtime restored after230 amount-prefix C loss; all29 source/file sets/Make/image identities match, ../docs/round234-final-source-match.json. Fresh original C630+50 production, actual no-argument/no-thread-override72+9/default12/public checks; original221 strict/race monetary rerun. Original221 GCC177+30 and127 primitive proofs retained, rejected230 GCC/helper proof not relabeled. Native/image identities reused without compile/training; A81/D996 unchanged proofs retained. Lower unchanged repeats are variation, not new algorithm regressions or gains. Raw ../docs/board-round234-selected-confirmation.json.


240/2d0a224 run-837a0698a4ce all five real evidence-head gates pass: T0.044073s/M21200896/S497/K31.253149/74.744689 points. Runtime byte-identical to restored234/225/187; lower unchanged repeats are variation, no algorithm change or new gain. Original source/image/best identity remains in round234-final-source-match.json.241 new source is still isolated and unpushed, pending C/D Linux/PGO/default proof. Raw ../docs/board-round240-evidence-head.json.


Candidate241 local selection: Only original-layout bounded in-flight hour-output scheduling changes, new ordinary charged hour_work.hpp and exact flushed-prefix count. Empty hours/cancel/retirement/IO stay live under all1..12 model schedules. Native strict/race/fresh full2441/independent/ID4095/latency escapes/order; GCC57 content/thread references+3 sinks, exact new generic full/sample PGO image72 references/24 defaults+3 sinks/native default all pass. All30 source/build/metadata inputs/Make/complete file sets/local images bound in ../docs/round241-candidate-source-match.json; all-track actual Make/public1/6/12/native defaults pass. Official full1000003/sample130363 PGO only, never publicseed1. Native small/noisy timing hypotheses are not target gains. Real total K must beat historical best; actual result pending, restore losers. Original passing controls remain available.


241/30448ff run-be12f748f8b9 all five actual gates pass: T0.045050s/M21123072/S540/K30.552483/74.252326 points. Reject: total K fails historical best 31.974332. Restore complete original225/187 source; A hour_work.hpp and Make/Docker dependency removed; C count-only/format and D prune removed. All30 candidate source/Git/local-image inputs bind in ../docs/round241-scored-source-match.json; new strict/race/GCC/image/default proofs remain historical to rejected code. No causal speed/holdout/eligibility inference. Raw ../docs/board-round241-window-count-prune.json.


247/b25a92f run-87a67a335f6f all five real restoration gates pass: T0.042692s/M21028864/S497/K31.806401/75.125726 points. Complete original29 runtime/build/metadata inputs and file sets/Make restored after241 losses; original A header removed. Exact best/Git/frozen/local-image identities ../docs/round247-final-source-match.json. Fresh native/image public1/6/12/actual defaults pass; original A81/C630+50/default72+9/D996 and source-bound strict/race/GCC/models retained without relabeling rejected241 proofs. Immutable images/native225 binaries reused, no247 compilation/training or whole-bank replay. Lower unchanged repeats are variation. Raw ../docs/board-round247-selected-confirmation.json.


249/5f75ecf run-a2cb1a7298dd all five actual gates pass: T0.044999s/M21176320/S497/K30.937086/74.523970 points. C7readers/5owners loses totalK21.142704 versus23.033578 and is fully restored to original scalar C8readers/4owners; A/D unchanged repeats are variation. All29 exact candidate Git/frozen/local-image inputs bind ../docs/round249-scored-source-match.json. Native role-speed hypotheses did not establish a target improvement. C7 strict/race/primitive/GCC231+25/image645+50/default75+9 source proofs stay historical to rejected code; original C263 proof not relabeled. Raw ../docs/board-round249-c-seven-readers.json.


253/ccf938b run-2d64eeeea0a6 all five real gates pass: T0.063888s/M21159936/S497/K25.967995/70.721921 points. Full original29 inputs/file sets/Make match saved best sources after rejected C249. Exact actual/Git/best/local-image proof ../docs/round253-final-source-match.json. C-only fresh native/image public1/6/12 and native/actual-image defaults pass; immutable original image/native binary reused, no new compiler/training or whole-bank replay. A/D unchanged earlier source-bound proofs retained; no rejected candidate proof substitution. Lower unchanged repeats are variation, not an established causal regression or gain. Raw ../docs/board-round253-selected-confirmation.json.


Candidate255 local proof, official trial pending. New isolated254 replaces old4096 LocalEndpoints with private2048 prefix-indexed learned-length/ID parsing hints, bounded full equality+actual delimiter and unchanged global interner. Every row/status/latency/duplicate remains exact. New native+GCC strict model385754checks each, nativeTSAN, fresh untrained/main/alias/ID4095/wide/order tests, GCC60refs+15inputerrors+3sinks, exact newPGO image75refs/25actualdefaults+15inputerrors+3sinks pass. Native25paired ratios public.971774/fresh1951 .966431/2221 .977586 are not Intel/K proof. Source-growth estimate uses AppleLLVM21, not official S. Exact combined29 source/Make/local-image binding ../docs/round255-candidate-source-match.json. Original passing253 remains the rollback source. Retain only supported real total-K improvements; no number-one, holdout or eligibility guarantee.


255/94f9df9 run-6ba280806e01 all five real gatesPASS: T0.050070s/M20852736/S491/K29.472757/73.471038 points. Reject new span2048: K29.472757 below31.974332; restore complete original A source. OfficialS491 confirms source reduction, but totalK loses. Exact29 actual/Git/frozen/local-image proof ../docs/round255-scored-source-match.json. New span/bucket model/GCC/PGO proofs remain historical to rejected code, never substituted for original. Native hypotheses did not establish a supported target gain; no precise causal or holdout claim. Raw ../docs/board-round255-spans-bucket-epochs.json.


256/da6f728 run-5c14540e890f all five real restoration gatesPASS: T0.043751s/M20836352/S497/K31.476947/74.899630 points. Full original29/Make restored after rejected255A/D, exact actual/Git/best/frozen/local-image proof ../docs/round256-final-source-match.json. Fresh A/D public/default replays use byte-identical original binaries/images; C unchanged passing component and original broad/source-specific strict/race/GCC/model proof retained, no new compiler/training/whole-bank replay. Lower unchanged repeats are variation. Raw ../docs/board-round256-selected-confirmation.json.


257/8b0f263 run-ff8624471042 all five real gatesPASS: T0.048066s/M21319680/S497/K29.893434/73.778790 points. Unchanged original source; lower repeat is variation, no algorithm regression/gain claimed. Exact29 actual/Git/frozen/local-image identity ../docs/round257-scored-source-match.json. New allocator/model/Linux proofs remain historical to rejected257, not relabeled as original. Raw ../docs/board-round257-aligned-labels.json.


258/5871ce0 run-14201f55515d original source allfive real gatesPASS: T0.046470s/M21217280/S497/K30.431731/74.166333 points. Exact original best-source/Git/frozen/local-image proof ../docs/round270-final-source-match.json; lower identical-source repeats are variation, including C slow outlier, not a new source regression or gain. No new compiler/training/broad-bank replay or rejected aligned proof substitution. Raw ../docs/board-round270-selected-confirmation.json.


262/5198eaf run-ea2dcfb169c2 all five real gatesPASS: T0.047618s/M21192704/S497/K30.069630/73.906404 points. Unchanged original source repeat; lower result is variation, not a new source regression or gain. Exact29 actual/Git/frozen/image proof ../docs/round262-scored-source-match.json. New degree-two models/GCC/PGO/image proofs remain historical to rejected code; never relabeled as original. Raw ../docs/board-round262-degree2-bypass.json.


263/737b80f run-8131a6fabe83 original allfive real gatesPASS: T0.047414s/M20885504/S497/K30.222379/74.016432 points. Exact original best-source/Git/frozen/local-image proof ../docs/round263-final-source-match.json. Lower identical-source repeats are variation; no new gain or rejected degree-two proof substitution. Fresh D-only original public/default checks used immutable binaries/images, no compilation/training/broad replay. Raw ../docs/board-round263-selected-confirmation.json.


264 two/four independent newline-aligned cursors per existing worker were freshly implemented in isolated own source, retaining12 total workers/exact cache/latency escapes and minimum first-line positions. Existing263 native control reused; each prototype compiled once under shared lock. Published1/6/12 plus13 rotating triples over public/full1951/full2221 match every exact reference and before-after input/source/ELF hash. Stream2 paired ratios.981771/.984287/.982195; stream4 .985507/.984106/.984301, essentially flat native RSS. Reject weak time/source case BEFORE broad partition/strict/race/GCC/image/default/board promotion. No Intel total-K gain. docs/round264-a-stream-screen.json; immutable .build/round264/frozen.json. Conceptual inspiration from independent-state latency hiding in Kocberber/Falsafi/Grot AMAC (https://www.research.ed.ac.uk/en/publications/asynchronous-memory-access-chaining/); this simple row-level interleaving is not complete AMAC and uses no copied implementation.


266 freshly isolates parser-thread reuse for aggregation with a std::barrier setup completion and uncreated-participant drop/error propagation. Original263 control reused; candidate compiled once. Public1/6/12 and13 rotating pairs public/full1951/2221 match all reference/input/source/ELF hashes. Paired.983831/.983617/1.002145, native RSS flat/slightly higher. REJECT weak and inconsistent cost/benefit BEFORE new barrier/failure/join/publication/strict/race/GCC/image/default/board proof. Root parallel helper and two ordinary joined phases stay unchanged; no new protocol correctness or target gain claimed. docs/round266-a-phase-reuse-screen.json and immutable .build/round266 snapshots.


Candidate268 local proof complete, real trial pending. Only six-number suffix formatting changes: same signed std::to_chars conversions into128 stack bytes, one append instead of separate space/number appends. Full signed64 capacity bound6*(1+20)+1=127; every production value remains exact. Public/full1951/2221 native13-pair ratios.963848/.960364/.967707 with13/12/11 wins and mixed RSS are a modest hypothesis, not Intel/K proof. Actual extracted tail with only range expression replaced checks11722 independent Python signed-width/binary/decimal-boundary/random vectors at1/12 under native strict ASAN/UBSAN and TSAN; unchanged parser/cache/records/ordered-output primitives remain byte-bound. Fresh2767sample/2777full ASAN,2789sample TSAN and all method/hour/ID4095/escape/ordered-hole/lag/error suites pass. New pinned generic GCC strict model11722x1/12 and main69 reference invocations+3 deferred sink errors pass. Unique unchanged full1000003/sample130363 PGO image c0a2dbe305da73c80050cebe02b8f0693015f0ca9355fbfd7e644e649716a238 passes96 content/thread references+3 sink errors and23 actual noarg/nooverride defaults. No rejected stream/barrier/borrowed-key code selected. Keep only supported actual A K>31.974332/75.240074, else restore exact original A/main/README/image and confirm.


268/97e58d7 run-2b5bdcb94249 passes all five real gates: T0.042327s/M20840448/S502/K31.952782/75.225434, narrowly below best31.974332/75.240074. Time alone improves versus best0.042474s but memory/source offset it; no total gain. Raw ../docs/board-round268-buffered-suffix.json and scored-source proof preserve exact29 inputs.

269 completes that refactor by deleting only Output::number, now never called. All remaining executed bodies and Output data layout unchanged; no unrelated unused-code or formatter/exemption change. Fresh native actual main strict ASAN/UBSAN+TSAN18 public/untrained full2777/sample2789 references pass; existing26811722 native suffix model/unchanged primitive proof stays limited to exact identical executed bodies. Fresh269 exact-header GCC strict model11722 vectors at1/12 and main69refs+3 sink errors, unique unchanged PGO image96refs+3 sink errors and23 actual defaults pass. No old source-specific GCC/image report reused as current. Actual root Make/full-public/default/all29 source proof follows. Separate normally cooled real trial required to retain only K>31.974332; else restore complete original737 A main/io/README/image and confirm once.


269/17443e4 run-9f7c320f6d29 passes all five real gates: T0.042302s/M21114880/S497/K31.926607/75.207638, below best31.974332/75.240074. Removal of the now-unused scalar formatter restores S497, but observed memory/time/source combination still does not support a total gain. REJECT268+269 together, restore complete original737 A/main/io/README and B57 image. All fresh source-specific native/GCC/model/image/default proofs remain historical, not original proof. Original changed-back public1/6/12 and native/Linux defaults pass without compilation/training; exact all29 original identity restored. One cooled real270 rollback confirmation pending. Raw ../docs/board-round269-complete-suffix.json and exact scored-source binding retained.


270/4821139 original-source confirmation run-d2cafa1720c7 passes all five actual gates: T0.050079s/M20918272/S497/K29.398011/73.415898. Full original all29/Make/Git/source/image identity verified. Lower unchanged-source repeats remain variation; no target-phase explanation or new gain claimed. Raw ../docs/board-round270-selected-confirmation.json and exact ../docs/round270-final-source-match.json.


Original275/06d3742686e78a4bfa7c7ad85adc4df9e827c3d7 all five actual gatesPASS, run-e80b829be01b: T0.043878s/M20717568/S497/K31.467321/74.892988. Complete all29/Make/README/Git/best component/local-image identity in ../docs/round275-final-source-match.json. Entire rejected274 route/style change removed. Best remains unchanged; lower latest repeat is preserved as variation without a new causal timing claim. Raw ../docs/board-round275-selected-confirmation.json.


278 exact small-group median/top-two prototype is rejected at native screen. n<4 sort;4..31 median nth then upper-tail top1/top2 because nearest95/max agree through19 and nearest95 is second-max for20..31; larger groups unchanged. One compile, original263 control, full-public1/6/12 and13 rotating pairs public/full1951/full2221 all input/output/source/ELF hashes PASS. Ratios.990631/1.020653/.998557, wins9/4/7 are mixed/flat with source growth. No independent exhaustive sort/rank/duplicates/full32/guard/strict/race/GCC/image/default/actual proof or target gain claimed. Original selected source untouched. Exact ../docs/round278-a-small-order-statistics-screen.json and ../docs/prototype-patches/round278-a-small-order-statistics-main.cpp.patch.


283 complete bounded endpoint-cache comparisons cover first/last8 for8..16 bytes and first/last16 for17..32, with original empty/other-length semantics and unchanged full-key global fallback. Native public1/6/12 and13pairs public/1951/2221 all hashes pass; ratios.979208/.996504/.966026 with8/13wins each are modest. Fresh untrained full3001 official-generator/Python-oracle confirmation, existing binaries/no recompile or training, is only.990484 with8/13wins and nearly flat RSS. REJECT before new all-length/every-position/guard/cache-collision/strict/race/GCC/image/default/actual proof; source growth lacks a strong case. No official S/K or general correctness claimed, original selected untouched. Exact ../docs/round283-a-cache-equality-screen.json, fresh-confirmation.json and patch.


Original281/17965626c38f4318ed55e33c24c68bbe68bdc88c all five actual gatesPASS, run-623d051300f1: T0.042998s/M21250048/S497/K31.626769/75.002741. Complete original29/Make/README/file-set/Git/best-component/local-image identity ../docs/round281-final-source-match.json. C280 group4 rejected fully; original linear source restored. Best unchanged; latest lower repeats remain variation, no new gain/precise causal timing claim. Raw ../docs/board-round281-selected-confirmation.json.


Original287/de45eaaba7466025464ebc9eab0594e3ea75fe44 passes every actual A/C/D gate after complete D286 rollback. D286’s12.66% observed memory saving failed total K because time was43.001% higher than the old best; no cap6 remains. A run-1f7d6bf1c413 T.042078/M20922368/S497/K32.070167/75.305061 is a new historical best at unchanged source, recorded as repeat variation. C run-b345ca0ecf80 K22.562748/67.669600 and D run-a64b4b99ca33 K19.755206/64.784078 are lower unchanged-source repeats; historical C68.118071/D65.319494 remain. All29/root/Git/frozen/current-best/file-set/README/Make/local-image binding round287-final-source-match.json. Complete ordinary feed rank53/106, mean69.456001, leader ALL STAR84.029489. No #1 or final judging claim.

C288 read-only binding proves the proposed compile-time decode template exactly duplicates rejected native-only179 (paired.993777) at current header bytes. The stale unimplemented-caption is corrected; no duplicate compiler/benchmark/PGO/model/board work. D289 new bounded128-edge cross-node gather/prefetch, exact ordered relaxation and stale checks has full-public1/6/12 and13 rotating pairs over public/full1823/full2633 hashesPASS, native ratios.969577/.967703/.963944 (11wins each), nearly flat RSS. Newly generated independent full3109 Python-Dijkstra oracle confirmation is.976972 with12/13wins and modest RSS difference. These remain modest native hypotheses, not Intel/K/general-correctness proof. Exact rejected-old one-neighbor100 and two-query-context284 protocols are distinct. Original selected287 runtime never changed. Candidate290 is reserved for full new bounded-buffer/stale/split/growth/prefetch/Floyd/strict/race/GCC/PGO-image/default/Make proof before any integration/actual trial; none started yet. Full3109 test-wrapper failures/recovery are preserved honestly in round289-d-relax-gather-fresh-confirmation.json and tools/round289-screen; generator is reused and only the first unsaved oracle calculation repeated, no compiler/training duplication.


Original295/30d4105bd5655ba2862d181f76c600dc6237233c now passes all real A/C/D gates after complete C294 and D290 removal. No new best algorithm/K gain. A run-58eda28b9c6b K31.710564/75.060198, C run-85d75cd62814 K22.694385/67.795921, D run-05b47a45e4ec K19.864725/64.904128 are lower unchanged-source repeats. Best A75.305061/C68.118071/D65.319494 remain. All29/current/Git/frozen/current-best/file-set/README/Make/local-image proof round295-final-source-match.json; complete ordinary feed rank54/108, mean69.456001, leader another ello84.139659. Rank changed while best scores held as other teams advanced; no #1/judging/eligibility guarantee.

A296 fixed64KiB per-hour mapped record blocks preserve full32-bit rows/latency19-bit escapes and source semantics at published1/6/12/three-full output screening, but13-pair ratios.988240/.981162/.999653 and inconsistent RSS are too small/mixed for new container source/lifetime/iterator/allocator complexity. REJECT before broader empty/prefix/guard/move/swap/OOM/release/race/GCC/image/default/actual proof, no general correctness or charged-memory gain claim. Original mapped vectors already leave unused reserved capacity untouched; a smaller virtual capacity does not imply lower measured memory. New header exists only in ignored prototype and published patch, never selected. Three-byte-row compression was discarded before code because the published latency distribution would add wide side data. Primary C++20 default-initialization semantics were read, no code imported. Exact round296-a-record-blocks-screen.json/preflight and tools/round296-screen. No live job/watcher remains.

A297 checked input-relative endpoint-cache slots shrink16 to12 bytes and retain full sampled hash/length/byte equality plus exact shared fallback. Cached offsets use the current immutable input slice, with declared mapping/uint32 range checks before storage; no canonical pointer is truncated. Published1/6/12 and13 rotating pairs over public/full1951/full2221 pass full input/output/source/ELF hashes, but ratios1.020400/1.004449/1.010681 are slower with mixed RSS. REJECT before new foreign/null/range/long-key/guard/canonical/lifetime/collision/native-GCC strict/race/image/default/actual proof. No root runtime changed. Exact docs/round297-a-offset-cache-screen.json, preflight, patches and tools/round297-screen; wrapper's old A283 print caption is disclosed, all executed paths/hashes were297. Primary C++20 pointer/integer mapping semantics are implementation-defined, so no broad portability/correctness claim is inferred from native hashes.

A304 std::array4096 fixed stack cache versus original vector is native-only REJECT: public1/6/12/three-full13-pair input/output/source/control/candidate hashesPASS, paired.997446/1.018237/.982209 and mixed RSS. No broad stack/guard/strict/race/GCC/image/default/actual proof claimed. Other chat coordinated this isolated screen under the shared lock; no selected source changed. Exact docs/round304-a-fixed-cache-screen.json/preflight/patch/tools.
