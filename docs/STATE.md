# Working state

This is the fresh Red Jones Speed Demon entry. Read `CODEX_PROMPT.md` for the full execution prompt.

- Completed: current official rules/spec/harness research; live-board snapshot; two public participant README reviews; fresh A/C/D C++20 implementation; native and offline Linux x86-64 builds; differential, adversarial, sample, full-public, and sanitizer validation; local optimization experiments and performance logs.
- Adopted experiment: Track D radix heap, default six workers. Rejected experiment: Track A percentile selection, which was slower on both measured sample seeds.
- Current full-public output hashes match the published manifest for all three tracks, natively and in restricted Linux x86-64 containers. `docs/VALIDATION.md` maps evidence to claims. No official board score has been earned or claimed yet.
- External steps: individual/team registration verification; board-app access for the fresh destination; recorded official runs; public-source publication by the required deadline.
- Fresh private GitHub destination: https://github.com/motionetcs/speed-demon-red-jones . Required branch: `speed-demon`.
- Use this repository's official references and new implementation files; preserve unrelated workspace folders.
- Official provenance: `docs/provenance.json` and `tools/official-revision.txt`.
- Benchmarks must be sequential. Do not compare Apple ARM timings directly with board timings. Native RSS is not the official cgroup counter.
- macOS `/usr/bin/time -l` requires an unsandboxed execution in this environment because the filesystem sandbox also blocks its `sysctl` call. Initial sandboxed test invocation failed in the timing wrapper; correctness was then rerun with the required execution access.
