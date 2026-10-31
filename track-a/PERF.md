# Track A optimization log

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
