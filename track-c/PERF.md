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

## Borrowed name bytes: memory hypothesis

The read-before-write membership experiment was exact but had no convincing local gain: at six workers it took 0.111600 s versus 0.105099 s, and at twelve 0.092379 versus 0.093038 s. It is rejected rather than claiming noise as an improvement. Raw checks and measurements: `opt-c-membership-read-*.json`.

The next candidate removes the shared character arena. Unescaped names retain stable views into mapped input; only decoded escaped names are copied into worker-owned stable strings. Exact full byte equality and release/acquire publication remain. The separate bitmap and direct numeric parser are retained. Five alternating full-data trials at twelve workers measured 0.106445 s first-parallel, 0.083619 s arena, and 0.085528 s borrowed names. Every hash matched; these are local launch-inclusive timings. The objective is a lower official memory peak while keeping most parsing gains. Record: `opt-c-borrowed-names-native.json`. Its real K remains pending.

## Native compilation: actual board record

`run-b050dd83ec00` on `f6b17e3b4d532d0dec3952df9da6d8d4297323de` passed every gate: T=0.092625 s, M=37,171,200 bytes, S=480, K=15.787118, machine points=59.915143. Record: `../docs/board-opt-native-cpu.json`.

Native targeting helps this arena version versus its generic build, but the result still trails the first parallel version at 60.253844 points. The borrowed-name candidate now targets this remaining memory cost.

## Memory experiment: actual board record

`run-cfa57a041382` on `28402fefb8136c3db205d3e312c87eef3b87b29f` passed every gate: T=0.10038 s, M=14,176,256 bytes, S=476, K=18.412702, machine points=63.255877. Record: `../docs/board-opt-memory-cd.json`.

Borrowed name bytes reduced board memory from 37,171,200 to 14,176,256 bytes. K exceeds both the arena version and the first parallel version, so this design is retained.

## Parser / D-worker comparison: actual board record

`run-2f5d6b5da65d` on `c21563dbfc44b1504bf8cc5d05f7fceaa8cbf1dd` passed every gate: T=0.099798 s, M=14,077,952 bytes, S=476, K=18.492031, machine points=63.349231. Record: `../docs/board-opt-parser-a-d12.json`.

Source is unchanged from the borrowed-name version. The small difference versus 63.255877 points is ordinary repeated-run variation, not a new algorithm improvement.

## Retained source confirmation

`run-9522fdbe2be1` on `07f2ac73092f64d98e40825809e88ce7010dca9f` passed every gate at 2026-10-31T04:57:43Z: T=0.100337 s, M=14,307,328 bytes, S=476, K=18.382779, machine points=63.220559. Full record: `../docs/board-opt-retained-acd.json`.

This confirms the retained source rather than a new optimization. A/C algorithms are unchanged from the prior parser comparison; D restores the earlier tested six-worker loader. The spread between unchanged-source practice runs is real, so best observed values and the latest confirmation are reported separately. Final holdout and judging remain separate.

## Second optimization round

Compact input-offset/length keys plus a separate escaped-pointer array and an early lookup prefetch preserve full equality and release/acquire publication. Local five-trial median changes from0.156199 s to0.138331 s. The numeric SWAR-only experiment was rejected (0.145250 versus0.142749 s); C retains scalar numeric parsing. All new-seed, full-data, growth/seam, memory/UB, race and Linux checks pass. Only an exact board run can establish an official gain.

Local phase intervals and alternating trials are in `../docs/round2-phase-profile.json` and `round2-layout-native.json`. They are Apple ARM development evidence, not official times.

## Hour-layout / compact-lookup board result

`run-60c3460244d4` on `d2fd0b53b6cf42a8786845b5d40c21e30865a8ce` passed all gates: T=0.097042 s, M=13,418,496 bytes, S=493, K=18.834184, machine points=63.74734. Exact record: `../docs/board-round2-ac.json`.

The compact/prefetch lookup improves observed K to18.834184. Next candidate adds a bounded comma search only for valid unquoted name/note fields; quoting and record-boundary logic are unchanged. Local medians0.125642/0.123132 s are close, so no statistically proven gain is claimed before the board run.

## Allocator / delimiter / private-D board result

`run-512dd8f4d6b5` on `b5df2af979bda869c0827b4dd59fda40f5a1ebe8` passed all gates: T=0.102277 s, M=13,639,680 bytes, S=501, K=18.241855, points=63.05345. Record: `../docs/board-round2-private-d.json`.

The delimiter candidate did not beat the preceding compact/prefetch K18.834184. It is not accepted as a standalone score gain.

## Offline profile-guided compiler experiment

Next experiment changes only the build: GCC profile generation with atomic counters, two sample datasets generated at seeds104729/130363, then profile-use recompilation with missing-profile errors enabled. The training generator is a byte-identical official copy, explicitly exempt from source size by the published harness; only `/solution` enters the final runtime stage. No public seed1 input, training dataset, cached result, or profile file enters that runtime image. The current algorithms/worker counts are unchanged from the preceding board comparison.

Offline Linux full-public/tiny outputs and129 untrained sample/adversarial runs across1/6/12 workers pass collectively. Reports: `round2-pgo-containers-{public,tiny}.json`, `round2-pgo-untrained-containers.json`. Untrained cases include name-table growth, quoted seams/EOF, percentile boundaries, and full-width graph distances. Actual board K decides retention; no compiler speedup is claimed in advance.

## PGO: exact board result

`run-902852c55b10` on `18896fe59b2dfd93036b023388f29dd0a4108449` passed every gate: T=0.098848 s, M=13,434,880 bytes, S=503, K=18.60067, points=63.476429. Record: `../docs/board-round2-pgo.json`. This is below the preceding best, so PGO and the weaker arena/delimiter experiment are removed from this track.

Next hypothesis: use canonical CSV name interiors as exact equality keys, count decoded lengths separately, and remove escaped-name allocations/pointer storage. Encoding doubles quotes and is injective under the legal grammar; quoted/unquoted equivalents are tested. Five alternating hash-checked full trials measured0.141451 s previous compact versus0.130563 s canonical on Apple ARM. Memory/UB, race, sample, full and restricted Linux checks pass; official K pending. A further private-membership prototype is correct but slower locally (0.112462 versus0.105678 s at12 workers; `round2-c-private-native.json`) and is rejected before submission.

## Canonical CSV / banded queue: real board result

`run-49603ba2b7b4` on `a5394d33e9058b843422529374362b00adbc0ecb` passed all gates: T=0.121885 s, M=12,218,368 bytes, S=460, K=17.302268, points=61.905152. Exact record: `../docs/board-round2-canonical-band.json`. Canonical name keys lower memory and S but run slower on Intel; observed total K is lower, so the earlier decoded-key algorithm is restored. A CRC hardware-hash prototype passes tiny/full checks but is also slower locally (0.142813 versus0.124712 s) and is rejected. Next: isolate PGO on the stronger d2 algorithm without the rejected delimiter-only change.

## Isolated compiler /128-band board result

`run-af1070009a13` on `46504cbb5cda9e3df890ffe202dab4e3f7587393` passed all gates: T=0.106622 s, M=14,123,008 bytes, S=495, K=17.774396, points=62.489742. Record: `../docs/board-round3-pgo-band.json`. The PGO result remains below the ordinary d2 build63.747340; restore that exact Docker build and remove its training generator.

## Variable-width packing: real board result

`run-2d4dd0b2c1e5` on `bba4fe03074368db5bb0bc0b49af917306e9bdb2` passed every gate: T=0.101829 s, M=13,885,440 bytes, S=493, K=18.260799, points=63.075989. Record: `../docs/board-round4-edgepack.json`. Runtime build inputs are unchanged from the retained configuration; the score difference is repeat variation.

Next compiler hypothesis: full-scale training at independent seed1000003, plus sample130363, better represents the scored workload than two samples. In C, sample and full use the same name-pool size, so new-key frequency differs materially. All input/output/profile files remain in builder stages. Public seed1 is not a training input. Validate on other seeds and real board K; retain only measured overall gains.

## Full-scale training / specialized decoder: real result

`run-948b67b2853e` on `eb16c07b177d5213110083063d4b38e50548714c` passed all gates: T=0.093897 s, M=13,455,360 bytes, S=495, K=19.124882, points=64.079939. Record: `../docs/board-round5-full-pgo.json`. Observed K improves beyond the ordinary build63.747340 to64.079939 points; retain full-scale training. This is one practice comparison, not a statistical guarantee. Next: dense exact name/country storage removes the separate bitmap and scattered representative strings.

Five alternating hash-checked local trials measured0.094802 s borrowed keys,0.083491 s owned name blocks,0.079711 s inline country words; RSS216.15/216.96/216.09MB. A separate initial-capacity comparison measured0.093464 s at131k versus0.090453 at262k, but added2.1MB; retain131k. Full/new-seed, growth/seam/country tests, strict sanitizers, a concurrent std::set key model and Linux checks pass. Actual board K is pending; Apple timings are not Intel scores.

## Dense C dictionary: exact board result

`run-62fc3f0d2df4` on `cb8cbedcd20a28153ebe790bb58f6b4c9bcc5f26` passed all gates: T=0.089832 s, M=13,357,056 bytes, S=524, K=19.414987, points=64.406855. Record: `../docs/board-round6-dense-c.json`. The dense name/country allocation improves the preceding64.079939-point best to64.406855; retained.

## Narrow graph-loader board result

`run-4bcf23d06742` on `61e345f753f6011b6ecd66c6cbba86030d72fa28` passed every gate: T=0.08826 s, M=12,447,744 bytes, S=524, K=19.86528, points=64.904735. Record: `../docs/board-round7-narrow-d.json`. Runtime/build inputs are unchanged; the observation is repeat variation.

## Flat/streaming A: exact board result

`run-3853c18e5195` on `2917982a9d0d26a813aacd1f2065331f6866016c` passed all gates: T=0.091169 s, M=12,324,864 bytes, S=524, K=19.584603, points=64.595738. Record: `../docs/board-round8-flat-a12.json`. Runtime/build source is unchanged; differences are repeat variation.

Next scanner hypothesis: SIMD equality masks locate comma/CR/LF for unquoted fields, with bounded complete vector loads and scalar tails. Quoted-field semantics are unchanged. Five alternating full native trials measure0.096884 s scalar versus0.092903 s NEON; no Intel gain is claimed. AVX2/SSE2/NEON scalar-reference and protected-page models, all-byte/offset/random tests, fresh sample/full hashes, sanitizers and Linux cases pass. Actual board K decides retention.

## SIMD CSV comparison: exact board result

`run-c4cd5934a4e4` on `1b21266eeee60232176372208d6c4120465ad988` passed all gates: T=0.089164 s, M=12,894,208 bytes, S=579, K=19.333879, points=64.315949. Record: `../docs/board-round10-simd-c.json`. Source growth outweighs the measured runtime/memory result, so restore the proven scalar-field/dense-key build from61e345f and remove csv_scan.hpp from the scored folder.

## Final retained-source confirmation

`run-a3119404362b` on `d28fe2590101b6b9a362e71b7bd8ee8f379f0741` passed all gates at 2026-10-31T07:14:40Z: T=0.096142 s, M=12,259,328 bytes, S=524, K=19.091712, points=64.042244. Exact record: `../docs/board-retained-final.json`. Runtime/build inputs match 61e345f byte for byte. This confirms the selected combination; historical best observations remain separate, and no repeat delta is called an algorithm gain. Subsequent documentation updates change no runtime/build/metadata input.

## Dense-store membership read experiment

The earlier membership read experiment used the older storage layout and had no convincing gain. This isolated retest uses the retained dense key/country allocation. Load the atomic country word first; a set bit immediately returns false. Otherwise fetch_or still arbitrates concurrent first sightings, so exactly one worker increments the distinct count. Country bits only transition from zero to one and never reset while workers run.

