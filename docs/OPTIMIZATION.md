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

Next hypotheses: quote-aware parallel CSV parsing and exact concurrent name membership for C; bidirectional search and faster graph loading for D. Neither is claimed as implemented or measured yet.

### Confirmed A board improvement

Run `run-ca62e267fa82`: 0.081951 s, 60,215,296 bytes, S=316, K=19.908239, 64.951642 machine points. All gates passed. This is about 6.58x faster than our original board run and adds 17.70 points. The next board experiment compares six workers against this twelve-worker result.

## C: quote-aware parallel parsing and shared exact membership

The candidate is implemented and passes reference, adversarial, full-public, memory/UB-sanitizer, thread-sanitizer, and Linux container checks. Local five-run medians improved from 1.155291 s to 0.132393 s at twelve requested workers. See `opt-c-parallel-*.json` for actual evidence. Its first board measurement is pending.

D's bidirectional/sparse-distance prototype is local and not yet submitted. Tiny/all-pairs/long-chain and two sample seeds pass; full-data performance and remaining checks must be completed before a board push.
