# Track D optimization log

These are local macOS ARM whole-process measurements including launch, not official scores. Raw runs and source fingerprints are in `../docs/experiments-local.json` and `../docs/experiments-d-full.json`. Scored board run IDs: **not available yet**.

| Experiment | Dataset / workers | Binary-heap median | Radix-heap median | Decision | Board run ID |
| --- | --- | ---: | ---: | --- | --- |
| Monotone integer queue | sample seed 1 / 3 | 0.06862 s | 0.05427 s | Keep for wider validation | Unavailable |
| Independent-seed check | sample seed 19 / 3 | 0.08294 s | 0.05812 s | Keep for wider validation | Unavailable |
| Full public check | full seed 1 / 6 | 1.00991 s | 0.65914 s | Keep; about 34.7% less time | Unavailable |

The hypothesis was that integer distances and monotone extraction could avoid comparison-heap work. Every configuration was warmed, then baseline/candidate order alternated across seven measured runs apiece. Every output matched its reference or the published full-data SHA-256.

For the radix candidate on full public data, three workers had a 0.87391 s median and 198.4 MB maximum process RSS across the measured runs; six had 0.65914 s and 245.6 MB. The default is six, with an environment override retained for board tuning. Native RSS includes mapped pages and is not the official cgroup counter; no official K is inferred from these numbers.

Baseline source is archived under `../tools/experiment-baselines`; the original flag name in those snapshots is translated by the experiment runner. The final source includes only the adopted radix implementation. Extra source-size cost still needs the organizer's formatter/scc measurement. Full public differential checks, independent random graphs, sanitizer checks, and restricted Linux x86-64 container checks verify the adopted candidate. Add real board IDs once the entry is connected.
