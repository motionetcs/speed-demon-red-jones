# Working state

Fresh Red Jones Speed Demon entry. Repository: https://github.com/motionetcs/speed-demon-red-jones ; required branch `speed-demon`. Keep it private until the required source-publication step. Use this repository's implementation and pinned official references; preserve unrelated workspace folders.

## Retained implementation

Retained source commit `07f2ac73092f64d98e40825809e88ce7010dca9f` is pushed and scored on all three tracks. `board-opt-retained-acd.json` confirms every gate passed. All retained build inputs match passed offline GCC15/Linux full-data validation. All algorithms passed new-seed reference/adversarial/sample/full-public checks plus memory/UB and thread sanitizers. Latest/default-only D6 was also rechecked without its environment override.

- A: 12 workers, generic CPU compiler, bounded endpoint search and one-pass latency parsing, disjoint aggregation/scatter, exact rank selection. Best observed K21.482224 /66.603962 points in `run-c70da1f28b23`.
- C: 12 workers, native CPU compiler, quote-aware partitions, direct numeric parser, exact shared lookup and separate membership bitmap. Unescaped names borrow mapped bytes; escaped decoded names use stable worker-owned storage. Best observed K18.492031 /63.349231 points in `run-2f5d6b5da65d`.
- D: 6 query workers, at most 4 loaders, native CPU compiler, two-pass parallel CSR loading, exact bidirectional radix Dijkstra, shared query-owned atomic labels with private exact fallback, lossless six-byte packed edges plus full-weight side table. Best observed K11.670991 /53.355387 points in `run-f813e2d591b2`.

A's six-worker/native compiler tests scored lower; C's full character arena used too much board memory; D's twelve query workers scored lower despite promising Apple ARM timing. Rejected variants and truthful exact run IDs are retained in each `PERF.md`. Do not reintroduce them merely from local timing. Tiny repeated-run score deltas are not claimed as algorithm improvements.

## Board and comparison

Team: https://speeddemon.dev/board/#red-jones-00c4a7 . Public machine-only board, separate from final holdout/judging. Current complete snapshot and computed best-three machine-points comparison: `optimization-current-board.json`, `optimization-comparison.json`. Starting snapshot `optimization-baseline-board.json`: overall computed rank 44/56, machine mean 45.224633. Final snapshot 2026-10-31T04:58:06Z: rank 30/56, machine-points mean 60.833093; leader 78.617098. See `RESULTS.md` for scores and leader gaps.

`python3 tools/watch_board.py --commit <sha> --report docs/<name>.json` waits for exact commit A/C/D records. Wait before another source push; team dispatches have a five-minute minimum interval. `python3 tools/compare_board.py` refreshes complete snapshots and ranks, retrying transient incomplete downloads. It ranks best observed scored records and computes the best-three machine-points geometric mean, not final judge totals.

## Verification and iteration

`make` builds release binaries. `python3 tools/verify.py --tracks acd --scale tiny --seeds <new seeds> --report docs/<name>.json` runs reference/adversarial checks at 1/6/12 workers. Use independent sample seeds and `--public` too. `--binary-dir .build/sanitize` or `.build/tsan` selects sanitizer builds. `python3 tools/container_verify.py --tracks acd --public --report docs/<name>.json` builds offline and checks full hashes in restricted Linux amd64 containers.

All synthetic public inputs in `.data` have published SHA checks. Official pinned revision `ad1f06063a76bf94066f169e133ec0c2e1485b65`; provenance `provenance.json` and `tools/official-revision.txt`. Never bake input-derived answers or graph/name catalogs into the image. Linux GCC15 portability is checked before pushes.

Benchmarks must run sequentially without competing compilers/tests. Apple ARM timings and RSS are candidate-selection evidence only, not board T or cgroup memory. macOS `/usr/bin/time -l` needs execution outside the filesystem sandbox because its sysctl is blocked. Docker/network tests also need the corresponding execution access here. Source fingerprints in historical reports include prose; only build-input hashes must remain identical after documentation edits.

## Registration and remaining event lifecycle

The entrant confirmed individual registration complete; no duplicate was submitted. Fresh team registration was accepted in Brave Work. GitHub App ID 177100099 has read-only code/metadata access to only this repository. User approved that installation and completed email reauthentication. No extra registration details or sign-in are currently needed. Do not store personal registration data in this repository.

Source freeze is November 2, 2026 at 15:00 UTC / 20:30 IST; public-source publication is required within one hour. Do not publish early or schedule anything without authorization. Final holdout and judging results are unavailable. CLI app-installation lookup may return403; the signed-in Brave Work UI verified the saved repository-only grant.

Main reusable prompt is `CODEX_PROMPT.md`, with workspace copy `../HACKATHON_CODEX_PROMPT.md`. Optimization evidence: `OPTIMIZATION.md`, each track's `PERF.md`, and raw `board-opt-*.json` reports. No subagents were used.

The final combined run confirms the source but repeated C/D measurements are lower than their best historical records on identical retained algorithms. Preserve that distinction. Source changes are complete for this optimization round; documentation/report updates do not change executable build inputs. Next useful work is new measured hypotheses, not repeating already-passed tests. No monitoring automation or future publishing action was created.
