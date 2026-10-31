# Scored optimization results

Official public-board snapshot: 2026-10-31T04:58:06Z. These are best observed practice-board machine scores; final holdout and judging totals are separate.

Computed best-three machine-points geometric mean: **45.22 → 60.83**. Rank **44 → 30 of 56** eligible scored teams. Current leader: Cause Of Death, 78.62.

| Track | Original points | Our best points | Leader points | Track rank |
| --- | ---: | ---: | ---: | ---: |
| A | 47.25 | 66.60 | 85.79 (NickTrapp) | 37/70 |
| C | 40.42 | 63.35 | 79.34 (NickTrapp) | 30/59 |
| D | 48.43 | 53.36 | 72.99 (Cause Of Death) | 30/60 |

| Track | Best run ID | Time | Cgroup peak | K |
| --- | --- | ---: | ---: | ---: |
| A | `run-c70da1f28b23` | 0.069571 s | 60.28 MB | 21.482224 |
| C | `run-2f5d6b5da65d` | 0.099798 s | 14.08 MB | 18.492031 |
| D | `run-f813e2d591b2` | 0.554190 s | 131.21 MB | 11.670991 |

## Exact retained-source confirmation

Commit `07f2ac73092f64d98e40825809e88ce7010dca9f` passed every check, build, correctness, timeout, and sandbox gate. This latest combined confirmation is distinct from the best historical observations above. C and D use identical retained algorithms across those repeated runs; small timing/memory differences are variation.

| Track | Confirmation run | Time | Machine points |
| --- | --- | ---: | ---: |
| A | `run-c70da1f28b23` | 0.069571 s | 66.603962 |
| C | `run-9522fdbe2be1` | 0.100337 s | 63.220559 |
| D | `run-9da2b9e55b4a` | 0.590860 s | 52.648366 |

## Retained source

A uses twelve workers, direct field parsing, disjoint aggregation, and exact percentile selection. C uses twelve workers, quote-aware parsing, compact exact membership, and mapped name views with copies only for decoded escapes. D uses six query workers, at most four loaders, a lower-memory second parse into forward/reverse CSR, bidirectional radix Dijkstra, exact shared labels with private fallback, and lossless packed weights.

C's character arena ran faster but used too much official memory and was replaced. D's second pass was slower locally but improved official K by lowering peak memory. Twelve D workers looked faster on Apple ARM and scored worse on Intel, so six is retained. A's native compiler experiment scored lower; generic compilation is retained for A. C/D retain native compilation. Small repeat-run changes on unchanged code are identified as variation.

## Verification and evidence

Every submitted algorithm candidate passed targeted reference and adversarial comparisons, new independent generated seeds, published full-data hashes at multiple worker counts, memory/undefined-behavior and race checks for concurrency, and offline restricted GCC15 Linux validation. The retained D default was also exercised with no environment override. All scored submissions passed check, build, correctness, timeout, and sandbox gates. The live feed uses one timed run per push, so small differences are not statistical proof.

Raw records and decisions: [optimization log](OPTIMIZATION.md), [comparison JSON](optimization-comparison.json), each track's `PERF.md`, and `board-opt-*.json`. `tools/compare_board.py` reproduces ranks from complete official feed snapshots. `tools/watch_board.py` ties results to an exact pushed commit.

The retained source is confirmed above. The subsequent documentation commit changes no Dockerfile, C++ source, header, build file, or track metadata.

[Official team board](https://speeddemon.dev/board/#red-jones-00c4a7) · [Official JSON feed](https://s3.amazonaws.com/raptors.dev/speeddemon.dev/2026/board/board.json)
