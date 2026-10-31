# Working state

This is the fresh Red Jones Speed Demon entry. Read `CODEX_PROMPT.md` for the full execution prompt.

- Completed: current official rules/spec/harness research; live-board snapshot; two public participant README reviews; fresh A/C/D C++20 implementation; native and offline Linux x86-64 builds; differential, adversarial, sample, full-public, and sanitizer validation; local optimization experiments and performance logs.
- Adopted experiment: Track D radix heap, default six workers. Rejected experiment: Track A percentile selection, which was slower on both measured sample seeds.
- Current full-public output hashes match the published manifest for all three tracks, natively and in restricted Linux x86-64 containers. `docs/VALIDATION.md` maps evidence to claims. No official board score has been earned or claimed yet.
- External steps: observe the organizer's registry sync and first scored board runs; public-source publication by the required deadline. Individual registration is entrant-confirmed; fresh team submission and app access are complete.
- Fresh private GitHub destination: https://github.com/motionetcs/speed-demon-red-jones . Required branch: `speed-demon`.
- The validated source was committed and pushed as `a79ef7f`; the remote's privacy and default `speed-demon` branch were verified. Subsequent documentation commits do not change the validated track sources.
- The user approved the exact repository-only installation and completed GitHub email reauthentication. Installed app ID `177100099` now has saved read-only code/metadata access to only `motionetcs/speed-demon-red-jones`, verified in Brave `work`.
- The fresh team form was successfully submitted in Brave Work at approximately 03:55 UTC on 31 October 2026, selecting A/C/D. Tally displayed “Form submitted” and its thank-you page. The entrant confirmed individual registration was already complete; no duplicate individual registration was submitted. Optional personal data was omitted. Do not store personal registration details in this repository.
- CLI app-installation lookup returns 403 because its token is not a GitHub App user token. Use the signed-in Brave Work UI for the grant and verification.
- Use this repository's official references and new implementation files; preserve unrelated workspace folders.
- Official provenance: `docs/provenance.json` and `tools/official-revision.txt`.
- Benchmarks must be sequential. Do not compare Apple ARM timings directly with board timings. Native RSS is not the official cgroup counter.
- macOS `/usr/bin/time -l` requires an unsandboxed execution in this environment because the filesystem sandbox also blocks its `sysctl` call. Initial sandboxed test invocation failed in the timing wrapper; correctness was then rerun with the required execution access.