Nine alternating full-public Apple trials: at six workers baseline0.102924 s versus candidate0.099660 s; at twelve baseline0.086994 s versus candidate0.087103 s. This does not establish an Intel improvement. Fresh tiny/sample seeds, adversarial quote/BOM/EOF/growth/country cases, ASAN/UBSAN, TSAN, the concurrent std::set model and restricted Linux full/public plus39 fresh/adversarial runs pass. Reports: `../docs/round12-*.json`. Actual board K decides retention; no gain is claimed before that run.

`run-0025d5253a3d` on `12618553a4bb85eef54716306892ea4a4e4d2254` passed all official gates: T=0.090039 s, M=12,509,184 bytes, S=526, K=19.637468, points=64.654274. Record: `../docs/board-round12-membership.json`. The result does not beat the retained64.904735-point best, and native twelve-worker timings were inconclusive. Restore the simpler unconditional atomic update; no improvement is claimed. A/D code was unchanged in this run, so their deltas are repeat variation.

## Batched independent CSV work

Parse eight rows into stable row-owned scratch strings and metadata, prefetch dictionary slots during parsing, then prefetch published immutable keys before exact interning/country updates. The acquire load precedes reading a published key pointer; unpublished keys are skipped by the hint and still handled by normal interning. Every escaped name remains alive until its row is processed. Table-growth cancellation still discards the whole pass and reparses exactly.

A clean nine-rotation comparison measures0.088362 s baseline versus0.086102 batch8. Four-digit numeric parsing alone is0.087475; numeric plus batch16 is0.089353. Neither numeric variant is promoted: marginal/slower timing plus extra source. Initial round16 measurements are only screening because browser activity overlapped; round17 is sequential. Batched8 remains a modest local hypothesis to test on Intel, with source cost included in actual K. Broader correctness and Linux checks precede submission.

Batch8 passes fresh tiny/sample seeds839/853/857, grammar/BOM/EOF/escaped-name and concurrent-growth cases, wide country membership, full public outputs at1/6/12 workers, ASAN/UBSAN, TSAN and the exact name-store model. All42 restricted Linux replays and actual default entrypoints pass; image identities match the offline build. Reports: `../docs/round18-*.json`. Actual board K remains pending.

## Batch result and country/quoted-field hypothesis

Round18 commit b1388b0 passed all gates: run-06aa416c42cf, T=0.086574 s, M=13,041,664, S=547, K=19.744041, points=64.771802. It does not beat64.904735/K19.865280; remove the batch8 changes. Record: ../docs/board-round18-compact-batch.json.

Use the original scalar/dense-name loop, a direct26^3 country-code map for the specified plain uppercase three-byte countries, and a bounded first-quote SIMD scan inside quoted fields. Full quote/doubled-quote/BOM/embedded-newline/money/name semantics are unchanged; exact comparisons remain. NEON, SSE2 and AVX2 have scalar tails and protected-page tests. Nine rotating native public trials measure original0.075696 s, country map0.074906, map+quote0.071686. Source growth is included in actual K; no official gain is claimed yet.

Round22/23 source passes strict ASAN/UBSAN seeds863/877 and adversarial1/6/12 workers, TSAN887, all17576 country codes plus unmatched/escaped/embedded-newline cases, public hashes, native and GCC15 SSE2/AVX2 scalar-reference quote models,36 exact Linux replays and actual default entrypoints. Round23 C runtime inputs are byte-identical to round22's sanitized source. Country-map/batching, owner routing and compact-pointer experiments that lack a convincing local tradeoff remain outside scored folders; no sanitizer/board pass is invented for those rejected prototypes.

Round23 commit44a902b6b7db427741a1bfd75c99dbee184ec909 passes every gate: run-96e046ba1f77, T=0.084959 s, M=12,115,968, S=574, K=20.080817, points=65.139069. This beats retained64.904735/K19.865280, including source-size cost; retain quote+country mapping. Record: ../docs/board-round23-lazy-quote-band.json.

Next reduce the region lookup from16-bit cells to8-bit cells only when the number of countries is at most255; the all-ones value still denotes an unmatched region. A template selects one width for the entire processing pass.256 or more countries retain the exact16-bit lookup. The old allocation is released before name processing. Eleven alternating native trials give0.072048 s current versus0.070557 narrow; native peak RSS rises about1MB, so no memory gain is claimed there. Linux/cgroup behavior and total K decide retention.

Fresh samples907/911 and adversarial tests pass ASAN/UBSAN; seed919/adversarial pass TSAN. Independent country counts0/1/254/255/256/257/17576 and unknown IDs pass the official byte oracle at1/6/12 workers. Full public hashes,54 exact-image restricted Linux fixture replays, and actual native/Linux defaults pass. Records ../docs/round24-c-*.json. Standard name hashing remains; a separate sampled hash shows only~3% local improvement and is rejected before broader tests/board promotion.

Round24 commit1856d3937190d20e2b43dc49234e4d49238233b7 passes every official gate: run-d1c26a9725ac, T=0.086306 s, M=11,345,920, S=588, K=20.114046, points=65.174972. The narrow lookup saves770,048 bytes versus12,115,968 and produces a small0.035903-point new best, within run variation; retain the exact lower-memory layout. Record: ../docs/board-round24-narrow-c-retained-d.json.

Next simplify the record-boundary prepass: XOR the quote predicates directly, since only odd/even parity is required. The parser and boundary search retain every existing quoting rule. Thirteen alternating native full-public trials: count parity0.073550 s versus XOR parity0.071396, unchanged memory. Fresh947/953 ASAN/UBSAN,967 TSAN, all country-width boundaries0/1/254/255/256/257/17576, adversarial seams/growth/BOM/EOF, full public1/6/12 hashes,54 exact-image Linux replays and actual defaults pass. Reports ../docs/round30-c-*.json. Real board K decides this modest development hypothesis.

Round30 commit2c6c51e452faf284f013fd6b12d7333c310dcecc passes every official gate: run-9711d7d8fc4a, T=0.079040 s, M=12,390,400, S=591, K=20.635539, points=65.730791. This beats the preceding65.174972/K20.114046 despite higher observed charged memory; retain exact XOR quote parity. Record: ../docs/board-round30-cutoff-parity.json.

Round32 ce5ad53ee45296595a6eab2c9ac74d77fa4c61e7 repeats unchanged C source at66.040306/K20.931778, T=0.078051 s/M=11,907,072, run-a0191e29220f; every gate passed. This higher observation is repeat variation on the retained XOR/narrow-lookup source, not another algorithm gain. Record: ../docs/board-round32-balanced-frontier.json.

## Final restored-combination confirmation

Exact commit 71a023706495a99867f32a3e1856317f0d9e73bb passes check/build/correctness/timeout/sandbox for all A/C/D. This track's run run-e562a54a2e3f: T=0.077215 s, M=11,071,488 bytes, S=591, K=21.353266, points=66.473216. Record: ../docs/board-round32-retained-final.json. Every one of the27 retained runtime/build/metadata inputs matches this scored commit in round32-final-source-match.json. All weaker runtime experiments are removed. This repeated-source result confirms the combination; historical best and latest confirmation remain separate, and repeat deltas are not called algorithm gains. Further updates are documentation/evidence only.

## Round38: grouped exact name lookup

Eight immutable key pointers share one atomic64-bit control word. Control value0 means empty,1 marks the group's sole writer, and published fingerprint bytes only choose full-name equality candidates. Readers acquire the word and wait for any writer before reading pointers; a successful CAS claims one empty byte. The writer initializes its full key/country words, then release-publishes the updated word. Other writers wait, so publication cannot lose a neighboring byte or insert the same name twice. Byte-mask false candidates are proven to refer to published entries and still require exact byte equality. Hashes never substitute for equality.

The slots shrink from16 to8 bytes, plus one control byte each. String ownership, country atomics, width fallback and cancellation/reparse remain exact. Eleven rotating native trials: baseline0.097859 s/217.14MB, grouped0.091800/214.60MB. Separate key/bitmap arenas, extra key prefetch and larger changes lose locally and are not promoted. The refactored layout-independent name model passes the unchanged baseline as well as the experimental layouts; dedicated reserved-state/mask/failure tests, ASAN/UBSAN and TSAN pass.

Fresh1009/1013 strict sanitizer,1019 race/reference cases, full public1/6/12, country counts0/1/254/255/256/257/17576, grammar/growth/NUL/UTF-8/empty-key models, pinned GCC15 strict models,54 exact-image Linux replays and actual default entrypoints pass. Reports ../docs/round36-name-models.json and ../docs/round38-*.json. Only actual total K decides retention.

Round38 f378b2e51c3a9e3236a37bd0424317b633befa42 passes every gate, run-dc0fae91e407: T=0.081553 s/M=10,407,936/S=618/K=20.895526/66.002666 points. Charged memory falls, but this observation does not beat retained66.473216/K21.353266. Next align each eight-pointer group to64 bytes, ensuring the whole group fits one target cache line. The atomic control protocol/full equality are unchanged.

The Mac alignment variant is slower in a paired screen (0.083138→0.087865 s). A separate static unsanitized GCC15/glibc diagnostic after lookup allocations shows original pointer bases modulo64 of0/48/48/48 versus aligned0/0/0/0. That confirms a target allocator-layout difference, not a speedup. It motivates this explicit Intel test despite the Mac result; actual K decides. Full-pointer3-bit tagging, split arenas and extra key prefetch lose locally and are not promoted.

Fresh isolated1049/1051 strict ASAN/UBSAN,1061 TSAN, full-public1/6/12, every country-width boundary through17576, layout-independent name/control collision/failure models, GCC15 strict models,78 exact-image Linux cases and defaults pass. No pointer is truncated and no hash substitutes for full equality. Reports ../docs/round43-*.json.

Validation harness note: the original round38 native sanitizer/race jobs could share adversarial output folders. Generated sample seeds were separate. The suites were rerun with unique run IDs, all passed, and1047 image-matched Linux replays passed. These isolated reports are authoritative for per-binary adversarial attribution. Original reports are preserved with that limitation; no runtime fix was required. Round43 uses isolated names/output paths from the start.

Round43 273c7094c1ca4a1594486abdc45e52427cbdaae8 passes every official gate: run-dd6969257c21, T=0.114374 s/M=10588160/S=623/K=17.56279/62.229676 points. Neither the lean A word scanner nor aligned C groups beats the previous best. Restore exact bf75194 runtime/build/metadata for this track. The validated losing candidates remain in commit273c709 and raw reports; no gain is claimed. Record: ../docs/board-round43-word-alignment.json.

Further split full-hash state array screening uses thirteen rotating full-public trials with every output SHA checked. C baseline0.075203 s versus split0.076781 s, native RSS217.15/215.20MB. Reject before broader sanitizer/Linux/board promotion; no general correctness or official gain is claimed. Source patch ../docs/prototype-patches/round46-split-full-hash.patch applies tobf75194; raw report ../docs/round45-46-writer-split-bench.json.

Current-layout worker retest, nine rotating full-public hash-checked native trials:4/6/8/10/12 workers =0.098015/0.087796/0.077921/0.075184/0.074420 s. Keep12. Report ../docs/round47-worker-loader-bench.json.

Next keep each worker-private country's eight64-bit aggregate counters in one aligned64-byte Statistics base; immutable country text metadata follows outside that line. The exact name table, country atomics, parser and reduction are unchanged. Eleven rotating public-hash-checked native trials: baseline0.077443 s, counterline0.075166, membership-last0.079393, counterline+last0.075457, prefetch+last0.079165. Memory is essentially unchanged. Only counterline proceeds; source cost is included by the board.

Fresh1079/1087 strict ASAN/UBSAN,1091 TSAN, every adversarial/BOM/EOF/quoted seam/growth/country-word case, country counts0/1/254/255/256/257/17576, full-public1/6/12,78 exact-image Linux replays and true native/Linux defaults pass. Reports ../docs/round50-*.json, combined identities ../docs/round51-candidate-source-match.json. Real K must beat21.353266/66.473216.

