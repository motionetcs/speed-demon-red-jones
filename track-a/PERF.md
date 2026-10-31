# Track A optimization log

All numbers here are local macOS ARM development evidence, including process launch, not official scores. Raw runs, hashes, and source fingerprints are in `../docs/experiments-local.json`. Scored board run IDs: **not available yet**.

| Experiment | Dataset | Baseline median | Candidate median | Decision | Board run ID |
| --- | --- | ---: | ---: | --- | --- |
| Exact selection for groups of at least 64 instead of sorting | sample, seed 1 | 0.04432 s | 0.04546 s | Reject; slower | Unavailable |
| Same independent-seed check | sample, seed 19 | 0.04379 s | 0.04924 s | Reject; slower | Unavailable |

Hypothesis: selecting only the required ranks would save comparisons in large groups. Each candidate was warmed once, then baseline/candidate runs alternated for seven measured runs apiece. Every run matched the official reference hash. The extra selection overhead did not pay on either sample, so the final code retains full sorting.

The fresh baseline already uses mapped input, endpoint interning, fixed hour buckets, and integer arithmetic. No earlier measured board baseline is claimed. Full public and container correctness are recorded in `../docs/validation-public-full.json` and `../docs/validation-containers-full.json` when present. Add actual board measurements and IDs after registration/app access; local run names are not substitutes for those IDs.
