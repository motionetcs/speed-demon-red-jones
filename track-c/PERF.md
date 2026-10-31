# Track C optimization log

This fresh implementation uses a mapped, quote-aware byte parser, a direct region lookup, and exact per-name country membership bits. First scored board run: **run-bbda54bf2316**.

The memory-layout hypothesis is that a few membership words per distinct name cost less than allocating a separate set node for every country/name combination. This is a structural design decision. No isolated before/after benchmark of a per-country set implementation was performed, so no measured speedup for that change is claimed.

`../docs/validation-sample.json` records exact comparisons for sample seeds 1 and 19. `../docs/validation-public-full.json` records repeated full-public native runs and the published output hash. Those are local macOS ARM process timings and process RSS, not the board's CPU timings or cgroup `memory.peak`.

The parser passes quoted newlines, escaped quotes, BOM boundaries, empty values, exact byte counts, untrimmed names, negative sub-unit amounts, and optional final terminators in the official worked/grammar tests. Sanitizer evidence is in `../docs/validation-sanitizers.json`. The next measured experiment should isolate name-table lookup or parsing throughput and use a real board run ID. No unperformed experiment or official score is invented here.

## First official live-board run

The organizer's full-public-seed-1 run passed check, build, correctness, timeout, and sandbox gates. This is one live-board run, not the final holdout/judging result.

| Field | Observed value |
| --- | --- |
| Run ID | `run-bbda54bf2316` |
| Commit | `788ae3b205928ca2bc3d60100703d5660123d0f0` |
| Finished UTC | 2026-10-31T03:57:23Z |
| Process wall time | 0.962631 s |
| Cgroup peak memory | 13,316,096 bytes |
| Measured source size S | 306 lines |
| Dependency weight D | 1 |
| K | 6.433258 |
| Live machine points | 40.421548 |

Source: [official board JSON](https://s3.amazonaws.com/raptors.dev/speeddemon.dev/2026/board/board.json); exact records are retained in `../docs/first-board-run.json`. The board time includes parsing, preprocessing, queries/aggregation, and output. Compare future changes on this same machine rather than interpreting differences from Apple ARM development timings as an optimization result.

## Parallel CSV and exact shared names

Hypothesis: a quote-parity partition permits independent CSV parsing, while atomic publication and exact per-name country membership avoid duplicate maps or large per-worker distinct sets. Worker-owned strings remain stable; release/acquire publication protects readers. Table saturation retries with a larger table.

Five alternating local full-data trials after warmup gave median serial/candidate times of 1.177628/0.771010 s at one worker, 1.122927/0.160815 s at six, and 1.155291/0.132393 s at twelve. These local figures select the twelve-worker board candidate; they are not official speedups. Full records: `../docs/opt-c-parallel-native.json`.

The candidate passes generated tiny/sample seeds, the full public hash at 1/6/12 workers, address/undefined-behavior and thread sanitizers, and offline restricted Linux x86-64 validation. Extra cases force concurrent name publication, quoted multiline partition seams, resizing beyond 114,688 distinct names, and more than 256 countries. Reports: `../docs/opt-c-parallel-*.json`. Real board results will be added after the exact candidate commit is scored.
