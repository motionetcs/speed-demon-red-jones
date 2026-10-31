# Live optimization work

Baseline snapshot: 31 October 2026, 04:00:12 UTC, preserved in `optimization-baseline-board.json`. These are public live-board measurements, not final holdout or judge totals.

| Track | Our time | Leader time | Our K | Leader K | Our track rank |
| --- | ---: | ---: | ---: | ---: | ---: |
| A | 0.539201 s | 0.019000 s | 8.810248 | 51.063272 | 55 / 67 |
| C | 0.962631 s | 0.029350 s | 6.433258 | 37.042980 | 43 / 58 |
| D | 0.995951 s | 0.121939 s | 9.302573 | 28.832712 | 34 / 60 |

Baseline leaders: A/D Cause Of Death; C NickTrapp. Exact leader values and run IDs are in the snapshot. The primary gap is throughput rather than dependencies; all three of our tracks have D=1 (zero extra runtime dependencies).

## A: parallel parse, count, scatter, and output

Hypothesis: the original serial parser, many small vectors, and serial formatting leave most cores unused. Parse independent newline-aligned chunks, reduce exact counts/errors, prefix-partition one contiguous latency array, then sort/format disjoint hour groups concurrently. Flat local endpoint tables preserve full string equality and grow if necessary.

All tiny, adversarial, sample seeds 7/19, and full-public outputs match, at 1/6/12 workers. Address/undefined-behavior sanitizer and Linux x86-64 sandbox reports are `opt-a-parallel-*.json`. The many-endpoint case additionally exercises table growth and chunk partitioning.

Five alternating local full-data runs after warmup gave these medians:

| Requested workers | Original serial binary | Parallel candidate |
| --- | ---: | ---: |
| 1 | 0.281404 s | 0.224491 s |
| 6 | 0.272663 s | 0.068589 s |
| 12 | 0.283396 s | 0.073818 s |

The original binary ignores the thread override. These Apple ARM process-launch-inclusive timings select promising candidates only. The first Intel board experiment uses 12 workers; a subsequent board comparison can decide whether six physical-core workers trade better against memory and merge overhead on the scoring CPU.

C and D refinements are now implemented and checked; the experiment history below distinguishes local evidence from official scores.

### Confirmed A board improvement

Run `run-ca62e267fa82`: 0.081951 s, 60,215,296 bytes, S=316, K=19.908239, 64.951642 machine points. All gates passed. This is about 6.58x faster than our original board run and adds 17.70 points. The next board experiment compares six workers against this twelve-worker result.

## C: quote-aware parallel parsing and shared exact membership

The candidate is implemented and passes reference, adversarial, full-public, memory/UB-sanitizer, thread-sanitizer, and Linux container checks. Local five-run medians improved from 1.155291 s to 0.132393 s at twelve requested workers. See `opt-c-parallel-*.json` for actual evidence. Its first board measurement passed: `run-a82ca12db6e4`, 0.124259 s, K=16.035293, 60.253844 machine points, versus the original 0.962631 s and 40.421548 points.

D's refined bidirectional/parallel-load/shared-label implementation is ready for its first board run. All reference, independent-seed, full-data, sanitizer, race, and Linux checks pass. The prototype and rejected approaches are retained in per-track PERF.md logs.

## Next combined candidate

A returns to twelve workers after six scored K=19.565079 versus twelve K=19.908239; the difference is small enough to include noise. Exact selection is retested after the memory-layout change and improved twelve-worker local median by about 6%. C compact lookup/numeric parsing improved local median by about 28%. D's parallel loader, bidirectional radix search, and query-owned shared atomic labels roughly halved local whole-process time; packed edges trade runtime against memory. No official improvement is claimed for these refinements until their exact commit scores.

Every refined track passes new independent sample seeds 23/41, full public byte/hash comparisons, adversarial cases, memory/UB and race sanitizers, and offline restricted GCC15 Linux validation. See `opt-a-parallel-selection-*`, `opt-c-compact-d-packed-*`, and `opt-d-packed-final-*`. Source fingerprints remain in historical reports; later prose edits naturally change documentation hashes.

## Refined candidate scored

Commit `072ce9b9046484a76c7e98aebd1e998e0d440d17` passed all gates on A/C/D. A: 0.076981 s, K=20.449888, 65.534547 points. D: 0.547406 s, K=10.876457, 51.824372 points. Both improve our previous measured best K. C: 0.106731 s, 37,818,368 bytes, K=14.656236, 58.301122 points; its lower time did not offset higher measured memory, so the refinement loses to C's previous 60.253844 points. Exact records: `board-opt-refined-acd.json`.

Next isolated board experiment changes only Docker compiler targeting to `-march=native` for A/C/D. Official harness documentation says these builds run on the scoring CPU. Offline Linux full and tiny output checks pass; the emulated CPU's performance is not used to predict an Intel gain. A separate uncommitted C membership-read fast path is deliberately excluded from this compilation comparison.