Round51 c4f966f2d0e6f0602fac16f0eb8218b8f16499fd passes all gates: run-e039c5f8e04b, T=0.100513 s/M=12439552/S=595/K=18.266059/63.082243 points, build65.807 s. This loses to the retained best; revert to exactbf75194 runtime/build/metadata. Record ../docs/board-round51-prefault-counters-loaders.json.

Minimal library-delimiter retest on the restored parser is rejected before broader sanitizer/Linux/board promotion. Thirteen paired full-public native trials all match hashes; C baseline0.095854 s/unquoted-field memchr0.099188 s. Neither is faster. Background desktop activity is not isolated; only paired screening is claimed. Raw round54-delimiter-bench.json and reproducible bf75194 patch in docs/prototype-patches preserve the experiment.

## Selected-combination real confirmation

Exact commit 07c31360af938e391c3e09e3d21f969a1709b092 passes check/build/correctness/timeout/sandbox for every entered track. This track run-5f54924be806: T=0.080746 s/M=11706368/S=591/K=20.649589/65.745571 points. The current historical best is66.473216/K21.353266 at71a023706495a99867f32a3e1856317f0d9e73bb, with byte-identical runtime/build/metadata inputs. This repeat is not an additional algorithm gain. All27 selected inputs match the scored source and each current best record in ../docs/round55-final-source-match.json.1056 current-image Linux replays and actual defaults pass. A/C additionally pass fresh isolated1109/1117 ASAN/UBSAN,1123 TSAN and all-country-width checks; D's exact round50 isolated strict sanitizer/race/independent source is retained. No unscored prototype remains in a track folder. Further documentation updates change no compiled input. Record ../docs/board-round55-selected-final.json.

## Intel-targeted CRC/full-equality lookup and bounded data fields

New unquoted name/note data_field scans complete in-range64-bit words for their mandatory comma and then a scalar tail. Quoted fields retain the original exact decoder; header/region parsing uses the original generic delimiter grammar. The first byte-match mask locates the separator. Empty fields, every byte value, escaped/embedded-newline values and protected page boundaries are explicitly modeled. Native eleven-way rotating screens: baseline0.095360 s, four-digit decimal0.096315, word-field0.091553, combined0.102840. Only the word-field path proceeds. Name allocation alignment, quadratic/double probing and other screening variants show no useful total tradeoff and remain outside runtime.

On SSE4.2, hash_key processes bounded eight-byte words through CRC32 and a zero-initialized bounded tail, seeded with length. Other architectures retain std::hash. This is an ordinary hash candidate filter: full decoded-name bytes still resolve every collision, and the concurrent release/acquire/bit-set protocol and exact grow/reparse fallback are unchanged. No precomputed name catalogue or answer is used. Older native ARM CRC screens are not an Intel measurement. No Mac speed claim is made for the new Intel-only path.

Fresh1129/1151 strict ASAN/UBSAN,1153 TSAN, all country widths0/1/254/255/256/257/17576 and full-public1/6/12 outputs pass. GCC15/Linux strict ASAN/UBSAN explicitly enables and executes SSE4.2 for hash/field protected-page models, deliberate collisions, stable names up to1MiB, NUL/UTF8, country words and40,000 parallel exact-reference updates. The same -march=native local build environment confirms SSE4.2 active.135 exact-image Linux reference/adversarial cases and actual defaults pass. All27 selected source identities are proved in ../docs/round60-candidate-source-match.json. Real K must exceed21.353266/66.473216 including added source cost.

Round60 a5887ec541782b0ad141ecd878f1c7b04280ccde passes every gate: run-426e0e70df4d, T=0.07615 s/M=11919360/S=636/K=20.95513/66.064518 points. The candidate does not beat the retained best and is reverted to exact57cc23e runtime/build/metadata. Record ../docs/board-round60-intel-c-allocator-a.json.

## Exact local CSV synchronization without the full parity prepass

A quote followed by comma, preceded by neither quote nor field/record separator, cannot be an opening quote or a doubled-quote escape under the frozen grammar. It therefore closes a text field. From that known field boundary, the unchanged CSV parser advances to a real record terminator. Each raw partition takes the first such anchor at or after its offset; if none exists, it takes EOF. These true record ends are monotone, so all records belong to exactly one contiguous worker range. Unquoted/all-empty/adversarial fields may make a larger serial chunk, but never a guessed split. BOMs remain with the following record. No name, country, monetary or quote rule is narrowed. All-country fallback remains.

The serial boundary search replaces a complete parallel quote-parity scan. Eleven rotating full-public native trials: retained0.077766 s, parallel local search0.080865, serial local search0.074708; memory essentially unchanged. Choose serial. The word-field/CRC round60 is reverted: it loses total real K. The spec says nonempty generated name/note fields are quoted, leaving little scanning work for the unquoted-word path; its native screening delta is not evidence of a broad algorithmic win.

New independent boundary models record actual serialized record ends, assert every split is true and monotone (hence complete once-only coverage), and exercise1..12 workers, quote runs/escaped fake rows, empty/unquoted forms, Unicode/BOM/CRLF/EOF, shifted offsets and protected pages. Native NEON and strict GCC SSE2/AVX2 models pass. Fresh1163/1171 ASAN/UBSAN,1181 TSAN, all adversarial/growth/full hashes, countries0/1/254/255/256/257/17576,78 exact-image Linux replays and actual defaults pass. Identity proof round62-candidate-source-match.json. Real K must beat21.353266/66.473216.


## Round62 real synchronization gain and Intel scanner follow-up

Commit9933500b9335ab4866a21ac96990dac5fa2f8cb5, run-faef1e571800 passes all five gates: T0.071868 s/M11,997,184/S601/K21.725994/66.848983 points. This exceeds retained66.473216/K21.353266, including source/memory. Runtime falls6.93% versus77.215 ms historical best. Retain exact local synchronization. A single run does not eliminate timing/memory variation. Record ../docs/board-round62-mapped-splits-endpoints.json.

Next choose128-bit SSE2 first-quote loads on Intel instead of256-bit AVX2. Typical names are shorter than a32-byte load; narrower loads may reduce extra cache-line work and allow earlier matches. Long fields continue looping over every bounded16-byte vector, then the same memchr tail. Native ARM remains NEON; no Apple timing is presented as evidence for the Intel-width change. The deleted AVX2 branch reduces source, with all money/name/country/quote rules unchanged.

Fresh1193/1201 ASAN/UBSAN,1213 TSAN, full1/6/12 outputs, every country width through17576, strict GCC/Linux quote/CSV-boundary models with SSE2 and AVX2 compiler features,78 exact-image Linux replays and actual defaults pass. Both GCC builds execute the new header's explicit SSE2 branch; the quote test's stdout reports compiler features only. Forced-inline and deeper payload-prefetch screens lose and are not promoted. Real K must beat21.725994/66.848983.


## Round64 result and bounded ownership redesign

Round64 44d8c63 passes all gates: T0.074216 s/M12,070,912/S592/K21.401757/66.522472 points. This loses to21.725994/66.848983, so restore the62 synchronization/global-table combination before a new algorithm. Exact run ID: ../docs/board-round64-native-scalar-sse.json.

The old round20 routing parsed the file twice and stored every row offset. This new pipeline parses every row once, computes ordinary aggregates in reader-owned groups and sends only name/country/hash events through bounded SPSC vectors. At12 workers8 read and4 own disjoint hash shards; smaller worker settings keep the requested total, and one worker runs the same exact private-name logic directly. Every queue holds at most512 events and has one producer/consumer. Acquire/release transfers vector ownership. An ordered empty batch marks completion; cancellation wakes blocked producers/consumers through a shared flag. Consumers use private exact full-key hash tables and non-atomic country bits, grow without reparsing and copy each unique key once.

Canonical interior bytes are an exact internal equality key: quoted CSV doubles every literal quote; legal unquoted fields contain no quote, so their bytes already equal that encoding. Doubling quotes is injective, and outer quoting therefore does not affect equality. Empty/quoted-empty names match. The parser still computes decoded byte lengths, preserves all whitespace/Unicode/BOM semantics and exact cents. Events borrow immutable mapped input, including escaped raw interiors, avoiding per-row decoded-string ownership. No data catalogue or known answer is used.

The first decoded-string pipeline is only2.9% faster locally at8readers/4owners;4/8 and6/6 fail the tradeoff. Compact canonical events with512-record batches measure0.070793 s versus0.079207 for round64 over eleven rotating, full-public hash-checked native trials (10.6% lower), essentially unchanged peak process RSS216.94 versus217.09MB.128 batches0.072090 and256 batches0.077096; select512. These Apple screens do not establish Intel K. The candidate includes the128-bit scanner as part of this changed pipeline layout; no separate width gain is claimed.

Fresh1223/1229 ASAN/UBSAN,1231 TSAN, full1/6/12 hashes and all country widths0..17576 pass. Independent exact-name models force collisions,60000-key growth, country-word boundaries, stable blocks up to1MiB, NUL/UTF8 and allocation overflow. Queue/reference stress covers0/1/511/512/513/1025/4097 rows, all1..12 requested workers, quote/unquoted equivalence and prompt normal exception cancellation. Native/GCC strict models, exact CSV boundaries,120 current-image Linux replays and actual native/Linux defaults pass. Frozen context .build/round67/source. Only real total K exceeding21.725994 can retain it.


Round67 eb80bc6, run-b070e35b2761 passes every gate: T0.062764 s/M13,221,888/S660/K22.482722/67.592444 points. This improves66.848983/K21.725994, including source/memory. Runtime falls12.67% versus71.868 ms. Retain the bounded canonical-key pipeline; do not transfer the narrower-scanner-only result as a separate gain. Record ../docs/board-round67-bounded-c-pipeline.json. Historical and confirmation runs remain separate. The unified name-store model now dispatches to the correct private or historical shared API; both bodies are retested under native/GCC sanitizers rather than silently running an incompatible old API.


Round70 7402c7f, run-d2e3d6e500a5 passes all official gates: T0.062559 s/M13357056/S660/K22.473765/67.583792 points. Code is byte-identical to the retained67 pipeline. This67.583792 repeat is within0.01 point of67.592444 and also exceeds the preceding66.848983; it confirms the measured pipeline improvement without inventing another algorithm gain. Exact report ../docs/board-round70-endpoint-crc.json.


Final selected combination 0008c8ae9868ebf4746fa228ec813ab2dda8ab6d, run-55821b17a8ec passes check/build/correctness/timeout/sandbox: T0.06222 s/M13447168/S660/K22.504622/67.613586 points. All27 current inputs match this exact commit and each best track source in ../docs/round71-final-source-match.json. A/C small new best observations are unchanged-source variation; the two real C algorithm improvements are recorded separately. Further updates are evidence/prose only. Report ../docs/board-round71-selected-final.json.


Post-canonical pipeline balance retest (same512-event keys/layout), eleven rotating full-public native trials, every hash checked: readers/owners4/8=0.085573 s,6/6=0.072830,8/4=0.069911,9/3=0.074627,10/2=0.097526. Default8/4 wins; all others rejected at screening only, with no broad sanitizer/board claim. Total workers remain12. Raw round72-canonical-pipeline-balance-bench.json and round72-prototype-index.json preserve exact compiler overrides. No runtime change follows this screen.


## Batched prefetch inside private canonical-name owners

The old shared-table payload-prefetch rejection does not measure this newer owner-private pipeline. Here consumers process16 events in three stages: prefetch table slots, prefetch a matching key/header/exact country word, then perform the unchanged exact updates in original order. Hints never decide equality or count. Names.first may grow the table later, but no stored prefetched entry reference is reused; key blocks remain stable. Every queue ownership/release/acquire/cancellation rule is unchanged.

Eleven rotating full-public native trials: retained0.060312 s; batch8=0.059265, batch16=0.058061, lookahead8=0.059286, lookahead16=0.059313. Choose16 (3.7% lower), with essentially unchanged native RSS. Source cost still counts and only real total K decides.

