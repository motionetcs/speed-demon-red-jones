# Working state

This is the fresh Red Jones Speed Demon entry. Read `CODEX_PROMPT.md` for the full execution prompt.

- Completed: current official rules/spec/harness research; live-board snapshot; two public participant README reviews; fresh A/C/D C++20 implementation; native and offline Linux x86-64 builds; differential, adversarial, sample, full-public, and sanitizer validation; local optimization experiments and performance logs.
- Original adopted experiment: Track D radix heap. Original serial-layout A percentile selection was rejected on samples; it has since been retested after changing the parallel memory layout.
- Current full-public output hashes match the published manifest for all three tracks, natively and in restricted Linux x86-64 containers. All three tracks also passed the first official live-board run on 31 October 2026 at 03:57 UTC. `docs/first-board-run.json` retains the actual records, and each PERF.md cites its run ID.
- Completed external steps: entrant-confirmed individual registration, successful fresh team submission, repository-only read access for the board app, a push to `speed-demon`, and three real scored board results. Future public-source publication by freeze remains required. Final holdout and judging results are separate and unavailable.
- Fresh private GitHub destination: https://github.com/motionetcs/speed-demon-red-jones . Required branch: `speed-demon`.
- The validated source was committed and pushed as `a79ef7f`; the remote's privacy and default `speed-demon` branch were verified. Subsequent documentation commits do not change the validated track sources.
- The user approved the exact repository-only installation and completed GitHub email reauthentication. Installed app ID `177100099` now has saved read-only code/metadata access to only `motionetcs/speed-demon-red-jones`, verified in Brave `work`.
- The fresh team form was successfully submitted in Brave Work at approximately 03:55 UTC on 31 October 2026, selecting A/C/D. Tally displayed “Form submitted” and its thank-you page. The entrant confirmed individual registration was already complete; no duplicate individual registration was submitted. Optional personal data was omitted. Do not store personal registration details in this repository.
- CLI app-installation lookup returns 403 because its token is not a GitHub App user token. Use the signed-in Brave Work UI for the grant and verification.
- First scored source commit: `788ae3b205928ca2bc3d60100703d5660123d0f0`. A: `run-c76f845b747a`, C: `run-bbda54bf2316`, D: `run-3e323bfac066`. All check/build/correctness/timeout/sandbox gates passed. Team board anchor: https://speeddemon.dev/board/#red-jones-00c4a7 .
- Use this repository's official references and new implementation files; preserve unrelated workspace folders.
- Official provenance: `docs/provenance.json` and `tools/official-revision.txt`.
- Benchmarks must be sequential. Do not compare Apple ARM timings directly with board timings. Native RSS is not the official cgroup counter.
- macOS `/usr/bin/time -l` requires an unsandboxed execution in this environment because the filesystem sandbox also blocks its `sysctl` call. Initial sandboxed test invocation failed in the timing wrapper; correctness was then rerun with the required execution access.

## Active optimization round

The user requested comparison with leaders and continued optimization of A/C/D using real board runs. Baseline and exact reports are in `docs/OPTIMIZATION.md`.

- A twelve-worker parallel aggregation scored `run-ca62e267fa82`: 0.081951 s, K=19.908239, 64.951642 points, all gates passed. Six-worker comparison `run-b768e98565d3`: 0.091654 s, K=19.565079, 64.574080 points; twelve restored based on observed K, with small-difference uncertainty acknowledged.
- C parallel parsing/shared exact names scored `run-a82ca12db6e4`: 0.124259 s, K=16.035293, 60.253844 points, every gate passed.
- Latest pushed commit before the next candidate: `835148746ad0da7f69d93a9f72f80cb710f1b52a`; records `board-opt-c12-a6.json`.
- Next combined candidate: A parallel exact rank selection; C compact name lookup, shared character arena, direct numeric parsing; D parallel one-pass loading, bidirectional radix search, shared query-owned atomic labels with exact fallback, lossless packed edges. All targeted references, adversarial cases, new sample seeds 23/41, full public hashes at 1/6/12, memory/UB and race sanitizers, and offline Linux full-data checks pass. See report families named in OPTIMIZATION.md.
- Do not infer official improvement from local Apple ARM timings. Next step: push this validated candidate, capture its exact-commit board report, and retain/revert by observed K. Then consider a separately tested native-CPU compilation experiment; official harness documentation says native compilation builds on the scoring CPU.
- Board watcher: `python3 tools/watch_board.py --report <path>` checks exact commit identity. Do not push another source revision until its result is captured. Default query/parse workers A12/C12/D6; D graph load at most4.

Checkpoint: combined candidate `072ce9b` scored successfully, records in `board-opt-refined-acd.json`. A now 65.534547 points and D 51.824372; C arena version regressed to 58.301122 despite faster time and must be improved or reverted versus first-parallel 60.253844. Native-CPU Docker-only comparison is fully Linux validated and ready to push; an uncommitted single-line C membership-read fast path is separate and must not enter that commit. Next native candidate is not final until exact board scores arrive.
