# Track A optimization log

All numbers here are local macOS ARM development evidence, including process launch, not official scores. Raw runs, hashes, and source fingerprints are in `../docs/experiments-local.json`. First scored board run: **run-c76f845b747a**.

| Experiment | Dataset | Baseline median | Candidate median | Decision | Board run ID |
| --- | --- | ---: | ---: | --- | --- |
| Exact selection for groups of at least 64 instead of sorting | sample, seed 1 | 0.04432 s | 0.04546 s | Reject; slower | Unavailable |
| Same independent-seed check | sample, seed 19 | 0.04379 s | 0.04924 s | Reject; slower | Unavailable |

Hypothesis: selecting only the required ranks would save comparisons in large groups. Each candidate was warmed once, then baseline/candidate runs alternated for seven measured runs apiece. Every run matched the official reference hash. The extra selection overhead did not pay on either sample, so the final code retains full sorting.

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