Fresh1283/1289 ASAN/UBSAN,1291 TSAN, every country width through17576, every1..12 worker progress/batch/EOF/equality/cancellation case, full/default outputs, exact private-name GCC/native reference models and120 current-image Linux replays pass. Frozen75 inputs are independently tied to these exact images. Real K must exceed22.504622/67.613586.


Round75 commit342c0aa, run-b9ce72d11d0b, passes all five official gates: T=0.062494 s, M=13950976 B, S=685, K=22.166688, points=67.285041. Reject owner prefetch because it loses to67.613586/K22.504622. Restore the prior simple event loop before independently testing index geometry. Raw result: ../docs/board-round75-cache-prefetch-labels.json. One observation does not remove timing/memory variation.


## Separate owner-routing bits from exact table-index bits

Default routing uses hash%4, fixing the low two bits for every name in a given owner. The old table also used those bits for its home slot, restricting home slots to one quarter of the table. The new index uses hash>>2 for lookup, growth and retry; the stored full64-bit hash and full key comparisons are unchanged. This remains an exact map for every worker count and deliberately colliding hash, with no data catalogue. Prefetch75 is removed.

Eleven rotating sequential full-public native trials: retained0.059044 s,75 prefetch0.060912, plain shift2=0.057556, high32=0.057960, fold=0.058247; combined prefetch shift2/high32/fold=0.061420/0.059442/0.059948. All output hashes match and RSS is essentially flat. Choose the smallest2.5% faster plain shift2 hypothesis. These are Mac screens, not Intel gains.

Fresh1301/1303 strict ASAN/UBSAN,1307 TSAN, full1/6/12, countries0/1/254/255/256/257/17576, pipeline progress/reference/cancellation at every1..12 workers, native/GCC strict independent full-key/collision/growth/long-key models plus every fixed-low-two-bit owner,147 exact-image Linux replays and actual defaults pass. All source identities are frozen in round77-candidate-source-match.json. Real K must exceed22.504622/67.613586.


Round77/1a9deb5, run-1d87df780cae passes all official gates: T0.062544 s/M13774848/S661/K22.333360/67.447703. Although independently indexing owner hashes is logically sound and faster locally, total K does not beat22.504622/67.613586. Reject it and restore exact4eb6f36 C runtime/build/metadata and README. Current restored Linux source/image matches that score-confirmed source; no new C algorithm gain is claimed. Raw ../docs/board-round77-owner-index.json.


Round79 restored71 source passes every gate, run-491cee46b5aa: T0.062217 s/M13688832/S660/K22.425136/67.536754. Same-source variation does not beat best67.613586.147 independent fixtures replay successfully in the newly rebuilt restored-source Linux image; its ID is distinct from the older71 image and is recorded explicitly. Source bytes match the selected71 proof. No new C algorithm is kept.


Round81 unchanged restored71 source passes all gates again, run-fa6fa707f785: T0.062192 s/M13045760/S660/K22.646534/67.750087. This exceeds the older67.613586 observation with identical runtime/build/metadata. It is timing/memory variation, not a new C algorithm. Raw ../docs/board-round81-bounded-space.json.


Final selected combination b80c1ab98657ab4f5d4d6ce3ffe83b9012c2dcda, run-92f0b3cc5905, passes check/build/correctness/timeout/sandbox: T0.062514 s/M13045760/S660/K22.588135/67.694018 points. All27 current runtime/build/metadata inputs and each current best source match the selected commit in ../docs/round87-final-source-match.json. Historical best and this latest same-source confirmation remain separate; a lower repeat is not hidden or labelled a new algorithm regression. Current A96/C147/D1032=1275 matching-image fixture replays, fresh combined Make/public1/6/12 and actual native/Linux defaults pass. Later updates are evidence/prose only. Raw ../docs/board-round87-selected-final.json.


## Canonical keys with a shared exact table and all-reader parallelism

