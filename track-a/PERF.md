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
