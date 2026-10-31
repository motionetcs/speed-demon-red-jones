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

## Confirmed parallel board result and compact lookup candidate

`run-a82ca12db6e4` on `835148746ad0da7f69d93a9f72f80cb710f1b52a` passed every gate: T=0.124259 s, M=16,891,904 bytes, S=465, K=16.035293, points=60.253844. Runtime fell about 7.75x versus the original 0.962631 s; points rose from 40.421548. Record: `../docs/board-opt-c12-a6.json`.

The next hypothesis separates compact immutable lookup entries from mutable membership bits and replaces worker-owned strings with a shared append-only character arena. Numeric parsing consumes delimiters directly. Five alternating local full-data trials gave twelve-worker medians of 0.146529 s for the first parallel version versus 0.105221 s for the refinement; six-worker medians were 0.169984/0.120356 s. Every hash matched. These local gains are not official board improvements. Report: `../docs/opt-c-compact-native.json`.

The refinement passes tiny/adversarial cases, independent sample seeds 23/41, full public hashes at 1/6/12 workers, address/undefined-behavior and thread sanitizers, and offline GCC15 Linux full-data validation. Reports: `../docs/opt-c-compact-d-packed-*.json`. The next exact-commit board result is pending.

## Refined candidate: actual board record

`run-edc906c4b648` on `072ce9b9046484a76c7e98aebd1e998e0d440d17` passed every gate: T=0.106731 s, M=37,818,368 bytes, S=480, K=14.656236, machine points=58.301122. Record: `../docs/board-opt-refined-acd.json`.

This is faster but scores lower than the first parallel version (60.253844 points), because measured peak memory rose to 37.8 MB. The compact-arena refinement is not accepted as an overall scoring improvement. A separately tested native-compilation comparison follows; a membership-read fast path is being checked independently.

Next experiment: `-march=native` in the Docker build. The official harness explicitly builds native-targeted submissions on the scoring CPU. Offline emulated Linux full-data and tiny hashes pass for all three tracks; reports `opt-native-cpu-containers-{public,tiny}.json`. Emulated timings are not performance evidence for Intel. Source algorithms are unchanged for this compilation experiment.