Public research reviewed31 October: Gunnar Morling's 1BRC results (https://www.morling.dev/blog/1brc-results-are-in/), Danny van Kooten's own C write-up (https://www.dannyvankooten.com/blog/2024/1brc/) and the exported transcript of Jon Gjengset's walkthrough (https://www.youtube.com/watch?v=tCY7p6dVAGE). These motivate evaluating synchronization and independent parsing work. No implementation from those sources or any competitor is copied. A Roy van Rijn YouTube page was opened, but transcript export was unavailable; no claim of having watched it is made.

The pre-pipeline shared-table experiments decoded escaped names per row. This new combination keeps67's injective canonical raw keys and current local CSV boundaries while reinstating our own event-written44d8c63 shared exact publication/country-bit table. All12 workers parse directly, with no event queue or dedicated owners. The initial131k sizing doubles and reparses after a fully joined capacity-canceled attempt, so arbitrary larger key sets are supported without a baked catalogue. Worker arenas outlive every reader. Real errors remain normal failures; only capacity cancellation triggers retry.

Eleven rotating full-public native trials: retained pipeline0.059397 s, shared131=0.055330, shared262=0.055004, peak RSS218.45/217.15/217.68MB. Select131 because the small262 timing difference does not justify its extra memory. Before broad validation, cancellation was made explicit: swallow Canceled inside workers, propagate actual errors, then retry only if too_small after join. Seven fresh paired trials of these exact89 bytes measure retained0.058817 versus selected0.056889 (3.3% faster), with roughly1.4MB lower peak RSS. These are Mac screens, not an Intel gain.

Fresh1409/1423 strict ASAN/UBSAN,1427 TSAN, full1/6/12 hashes, all country widths through17576, every1..12-worker reference/progress fixture, normal malformed-input cancellation, native/GCC shared atomic-key/country publication/full-key collision/stable long-NUL-UTF8/parallel std::set models,147 matching-image Linux replays and actual defaults pass. The120k-key fixture forces a131k-table occupancy retry and confirms no partial double counting. Historic test_name_pipeline filenames now supply worker/reference/cancellation cases only; no queue ownership is claimed for removed queues. All27 exact frozen inputs are proved in round89-candidate-source-match.json. Real K must beat22.646534/67.750087, including all source and memory costs.


Round89/864fb25 canonical shared table passes all official gates, run-6660a56146ef: T0.076907 s/M12455936/S598/K20.860806/65.966555. This loses to22.646534/67.750087 despite its faster native screen and smaller source/memory. Restore exactcfd094c C pipeline runtime/build/metadata and README. The i5 atomics/coordination tradeoff does not match the Apple result; no gain is claimed. New queue/event-layout work must build on the stronger private-owner pipeline. Raw ../docs/board-round89-canonical-shared.json.


## Bounded CPU-relax waits for the Intel SMT target

Restore the stronger private-owner pipeline after the canonical shared table loses actual89 K. Keep the32-byte full-width event representation. Producers and idle consumers now perform at most127 CPU spin hints before an ordinary OS yield on the128th unsuccessful poll. Cancellation remains checked on every outer wait. Progress resets the consumer budget. Release/acquire handoff, vector ownership, EOF markers, exact key/country logic and total requested threads are unchanged. x86 uses PAUSE, AArch64 a yield hint, other targets a compiler fence before the bounded OS yield. No host setting or harness is modified.

Intel's own optimization manual recommends short PAUSE spin loops to reduce shared-core resource/pipeline contention (https://www.intel.com/content/dam/doc/manual/64-ia-32-architectures-optimization-manual.pdf). The board pins12 threads on6 physical P-cores, whereas this Apple host does not model that SMT contention. This is a target-specific hypothesis, not a claimed native gain.

Eleven rotating full-public native screens: retained0.058402 s; compact16-byte512=0.059458, compact1024=0.058743, spin128=0.058973, combined compact1024/spin=0.059093. All hashes pass. Compact payloads do not justify their source/escape complexity here and remain unvalidated beyond screening; no general wide-offset/long-key proof is claimed for them. Select only the conservative spin128 for a real Intel test, explicitly despite1% slower Mac timing, with source cost charged.

Fresh1429/1433 strict ASAN/UBSAN,1439 TSAN, every country width through17576, all1..12 worker/reference/EOF/cancellation cases, native/GCC independent exact private-name models and147 exact-current-image Linux cases pass. The new image exercises the actual x86 PAUSE path; native uses ARM yield. Actual native/Linux defaults pass. All27 frozen95 inputs are tied in round95-candidate-source-match.json. Keep only if real K exceeds22.646534/67.750087.


Round95/13e3224 bounded CPU hints passes gates, run-17c0e893097f: T0.063298 s/M13656064/S678/K22.153886/67.272496. It loses to22.646534/67.750087; restore exactcfd094c original wait/runtime/build/metadata and README. Intel guidance alone is not evidence of a gain on this pipeline. Raw ../docs/board-round95-full-pgo-pause.json.


## Direct-pointer24-byte name events

Keep the selected private-owner pipeline and owned exact key/country storage. Change only queued events from32-byte string_view/hash/country records to24-byte direct pointer/full64 hash/guarded48-bit length/16-bit country records. C++ bitfield access handles the representation; every full byte of the original name is still compared. The length guard throws before use rather than truncating, and the existing unique-key storage already checks32-bit lengths. Every possible country through17577 and long1MiB binary/UTF8 names remain exact; no fixed catalogue or seed recognition occurs. Relative file offsets and per-batch escape lists from rejected93 are absent.

Raw103 native medians0.056967/0.047221 must NOT be read as17% causal gain: both variants change from45–47ms to57–59ms during the series, crossing their median at different trial counts. Treat smaller queue transfers/cache footprint only as an Intel hypothesis. A future real total K decides; baseline22.646534/67.750087.

Fresh1451/1453 strict ASAN/UBSAN,1459 TSAN, full1/6/12 outputs, every country width through17576, all1..12-worker reference/EOF/progress/cancellation fixtures, native/GCC exact private-name models and the new event pointer/length/every16-bit-country/full-hash/copy/vector-growth model pass. A mixed integer initializer in the new test initially failed compilation; the test type was corrected before model acceptance, with no runtime change. Exact current Linux fixture counts/IDs/defaults are in round104-candidate-source-match.json. Source identity must match this frozen proof before submission.

Other97/99 screens lose: numeric SWAR int/money/combined0.047465/0.047505/0.048001 versus0.045957; early buffer release0.045882, borrowed-key inline membership0.057289, combined0.056422 versus0.045475. All public hashes pass. Numeric helpers have native strict scalar/all-byte/random/protected-page unit proof only. Borrowed-key ownership changes have no broad lifetime proof and are discarded. No such unselected code enters a track folder.


Round104/252d750 C24-byte events passes all5 official gates, run-8960a9aefdfa: T0.062161 s/M13029376/S666/K22.627138/67.731481. It narrowly loses the stronger22.646534/67.750087 observation. Restore exactcfd094c C runtime/build/metadata and README; no17% speedup is claimed from the invalid native median comparison. Raw ../docs/board-round104-event24-batch32.json.


Round107 exact restored71 source passes all5 gates, run-2dd8d90f2a40: T0.062657 s/M13557760/S660/K22.389299/67.502025. This lower repeat is unchanged-source variation; best67.750087/K22.646534 remains. Rejected24-byte events are absent. Raw ../docs/board-round107-owned-loader.json.


## Process-local glibc arena cap on private-owner pipeline

The current71 pipeline allocates private owner tables/name blocks and bounded reader vectors. Test only final runtime-image ENV MALLOC_ARENA_MAX=2. No host setting, allocator library, parser/table/queue logic, compiler flag or PGO input changes. GNU's primary manual defines this as a per-process allocator-arena limit independent of core count (https://sourceware.org/glibc/manual/latest/html_node/Malloc-Tunable-Parameters.html). Reduced retained allocator memory versus lock contention is a hypothesis; native Apple allocator timing does not measure it. Earlier A cap losses and D cap wins do not establish the result on this newer C private-owner layout.

Image configuration explicitly contains MALLOC_ARENA_MAX=2; exact current-image full-public,147 independent grammar/country/worker/EOF/reference fixtures and actual defaults pass. Every C++/header/metadata/generator and training/compiler line is byte-identical to selected109, so original71 strict proof remains. Only new image/configuration behavior is freshly tested. All27 inputs/explicit image IDs are in round111-candidate-source-match.json. Keep only if actual K exceeds22.646534/67.750087, otherwise restore exact6e5950c C Dockerfile.


Round111/cc66c82 process-local arena cap2 passes every official gate, run-f54ecb2bb0d8: T0.063014 s/M13516800/S661/K22.334229/67.448548. It loses to22.646534/67.750087; restore exact6e5950c C Dockerfile without the added environment. No host setting was changed. Raw ../docs/board-round111-native-a-arena-c.json.

Round112 exact block-quote-mask payload parsing is rejected at native screening only. It keeps raw canonical key bytes and computes decoded lengths from exact quote parity/popcounts; generic header/region handling remains. Full-public outputs match all trials, but11 rotating medians are retained0.059089 s, mask0.061709, fast-first-quote0.059392. Median within-rotation ratios are1.0398 and0.9922 (0/11 and6/11 paired wins). The0.8% paired fast result does not pay for added source and is within variable native scheduling. No broad independent/sanitizer/GCC or real-score proof is claimed for these discarded scanners. The physical-byte/field-structural SIMD approach remains a separate future hypothesis, not implemented here. Raw ../docs/round112-c-quote-mask-bench.json.


Round118/ea8bfe3 unchanged selected C passes every gate, run-6fca1dceac83: T0.063053 s/M13754368/S660/K22.254707/67.371094. Same-source repeat, not a new algorithm gain; historical best remains separate. Raw ../docs/board-round118-calendar-a.json.


Selected restoration119/f69d4db, run-d94d17031dac, passes all five real gates: T0.098065 s/M13340672/S660/K17.954377/62.708517. All27 selected inputs exactly match6e5950c. This is a lower same-source confirmation, not an algorithm improvement; historical bests remain separate. C's unusually slow identical-source repeat is retained honestly, with no code regression asserted from one observation. Raw ../docs/board-round119-selected-confirmation.json.


Round120 streaming quote/comma/LF structural scan has correct full-public hashes but loses its native screen: retained0.058690291 s versus0.071416166, paired median ratio1.22605 and1/11 wins. NEON16-byte blocks execute; AVX2 source is unexecuted. Legal-input screen only: interior malformed-quote proof, GCC/sanitizers/image/official checks are absent and DockerCOPY was not updated. Rejected before promotion, preserved in round120 prototype index/patch. Primary conceptual research: Langdale and Lemire, https://arxiv.org/abs/1902.08318 (prefix quote parity and structural masks). CSV doubled quotes differ from JSON backslash escapes; no simdjson code or dependency is imported. A distinct121 Intel-oriented64-byte/PCLMUL scanner has fresh separate validation pending and is not a confirmed gain.


## Intel-oriented64-byte streaming CSV structural scanner

Candidate121 classifies quote/comma/LF masks together, carries exact quote parity across in-range blocks and emits five field spans per record with no global index allocation. Every doubled quote toggles parity twice; name keys retain the same raw canonical interior and decoded byte lengths subtract exact escaped-pair counts. Quote placement is validated against immediate separators/pairs, including block seams. Unquoted CR and unexpected numeric suffixes fail normally. BOM is still skipped only on record IDs; embedded LF/CR/UTF8 in quoted names/notes remain bytes. The original header/region lexer, safe record partitions,8-reader/4-owner queues, name storage, country widths, scalar numeric semantics and full1000003/sample130363 PGO are unchanged.

The AVX2 path classifies two32-byte vectors per64-byte block and computes prefix parity using PCLMUL when available. SSE2, NEON and scalar fallbacks preserve exactly the same masks; tails never load out of range.120's slower NEON16 result is not a target-machine result for this different implementation. This is explicitly an Intel-only performance hypothesis pending actual K, including added source cost; no Mac or emulated speedup is claimed. Conceptual citation: https://arxiv.org/abs/1902.08318 ; implementation is fresh and imports no parser/library code.

Fresh1567/1571 ASAN/UBSAN,1579 TSAN, full1/6/12 public outputs, countries0..17576 plus unmatched, every1..12 worker boundary/EOF/progress/reference/cancellation check pass. New strict native NEON/scalar and pinned GCC15 SSE2/AVX2+PCLMUL/scalar models execute exhaustive16-bit/random64-bit prefix references, all byte/offset positions, quote runs,50000 independent encoded record sets,1MiB escaped fields, protected page tails and malformed quote/field counts. Exact new production image passes147 independent Linux runs and normal cancellation fixtures at2/6/12 workers. Native GCC preprocessor flags explicitly include AVX2/PCLMUL/POPCNT, so actual Linux production replay covers that path. All28 candidate inputs/explicit image IDs/unchanged A96/D1080 cases/defaults are tied in round121-candidate-source-match.json. Keep only if actual C K exceeds22.646534/67.750087, otherwise restore every original f69d4db C runtime/build/metadata/README and Make dependency.


Round121/e3eb08d 64-byte structural scanner passes all five actual gates, run-b26ab1ba9e5f: T0.10498 s/M14282752/S835/K16.524405/60.906292. Reject and restore every original f69d4db C runtime/build/metadata/README and Make dependency, removing record_scan.hpp. Fresh source-specific strict/native/GCC/model/image proof remains attached to the losing scanner; no gain is claimed. Raw ../docs/board-round121-structural-c.json.


Round124/b3d0cef unchanged selected source passes every actual gate, run-e5d3c22f1226: T0.062566 s/M13844480/S660/K22.311993/67.426918. Same-source repeat only; preserve historical best separately. Raw ../docs/board-round124-avx2-d.json.


## Eight-byte owner entries with exact stable-block offsets

Candidate127/combined128 halves owner-table entries from16 to8 bytes: low32 bits of the full routing hash are only a rejection fingerprint, paired with an encoded block/word index. Every candidate still compares complete key length and bytes. Index0 marks empty, so low hash0/1/full64 collisions remain valid. Ordinary64KiB uint64 slabs keep allocated words stable;19 block bits and13 word-offset bits address them. Oversized names get a dedicated block. Every header and country word is initialized; only copied name bytes are compared. No pointer is truncated, no object representation with unread uninitialized data is moved, and storage indices survive metadata-vector growth. Explicit arithmetic/index guards prevent wrap. The block-index space spans at least32GiB before exhaustion, beyond the8GiB sandbox budget. Full-width key length and exact country membership semantics match the original representation.

125 flat-vector entries screen3–4% faster but add4MB native RSS due arena growth; rejected.126 stable blocks initially screen2.4% faster and save1MB, but this is not a speed claim for changed guarded127. Exact guarded127 final11 alternating full-public hashes measure retained0.059450542 versus0.059118541 s, paired ratio0.9981168 (effectively flat); peak RSS218415104→217366528 saves1048576 bytes. Source cost and Intel memory/runtime must still earn total K. All original parser/partition/8-reader4-owner/512-event queue/canonical encoding/full64 routing/PGO behavior stays unchanged.

Fresh1607/1609 strict ASAN/UBSAN,1613 TSAN, public1/6/12, country widths0/1/254/255/256/257/17576, every1..12-worker EOF/reference/progress/cancellation pass. New independent offset models execute under native/GCC ASAN/UBSAN: low32 fingerprints0/1/2/42/deadbeef/MAX with distinct full64 hashes, forced complete collisions, full-key std::set, all country words through17577, table/block growth, exact full/partial/dedicated1MiB blocks, saved indexed bytes after growth, long NUL/UTF8 keys, synthetic encoded-index maxima and overflow guards. Model dispatch is updated and the original private model is actually rerun under both compilers; the old pointer-model is not substituted. Exact production C image passes147 independent cases and normal cancellation at2/6/12 workers, plus actual defaults. A96 and D1080 selected-image cases remain explicitly matched. All27 inputs/model hashes/images are tied in round128-candidate-source-match.json. Keep only if actual C K>22.646534/67.750087. Otherwise restore names.hpp and README exactly to f69d4db, preserve the model/archive/losing results, and validate the selected combination.


Round129 inline sampled-hash screens on both original and offset name tables are rejected before promotion. Every full-public output hash matches; eleven rotating raw global medians are51.2405/49.0837/48.3386/51.7655ms for original/offset/sampled-original/sampled-offset, but a host speed-regime transition makes those global differences misleading. Median within-rotation original-based ratios are1.0/0.99957/0.99739/0.99674, effectively flat. Added source has no measured worthwhile native tradeoff; no byte/guard/distribution/collision/sanitizer/GCC/image/official proof is claimed. Exact parents/patches/scope remain in round129-prototype-index.json. The unchanged standard full64 hash remains submitted.


Selected128/93fc9c9 compact offset-block names passes all five real gates, run-5f755c073a9a: T0.062444 s/M12378112/S672/K22.777856/67.875642. Retain: total K improves22.646534→22.777856 and points67.750087→67.875642. Compared with the historical best, runtime is roughly flat/slightly slower0.062192→0.062444s, charged memory13045760→12378112 and S660→672. This is an observed score/memory tradeoff, not a causal runtime-speed claim. All offset-specific native/GCC/model/sanitizer/race/image/source proof remains exact. Raw ../docs/board-round128-offset-c.json.


Documentation-only head130/83a5f9c, run-965b0657fc79, passes every real gate with identical selected128 runtime inputs: T0.085043 s/M13434880/S672/K19.200964/64.166152. Lower same-source repeat, not a new algorithm regression; best records remain separate. Raw ../docs/board-round130-evidence-head.json.


## Cooperative parsing and exact name ownership

Candidate133 gives each requested worker both a record partition and one hash%threads name shard. Self-shard names update directly; other names travel through directed SPSC queues with64-event staging/published batches. A blocked sender pumps only its own incoming queues; consumption never sends. It also pumps after64 parsed rows. This distributes name lookup across12 owners while retaining12 total workers; thread1 is direct. Every partial batch precedes one empty EOF marker, and a worker drains every peer EOF before exiting. Exact ordinary aggregates remain worker-private, and each full-key country bitmap has one owner. No rows, keys, weights or identity are approximated.

The producer swaps a vector then publishes ready=true with release; the consumer acquires true before reading. It clears the vector then releases false; the producer acquires false before reuse. Each directed edge has one producer and one consumer. This follows C++20 release/acquire synchronization (primary draft: https://timsong-cpp.github.io/cppwp/n4861/atomics.order). A full-buffer cycle cannot consist only of non-consuming waiters: each blocked worker consumes incoming work, and finished workers have received every ordered peer EOF. Exceptions set global cancellation, checked during parse/wait/pump and before publishing. This reasoning plus tests is evidence, not a formal verifier certificate.

131/132 screens show wait-only pumping is4x slower; periodic pumping is essential for balance.64/64 selects a combined native memory/time hypothesis, not a claimed target result. Exact frozen13311 alternating full-public hashes measure retained0.059677041s/RSS217464832 versus cooperative0.058555875/RSS216694784; paired time ratio0.982248. Desktop is not isolated, source cost and Intel/cgroup K remain decisive. Unselected batch/pump variants have native screen only. Exact parents/macros/limits are in round131-133-prototype-index.json.

Fresh1619/1621 strict ASAN/UBSAN,1627 TSAN, full1/6/12, every country width and every1..12 topology pass. Black-box official-reference checks add64/128/256/512 seams, empty/partial/EOF streams, skewed and30000-distinct names,1MiB quoted records, BOM/UTF8/CRLF/cents/unmatched groups and early/late normal cancellation with30s invocation bounds. Python CSV's default131072 field cap initially stopped only the new synthetic1MiB oracle call; the test wrapper raises its own capacity4MiB, leaving frozen reference/harness code unchanged, then both complete ASAN/TSAN matrices pass. Input binding is explicitly rederived deterministically before metadata hashes are added.

An independent transport model primes every directed edge before a barrier, forcing full cyclic queues. It verifies complete token identity/exact-once delivery/EOF against separate reference data at all1..12 topologies,1/64/128 batches/partial tails, cancellation before/after space and throwing callbacks. Native ASAN/UBSAN+TSAN and pinned GCC strict transport/name/event models pass; offset-key/name/country proofs are rerun rather than substituted. Exact production image passes261 standard/reference replays plus228 every-worker valid and24 normal-error invocations; counts include some repeated case/thread configurations and are not a timing sample. Original A96/D1080 images and actual defaults remain explicit. All27 compiled inputs/tool/model hashes match round133-candidate-source-match.json. Retain only if actual C K>22.777856/67.875642; otherwise restore main.cpp/names.hpp/README exactly to83a5f9c, preserve the losing records and revalidate the selected128 combination.


Round133/16bedd2 cooperative64/64 worker pipeline passes all five real gates, run-de8f86b1e04b: T0.067282 s/M12169216/S676/K21.998877/67.120025. It loses K21.998877/67.120025 versus selected22.777856/67.875642. Despite lower memory12169216 vs12378112, time0.067282 vs0.062444 and S676 vs672 reduce total K. Restore main.cpp/names.hpp/README exactly83a5f9c; preserve all failed evidence, not a runtime speed claim. Raw ../docs/board-round133-cooperative-c.json.


Restored selected135/2b3834d, run-c71ee4a7dbf1, passes every real gate with exact selected128 runtime bytes: T0.095021 s/M12017664/S672/K18.574421/63.445764. Lower same-source confirmation, not another algorithm change. Current regular-image1323 cases, additional selected-C228 every-worker/24 normal errors, fresh combined public/defaults and all27 inputs match round135-final-source-match.json. Raw ../docs/board-round135-selected-confirmation.json.


Evidence-head137/715dcc6, run-9ebddf7e8d11, passes all five real gates on identical selected128 runtime: T0.062369s/M12300288/S672/K22.820315/67.916082 points. C has a slightly higher same-source best67.916082/K22.820315; that is variation, not another algorithm improvement. Raw ../docs/board-round137-evidence-head.json.


139/184778c run-0847c23610ca passes all five gates: T0.090417s/M12857344/S672/K18.785977/63.691689 points. Unchanged C has another lower same-source outlier; preserve137 best22.820315/67.916082 separately. Raw ../docs/board-round139-method-reserve.json.


140 new8-byte-entry geometry screen loses lower loads: retained0.058578s/RSS217415680; load75 paired1.01755/RSS219463680, load50 paired1.00878/218497024. Shift2 paired0.98349/217366528 and initial64k shifted0.98769/218447872 are modest, while their older16-byte counterpart lost actual77. No new candidate promoted.142 independently written aligned4/8/16-entry fingerprint/empty masks retain exact full keys and aim for grouped probing, conceptually motivated by Abseil primary design notes https://abseil.io/about/design/swisstables . No library/source imported. The group4 global median0.047363 versus retained0.056922 is misleading under a fast→slow native host transition; paired1.01047 loses. Group8/16 paired1.03636/1.03955 lose. No independent dense-prefix/first-empty/collision/growth/wrap/sanitizer/GCC/image/actual proof for these native-only variants. Reproducible source/parents are in round140/142-prototype-index.json; do not promote global medians.


145/348257e run-32bb1ce1e233 passes every real gate: T0.062142s/M12443648/S672/K22.809036/67.905347 points. Unchanged selected source: preserve this lower repeat separately from historical best; no new algorithm gain. All28 inputs match round145-final-source-match.json. Raw ../docs/board-round145-mapped-cache.json.


Evidence147/69322d0 run-e2882f361f1b passes all real gates on identical selected145 inputs: T0.062299s/M12214272/S672/K22.865201/67.958752 points. C67.958752/K22.865201 is a slightly higher same-source best; A/D lower repeats remain separate. No new algorithm gain is claimed. Raw ../docs/board-round147-evidence-head.json.


## Bounded windows for each reader/name owner

151 keeps8 readers/4 private name owners but replaces each single published vector with an independently event-written16-slot SPSC vector ring and256-event staging. A producer can continue filling other owners while one connection is briefly busy. Every row still routes by the original full64 hash and exact full-key country table. Producer swapping precedes release publication; consumer acquires before reading, clears before release consumption, and producer acquires that consumption before reusing the same cell. Published-minus-consumed stays within16 even under unsigned uint64 wrap. Single-producer/single-consumer roles, immutable borrowed-key lifetime and fully joined queue destruction are unchanged. Owners never send; FIFO empty batches finish each individual stream. Parse/send/owner loops retain normal cancellation. This reasoned handoff argument follows C++20 atomics.order/thread.join semantics, not a formal verifier certificate.

149/150 isolate ring capacities and staging sizes. Exact frozen15111 alternating full-public hashes measure retained0.058137458s/RSS217415680 versus16x2560.048972250/220741632, paired0.84547157. This15.45% local time hypothesis costs3,325,952 extra native RSS bytes and added source; only actual Intel/cgroup K can decide. Other parameters have screen-only proof.148 full-key hardware CRC32C loses natively: staged/padded paired1.03627/1.04121 despite strict independent polynomial/all-byte/guard-page ARM/GCC-SSE4.2/fallback models. No CRC runtime code is selected. Primary intrinsic references are recorded in round148-hash-models.json; no external implementation imported.

Fresh1721/1723 ASAN/UBSAN,1733 TSAN, full1/6/12, every country width and every1..12 topology/reference/1MiB/normal-error cases pass. New4095/4096/4097/262161-row one-key skew fixtures fill and repeatedly wrap16x256 windows at all1..12 workers; escaped UTF8/trailing spaces, embedded LF/BOM, unmatched groups and exact cents have full official-reference bytes and input SHA bindings. Independent fully primed token/key/country/order tests cover every2..12 role split plus1/11 and11/1, varied/partial batches, ordered EOF, empty/full cancellation and internal sequence wrap. Native ASAN/UBSAN/TSAN and pinned GCC strict ring+offset-name models pass. Names storage/NameEvent component text remains byte-identical; old queue/cooperative proof is not transferred.

Exact current C image passes285 regular replays plus228 every-topology valid/24 normal errors and48 all-topology pressure invocations, including overlapping configurations. A96/D1080 images remain unchanged. Actual native/Linux defaults and every28 input/image are bound in round151-candidate-source-match.json. Extra correctness invocations are not independent timing samples. Keep only on actual C K>22.865201/67.958752; otherwise restore main.cpp/names.hpp/README exactly69322d0, retain proofs and confirm the original source.


151/9e5d342 run-a2c9675ba013 passes every real gate: T0.06371s/M16265216/S687/K21.281155/66.39976 points. Reject per-connection16x256: K21.281155 loses22.865201/67.958752; charged memory16,265,216 versus12,214,272B grows and time0.063710 versus0.062299s fails the native hypothesis. Restore C main.cpp/names.hpp/README exactly69322d0. No causal phase explanation is measured. Raw ../docs/board-round151-spsc-windows.json.


## Pool publication capacity by name owner

155 replaces151's per-connection rings with one16-slot/256-event queue per owner shared by readers. A brief std::mutex try-lock protects only a nonblocking space check, vector swap and release publication. A full/busy retry drops the lock before cancellation/yield; consumers never acquire it. The mutex orders publishers, and release/acquire orders reader ownership and cleared-cell reuse. Each reader sends all its data before one EOF; consuming every reader EOF therefore exhausts all data under global FIFO. Private Names storage/NameEvent/parser/hash/roles/PGO stay exact. This is a new multi-producer protocol;151 SPSC proof is not transferred.

154 isolates queue capacity/batch tradeoffs. Exact15511 alternating full-public hashes: retained0.058430709s/RSS217399296, pooled0.052413208/217120768; paired0.89450447. Native10.55% time and278528-byte RSS hypotheses do not establish Intel/cgroup K. Fully primed NEW multi-producer exact-token/key/country/per-producer FIFO/global-EOF/internal-wrap/full-or-locked-cancel models pass native ASAN/UBSAN/TSAN and GCC strict checks. Fresh1753/1759 ASAN/UBSAN,1777 TSAN, full1/6/12, all countries/every topology/1MiB/normal-error and one-owner pressure checks pass. New C image has285 regular replays+228 topology valid/24 normal errors+48 pressure invocations, with overlapping case/thread configurations explicitly separated from timing. Exact29 combined source/image/default proof is round155-candidate-source-match.json. Keep only on actual K>22.865201/67.958752.


155/4191767 run-2382e05d8744 passes all five real gates: T0.062952s/M12304384/S687/K22.6378/67.741711 points. Reject pooled C: K22.637800/67.741711 fails22.865201/67.958752; time0.062952 versus0.062299s, memory12,304,384 versus12,214,272 and S687 versus672 all grow. Restore main.cpp/names.hpp/README exactly69322d0. Native10.55% gain did not transfer. Raw ../docs/board-round155-pooled-private.json.


157/34293c2 run-280abcfaed3b passes all five real gates after exact selected145 restoration: T0.062285s/M12685312/S672/K22.695362/67.796856 points. Lower unchanged-source repeat; historical best 67.958752 stays separate. All28 inputs and complete file sets match current best-track sources; fresh157 combined public/defaults and original C48 pressure replays pass. Rejected151/155 code is absent. Raw ../docs/board-round157-selected-confirmation.json and round157-final-source-match.json.


159/0882828 run-bada483f50d8 passes all five real gates on identical selected145 source: T0.063052s/M12009472/S672/K22.805252/67.901744 points. Lower same-source repeat; no new algorithm gain. Raw ../docs/board-round159-evidence-head.json.


## Decouple owner routing from table placement

163 changes only the compact name table's placement/rejection fingerprint from low32 to upper32 bits of the same full64 routing hash. With four owners, routing fixes two low bits; selecting upper bits avoids that fixed placement pattern. Full key length and every byte remain the final equality check; index0 alone denotes an empty entry, so fingerprint0/1 stay legal. grow() uses the same stored fingerprint. Country bits, offset blocks, parser, private-owner roles, original512-event SPSC pipeline and PGO are unchanged.

160 paired native ratio0.977261; frozen163 paired0.977752. Frozen global medians0.057768625 retained/0.058417709 new cross a host speed regime and do not show a causal global improvement; only the small paired hypothesis is offered for an Intel K test, with flat RSS and no source-layout expansion. Fresh1783/1787 strict ASAN/UBSAN,1789 TSAN, full1/6/12, all country widths/every1..12 topology/skew/quoted1MiB/BOM/cents/normal errors pass. New upper32 placement/collision/0/1/different-low-bit model also reruns the full offset std::set/country/index/growth/long-key model under native and GCC strict sanitizers. New C image passes141 regular replays plus228 every-worker valid/24 normal errors and48 pressure invocations; counts overlap other suites and are correctness invocations, not independent timing samples. Actual defaults pass. Exact29-source/local-image proof is round163-candidate-source-match.json. Keep only if actual K exceeds22.865201/67.958752; otherwise restore names.hpp/README exactly0882828 and original image263099fc....


163/d0bf708 run-da3afff606d0 passes all five real gates: T0.062251s/M12476416/S672/K22.777075/67.874898 points. REJECT upper32 fingerprint C: K22.777075/67.874898 points fails22.865201/67.958752. Time0.062251 is slightly lower than0.062299, memory12,476,416 exceeds12,214,272B, S672 unchanged. Native paired hypothesis did not establish a target gain. Restore names.hpp/README exactly0882828. Raw ../docs/board-round163-ordered-high.json.


165/72b040a run-6843e7f296dc passes all five real selected-combination gates: T0.062469s/M11997184/S672/K22.916113/68.007047 points. Restored original low32 source has a slightly higher same-source best68.007047/K22.916113; variation, not an upper32 gain. Every29 inputs/file set and local image matches selected/best sources in round165-final-source-match.json. Fresh Make/public/defaults and restored-C141 new-reference replays pass. Raw ../docs/board-round165-selected-confirmation.json.


167/b693b45 run-4812954357e8 passes all five real gates on unchanged selected165 inputs: T0.062718s/M11821056/S672/K22.938327/68.028087 points. C68.028087/K22.938327 is a slightly higher same-source best; A/D are lower repeats. No new algorithm gain. Raw ../docs/board-round167-evidence-head.json.


169 independently written complete bounded small-key comparisons cover BOTH first/last16 bytes for16..32-byte keys, optionally BOTH first/last8 for8..15, with full length/fallback equality. Public hashes pass, but paired block16=0.986655 and8+16=1.008735 do not justify added source/new guard/collision proof; global medians cross a host regime and are not a causal gain.170 retests owner prefetch on materially newer128 eight-byte offset entries, unlike losing75 direct-pointer entries:1/4 fingerprint probes with16/32-row blocks and fresh actual first() lookups. Every public hash matches, paired one16=1.021615,probe4-16=1.081742,probe4-32=1.086374 all lose despite misleading global medians. Reject every169/170 variant before broad sanitizer/race/guard/lifetime/GCC/image/official promotion. Source patches and proof limits remain in their prototype indices.173 C is original selected165, with no helper/prefetch change.


173/7e77576 run-35e53b7b8fe0 passes all five real gates: T0.062480s/M12267520/S672/K22.812203/67.908361 points. Unchanged selected165 C lower repeat;167 best68.028087/K22.938327 remains separate. Raw ../docs/board-round173-adjacency-pages.json.


175/e8a5109 run-5faf38e26ef1 passes all five real restoration gates: T0.062531s/M11665408/S672/K23.033578/68.118071 points. Higher unchanged selected165 source best68.118071/K23.033578 is variation. Every29 input/file set matches current selected and best-track sources; fresh Make/public/defaults and original D996 new-reference cases pass. Raw ../docs/board-round175-selected-confirmation.json and round175-final-source-match.json.


177/5bf3ee3 run-b41d413b7699 passes all five real gates, unchanged selected175 runtime: T0.063100s/M12566528/S672/K22.590786/67.696567 points. Lower same-source variation; best retained separately. Raw ../docs/board-round177-evidence-head.json.


178/42c50ce run-6fe931245d87 all real gates pass: T0.062372s/M12713984/S672/K22.669290/67.771896 points. Unchanged source lower variation; best kept separately. Raw ../docs/board-round178-full-pgo.json.


## Inline the existing complete CSV field function

181 adds only [[gnu::always_inline]] to Csv::field. After removing that attribute, main.cpp exactly equals selected175. Every body statement/header/key byte/decoded count/error/numeric path,8-reader/4-owner512-event pipeline/low32 offset names/full1000003+sample130363 PGO stays. No assumptions or input-specialized results are introduced. The existing in-class definition is already inline for linkage; the attribute controls compiler inlining restrictions. Primary GCC attribute documentation is recorded in round178-181-research.json.

179's11 rotating full-public hashes measure retained0.058046750s/RSS217399296, field-inline0.055526542/217415680, paired0.960862 (3.91% native hypothesis, no RSS gain). Trimmed unused returned-flag1.005353, combinedinline+trim0.963010 and compile-time template0.993777 remain native-only screens, without broad byte/guard/strict/GCC/image proof. Only field-inline is promoted. D180's two-digit tail also loses1.015139 and is not promoted or generally proved.

Fresh2003/2011 strict ASAN/UBSAN, untrained full2027,2029 TSAN, public1/6/12, every country width, every1..12 worker topology/EOF/1MiB quoted field/skew/distinct names/one-owner262161 pressure and normal cancellation pass. New pinned GCC strict production144 valid/30 normal errors and exact new PGO image405 valid/30 normal errors pass; identical input+thread cases are deduplicated. Original exact header/protocol models remain source-bound; no unexecuted new protocol is claimed. Fresh combined Make/full public/defaults and all29 source/context/image/file sets are in round181-candidate-source-match.json. Keep only if actual C K>23.033578/68.118071, otherwise restore Cmain/README exactly42c50ce and original image263099fc.... A178 remains provisional and D original. No target improvement claimed until actual all-track record.


181/95c75c7 run-942c51635030 all real gates pass: T0.062821s/M12693504/S672/K22.595417/67.701018 points. Reject field-only inline:22.595417 loses original best23.033578; restore Cmain/README exactly42c50ce and control263099fc image. New combined numeric+field184 remains unscored outside root. Raw ../docs/board-round181-inline-field.json.


## Inline the existing numeric parsers along with fields

184 explicitly inlines field, integer and amount, with every body statement/header unchanged selected175; removing exactly three GNU attributes reproduces that original main.cpp. Field-only181 passed real gates but lost K22.595417 versus23.033578, and was completely restored before this distinct combined trial.182's integer-only0.943706/amount-only0.976130 remain screen-only; both0.929971 relative to field-only181 selects the combined hypothesis. Fresh exact18411 rotating public trials versus original175 measure retained0.056504709s/RSS217382912, field-only0.054015500/217415680 (paired0.946269), all-inline0.049243500/217399296 (paired0.890574). Native10.94%/flat-RSS is only a hypothesis, especially after181's target loss.

Fresh2053/2063 strict ASAN/UBSAN, full2039,2069 TSAN, public1/6/12, all countries/every1..12 topology/EOF/1MiB/one-owner pressure/normal cancellation pass. Exact new pinned GCC strict144 valid+30 normal errors and production-image405 valid+30 normal errors pass, deduplicated by input/thread. Fresh combined Make/public/defaults and29 source/context/image/file-set proofs pass. Copied diagnostic/scoping captions initially said181 while all executed source/binary/report paths and hashes were184; metadata captions were corrected with explicit notes, retaining original completed logs and every measurement/hash. No runtime fix. round184-candidate-source-match.json binds the exact inputs. Keep C only on real K>23.033578/68.118071; otherwise restore complete Cmain/README to42c50ce and original263099fc image. No confirmed target gain yet.


184/2a228b4 run-9f659978a7c5 all real gates pass: T0.062545s/M12468224/S672/K22.726464/67.826593 points. Reject combined parser inlining:22.726464 loses original23.033578 despite native10.94%. Restore Cmain/README exactly42c50ce and original263099fc image. Fresh full strict/GCC/image proof stays historical to rejected code. Raw ../docs/board-round184-inline-parsers.json.


187/d6cea74 run-0040c07b5d6f all five real gates pass: T0.098959s/M12079104/S672/K18.182538/62.982725 points. Original C fully restored. Lower same-source0.098959s/62.982725 outlier stays separate from68.118071 best; no algorithm-regression or target-phase explanation asserted. All29 inputs/full file sets match current selected and best-track sources, round187-final-source-match.json; fresh original-C405 references/30 errors and combined public/defaults pass. Raw ../docs/board-round187-selected-confirmation.json.


189/ceb78f8 run-31c9587a4cc3 passes all five real gates on unchanged selected187 runtime: T0.061886s/M12267520/S672/K22.921420/68.012076 points. Lower same-source variation; C0.061886s here versus1870.098959s is not a new algorithm gain or causal explanation. Raw ../docs/board-round189-evidence-head.json.


## Bounded AVX2 first-quote search

190 adds only a32-byte AVX2 first-match loop before the original SSE16/NEON/scalar tail. Each complete in-range load compares bytes to quote, extracts a32-bit mask and uses trailing-zero count only for a nonzero mask. Mask bit31 is preserved through uint32 conversion. Tail/parser/escaped-pair/decoded count/raw canonical key/numeric/country/partition/queue/PGO/default logic stays. This is distinct from losing121's full structural/PCLMUL parser and112's payload quote-count mask. No CSV grammar assumptions are weakened. ARM executes the unchanged fallback, so no native ARM speedup is claimed. Primary Clang intrinsic semantics and official kickoff transcript support the AVX2-only target hypothesis; no played-video claim.

Fresh independent quote model checks0..256 lengths/all quote positions, every256 byte at96 offsets,65536 low16 masks/high31/63,100000 random binary buffers,1MiB/logical ends with quotes immediately outside and both protected-page boundaries. NativeNEON/scalar and GCC AVX2/SSE2/scalar strict ASAN/UBSAN pass; exact preprocessed helper confirms32-byte AVX2 block only in AVX2 mode. New2101/2111 ASAN/UBSAN/full2129,2131 TSAN, all countries/every topology/1MiB/pressure/normal errors pass. GCC strict144 valid+30 normal errors uses-march=native and proves__AVX2__, so new path really executes. Exact PGO image405 valid+30 errors, public1/6/12 and actual combined native/Linux defaults pass. Original queue/name protocols stay source-bound; nativeTSAN is unchanged NEON/shared-protocol evidence, not an unexecuted x86TSAN claim. All29 source/image/context/file sets bind in round190-candidate-source-match.json. Keep only if real C K>23.033578/68.118071, otherwise restore quote_scan.hpp/README exactlyceb78f8 and original263099fc image. No target gain before actual result.


190/1cd2a7b run-4c9bd9fe7e59 all real gates pass: T0.061274s/M12419072/S682/K22.928248/68.018544 points. Reject AVX2 quote-only:22.928248 loses old23.033578. T0.061274s is lower than old best0.062531s but M12419072 versus11665408 and S682 versus672 cost more; exact quote/README restored. No causal timing estimate. Raw ../docs/board-round190-avx2-quote.json.


## Intel-only whole-key CRC, with complete key equality

193 uses own event-written148 staged8/4/2/1-byte CRC32C algorithm, now only on little-endian x86-64/SSE4.2; other targets retain original std::hash. New exact provenance/recorded event patch is round193-hash-provenance.json, not an organizer certificate. Old148 ARM-native loss is not an Intel result, and old primitive proof is not claimed as new integration. Hash length seeds CRC state, every byte is read and the32-bit state is mixed into64 routing bits: still32 bits of entropy, never cryptographic or a replacement for complete key equality. Original low32 table/index/country/quotes/queues/PGO remains; quote-only190 is removed, no combination. New header is counted/COPYed with an explicit Make dependency.

Fresh native fallback/GCC SSE4.2+fallback strict polynomial/all-byte/random/1MiB/both-guard models pass. Exact current offset std::set/index/country/growth/long-key/overflow models freshly execute under all dispatches. A genuine production CRC collision is found without injected hashes: both distinct keys stay distinct at every country through17577. Those exact bytes pass full CSV reference at all1..12 workers,512/513/8193 EOF/pressure,narrow/wide lookup/BOM/quotedLF/signed cents, under native strict/race and exact activated-GCC/image paths. New2179/2183 ASAN/UBSAN/full2203 and2207 TSAN, every country/topology/1MiB/pressure/normal errors pass. GCC-native separate static activation probe and__SSE4_2__ prove CRC selection;168 strict valid+30 errors and501 exact PGO-image valid+30 errors pass. Native fallback is not falsely called x86TSAN; unchanged SPSC synchronization and deterministic read-only hash reasoning stay explicit. Public1/6/12 and composite195 actual defaults/source30 proof pass. Keep only if real C K>23.033578/68.118071, otherwise restore names/Docker/README and remove name_hash.hpp/Make dependency toceb78f8/original image263099fc, preserving A winner. No target gain before real record.


195/10e3ade run-acc2c9e9eb34 all five real gates pass: T0.061860s/M12578816/S730/K22.530101/67.638157 points. Reject Intel CRC:22.530101 loses23.033578; T0.061860/M12578816/S730 versus old0.062531/11665408/672. Restore names/Docker/README, delete name_hash.hpp, restore Make dependency. Full strict/actual collision proof stays historical. Raw ../docs/board-round195-native-a-crc-c.json.


197/8003961 run-5a9a5be47984 all five real gates pass: T0.062422s/M11792384/S672/K23.003818/68.089996 points. Original std::hash/low32/quote C restored;23.003818 remains below best23.033578. No new algorithm gain. All29 source/build/metadata inputs/full file sets match selected and current best-track sources. Fresh original A81/C501+30 errors, combined public/defaults pass; round197-final-source-match.json. Raw ../docs/board-round197-selected-confirmation.json.


199/d4027c9 run-a6160af16561 all five real gates pass on unchanged selected197 runtime: T0.062815s/M12214272/S672/K22.771094/67.869194 points. Lower same-source repeat, historical best kept separately. Raw ../docs/board-round199-evidence-head.json.


200 read-only two-sample/independent full2203 profile: lossless trailing-space-run compression would save only3400–3960 rounded key-payload bytes;95.3k full bases remain. Reject before implementation; preserve every space and exact canonical key.198 sparse-country proposal also remains rejected. No runtime catalogue/seed recognition or cgroup/K claim.

202 re-evaluates shifted home and24-byte events only on materially newer128 eight-byte offset entries. Old77/104 sixteen-byte-table losses are retained; new11 rotating native full-public hashes give paired0.925304 for shift2 and0.942004 for event24. Select only shift2 for fresh204 proof, not a combination. Event24 remains native-only/unproved and absent. These are local hypotheses, not Intel scores.

204 changes exactly three owner-table expressions: home index, rehash and retry use fingerprint>>2, so default four-owner routing no longer fixes the first two home-slot bits. Stored low32 rejection fingerprints, full length/byte equality, full64 owner routing, private stable blocks/country bitmaps, original quote/parser/eight-reader/four-owner/512-event queues and native GCC/full1000003+sample130363 PGO stay. Other owner counts remain exact without a distribution or collision-free assumption.

Fresh native and pinned GCC-native strict offset/index std::set models cover full-key/low32/full64 collisions0/1/MAX, shifted-home low2 aliases/wrap, table/block growth, all country words, long NUL/UTF8/1MiB keys and overflow. New model executes every1..11 owner routing with actual table growth. Fresh2251/2267 ASAN/UBSAN/full2281,2273 TSAN, every country width/topology/1MiB/pressure/normal error pass. Pinned GCC strict production168 valid+30 errors and exact new PGO image501 valid+30 errors pass, along with public1/6/12, combined Make and actual native/Linux defaults. CRC-pair fixture inputs here do not claim CRC activation; hashing remains original std::hash. All29 inputs/full file sets and explicit images bind in round204-candidate-source-match.json. Only supported real C total K above23.033578/68.118071 permits retention; otherwise restore names.hpp/README exactlyd4027c9 and original C263 image, preserve honest records and confirm restored combination. No target gain is claimed before the actual run.


204/0112b33 run-9de1df726683 all five real gates pass: T0.061410s/M12238848/S672/K23.020854/68.106072 points. Reject shifted home:K23.020854/68.106072 loses23.033578/68.118071 despite lowerT0.061410 versus0.062531s; M12238848 versus11665408 grows, S672 unchanged. Restore names/README exactlyd4027c9 and original C263 image. No precise causal decomposition or target gain claimed. Raw ../docs/board-round204-shifted-offset-home.json.


206/e3140e0 run-5334e2cb1c9b all five real restoration gates pass: T0.062146s/M12095488/S672/K22.938120/68.027891 points. Original selected197/187 runtime restored; lower unchanged repeat, historical best separate. All29 inputs/full file sets match selected and current best-track sources, round206-final-source-match.json. Fresh original C501 independent204 references/full2281/all workers+30 errors and combined Make/public/defaults pass. Raw ../docs/board-round206-selected-confirmation.json.


208/8acb692 run-ad4c58e5b039 all five real gates pass on unchanged selected206 source: T0.062835s/M12251136/S672/K22.753751/67.852650 points. Lower repeat variation; historical best separate. Raw ../docs/board-round208-evidence-head.json.


210 unchanged selected206 binary at12/4/6/8 total workers has paired1.0/1.550241/1.239685/1.001581 across11 rotating full-public native hashes. Native6 is23.97% slower and about1MB lower RSS;8 is flat. Apple CPU does not model6 scoring P-cores/12 SMT. Primary Intel Core datasheet/resource-sharing guide motivates a target-only normal-concurrency experiment, not a speed prediction. No CPU affinity, host/BIOS, harness/timer/counter or credentials change.

212 changes only final image ENV SPEED_DEMON_THREADS=6:4 readers/2 owners at runtime, native CLI fallback and original full1000003/sample130363 PGO still12 (8/4). Every C++/header/build/profile byte unchanged; original std::hash/unshifted offset/private SPSC/country logic stays. New image has exactly C263 filesystem and ELF, with one added environment key only, verified by read-only SHA/config inspection. Original501 explicit-worker/reference and exact-source strict/race models remain binary-bound. Fresh actual ENTRYPOINT/no-argument/no-thread-override default6 executes56 unique independent reference inputs and4 normal errors, including untrained full2281/samples2251/2267/2273/country widths/topology/1MiB/pressure/BOM/EOF/signed cents. Synthetic CRC-pair inputs do not activate CRC. Public1/6/12 overrides, actual image6/native12 defaults, composite Make and all29 source/image proofs pass. Only real C K>23.033578/68.118071 permits retention; otherwise restore full Docker/README to8acb692 and C263 image. This is explicitly an Intel-only trial despite slower Mac6; no target gain before actual record. Normal frozen harness invocation preserves image environment and was read only, never modified.


212/e65b2b0 run-c0a35c1d59a9 all five real gates pass: T0.083071s/M10715136/S673/K20.322071/65.398398 points. Reject C6:K20.322071/65.398398 loses23.033578/68.118071; lower memory10,715,136B does not compensateT0.083071s/S673. No target gain. Restore chosen baseline before any retained selection; separate8-worker candidate still requires full no-override/image/source/real-K proof. Raw ../docs/board-round212-unused-a-c6.json.


213 separately tests only final-image default8 after212 C6 loses:5 readers/3 owners using the existing formula. All C++/headers/compiler/training stay original206/C263; native CLI/PGO12 unchanged.210 native8 is flat1.001581 versus12, unlike6's1.239685; three owners also avoid fixing low home bits under modulo4. This is a proposed mechanism, not measured causal phases or a collision/distribution assumption; three tables can grow larger. No affinity/host/BIOS/harness/timer/counter changes. New image exactly preserves C263 filesystem and ELF with one ENV8 key only. Fresh actual ENTRYPOINT/no-argument/no-thread-override56 independent reference inputs+4 normal errors (including untrained full2281/samples/country/topology/1MiB/pressure/BOM/EOF), public1/6/12/defaults/native12 and all29 source/image proofs pass. Original explicit-worker501/strict/race evidence remains code/binary-bound. Aio and B57 fully restored, D unchanged. Only actual C K>23.033578/68.118071 permits retention; otherwise restore full Docker/README to8acb692/C263 and confirm original combination. Real performance decision pending; no target gain claimed yet.


213/4e41c96 run-4afb857fd75f all five real gates pass: T0.090841s/M11931648/S673/K19.020029/63.960559 points. Reject C8:K19.020029/63.960559 loses23.033578/68.118071; T0.090841/M11931648/S673. Restore complete Docker/README to8ac/C263; native flat8 did not transfer, no target-phase causal explanation measured. Raw ../docs/board-round213-c8.json.


217/3f3cff4 run-4d745e414ae8 all five real restoration gates pass: T0.063535s/M12296192/S672/K22.611452/67.716422 points. Full original selected206/187 runtime restored after unused-A method removal and C6/C8 default-worker losses. All29 root/frozen/scored/best inputs and complete file sets match, round217-final-source-match.json. Fresh combined public1/6/12 and native/Linux actual default12 pass; exact206 native executables reused, immutable A81/C501/D996 image/strict/race references retained by source/binary identity, no fresh whole-bank217 replay or compilation claimed. Best/latest and variation separate. Raw ../docs/board-round217-selected-confirmation.json.


221 candidate: match six-worker build-time PGO to final image runtime6, keeping original complete C++/headers, flags, official generator1000003/full and130363/sample. Own local218 ELF owner4 fast branch/cold alternate division motivates this test, not an asserted cause or gain. Native210 six-worker loss and real212/213 runtime-only6/8 losses remain evidence. Accept only real all-gates C K>23.033578; restore otherwise.


220/0e5f1aa unchanged selected217 runtime, run-2c593768268e, all five actual gates pass: T0.079011s/M12619776/S672/K20.171351/65.236749 points. Lower unchanged repeats, not new gains; bests separate. Raw ../docs/board-round220-evidence-head.json.


221/3611979 run-60d712df6638 all five actual gates pass: T0.080874s/M10493952/S673/K20.682353/65.779997 points. C matched6 build/runtime loses K20.682353 versus23.033578; fully restore original C Docker/README. A/D unchanged lower repeats. New strict177/image510/default59+errors proofs remain historical to candidate. No target phase/cause claim; raw ../docs/board-round221-matched-six.json and round221-scored-source-match.json.


224 matched8 build/runtime: original C++/headers/compiler flags and training1000003/full+130363/sample unchanged. Native8 previously flat; runtime-only8 lost real K19.020029. Matching6 also lost20.682353. This distinct3-owner trained profile is a separate negative-evidence-aware target test; no causal denominator or gain claim. Keep only actual K>23.033578 with all gates, otherwise fully restore original.


224/bdbdcb5 run-4de10ff88942 all five actual gates pass: T0.097965s/M12021760/S673/K18.287870/63.108157 points. C matched8 build/runtime loses18.287870 versus23.033578; fully restore original C Docker/README/C263 image. A/D unchanged lower repeats. Source-identical221 strict/race/GCC stays relevant to original C++,224 production510/default59+errors proof is historical to rejected PGO/config. No target phase/cause claim. Raw ../docs/board-round224-matched-eight.json.


226 current original low32/8-byte-table batch128/256/1024 versus512,11 rotating full-public native hashes at12 workers paired1.049064/1.000470/0.995618; at8 paired1.011321/1.004029/1.017199. Keep512: slower/flat,1024 adds RSS. No targetK/cgroup claim or new batch-boundary/strict/race/GCC/image/actual proof for rejected constants. Raw ../docs/round226-c-batch-screen.json.


225/2d71679 run-eaf5b50e30e8 all five actual restoration gates pass: T0.062347s/M12673024/S672/K22.688472/67.790263 points. Full original217/187 runtime restored after221/224 matched6/8 PGO losses. All29 inputs/file sets/Make match scored/current best sources, round225-final-source-match.json. Fresh original C510+30 image references, actual no-argument/no-worker-override59+4 and native/Linux default12/public checks pass. Source-identical221 strict/race/GCC177+30 retained; original A81/D996 immutable proofs remain, no new A/D whole-bank replay. Native executables/images reused, no225 compilation/training claimed. Best/latest/variation separate. Raw ../docs/board-round225-selected-confirmation.json.


230 amount-only bounded8-byte digits:228 native11 rotating full-public hashes show paired0.964362 versus scalar, nativeRSS flat; integer-only0.997675 and both0.981323 are unselected. Use only own fresh A163 decimal.hpp byte-identically and charge it normally. Keep every original sign/start/dot/two-fraction-digit/EOF/country/name/queue behavior,12 workers/compiler flags/PGO. Need fresh direct CSV numeric/full64/guard models, strict/race/untrained integration/GCC/exact-image/default/source proof and actual C K>23.033578 before retention. No target speedup claimed from Mac.


229/c47cf0b run-4edb20dfd38f all five actual gates pass, unchanged225 runtime: T0.063404s/M12406784/S672/K22.594301/67.699946 points. Lower repeats, not new gains; bests separate. Raw ../docs/board-round229-evidence-head.json.


230/f7b2913 run-be2350fd8541 all five real gates pass: T0.065553s/M13078528/S699/K21.858223/66.980742 points. C amount prefix loses21.858223 versus23.033578; source699 versus672 grows, native3.56% screen did not produce supported target totalK gain. Fully restore original C main/Docker/README/Make and remove C decimal.hpp. A/D unchanged lower repeats. Fresh numeric/guard/strict/race/GCC216+50/image630+50/default72+9/source proof stays historical to230, not original scalar model proof. No target phase/cause claim. Raw ../docs/board-round230-amount-prefix.json.
