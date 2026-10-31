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
