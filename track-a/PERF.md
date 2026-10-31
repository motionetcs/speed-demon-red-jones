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
