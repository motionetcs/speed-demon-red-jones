# Scored optimization results

Official snapshot: 2026-10-31T07:50:02Z. Public practice-board machine points; final holdout and human judging remain separate.

Best-three machine-point geometric mean: **64.767 → 64.903** this round; rank **32/66** (previously33). Leader Cause Of Death **80.244**. The entry is not in first place.

| Track | Our best points | Leader points | Rank |
| --- | ---: | ---: | ---: |
| A | 70.144504 | 85.792516 (NickTrapp) | 30/79 |
| C | 64.904735 | 80.648576 (NickTrapp) | 31/66 |
| D | 60.051455 | 72.994274 (Cause Of Death) | 22/69 |

## Retained improvement and rejected changes

A line offsets now use lossless16-bit deltas with full32-bit escape positions. Official A best improves **69.704972 → 70.144504**, K24.779894 →25.286579. Cgroup peak **39,796,736 →34,947,072 bytes**; runtime is about unchanged (0.060856 →0.060625 s), while canonical source increases344 →362 lines. Retain this measured K improvement; the small timing difference alone is not called a proven speedup.

C membership reads passed every gate but did not beat the retained best, so they were reverted. The D negative filter also passed every gate but scored59.727060 versus the retained60.051455; reverted. Small-group A selection and D corridor bypasses produced correct checked outputs but were slower locally and never promoted. See per-track PERF.md and round12–15 reports/patches.

## Exact final combination confirmation

Commit `11e467385c4d8869a4afbcc7bb8a80d42ff99e98` passed **check, build, correctness, timeout and sandbox** for all three tracks. The25 current runtime/build/metadata inputs match that exact scored commit in round15-final-source-match.json.

| Track | Confirmation run | Time | Points |
| --- | --- | ---: | ---: |
| A | `run-c26f23dfdc36` | 0.060625 s | 70.144504 |
| C | `run-fb1223f861e9` | 0.091655 s | 64.238285 |
| D | `run-29af6c04ddff` | 0.373223 s | 58.597025 |

C/D runtime inputs match the previously confirmed retained source byte for byte. Their changed repeat values are variation, not algorithm changes; historical best and latest confirmation stay separate.

## Verification and eligibility

A passes fresh sample seeds821/823/827, public full hashes at1/6/12 workers, ASAN/UBSAN, TSAN, reference-checked65534/65535/65536 and larger offset gaps, and48 restricted Linux replays. The exact replay image matches the candidate build report. C/D retain their previously validated exact algorithms, and the real final-combination run passes every gate.

The observable entry audit passes; it is not an organizer-issued eligibility certificate. Registration is entrant-confirmed, app scope is repository-only, AI assistance is disclosed, and no human-understanding attestation is invented.

**Still required:** preserve a final passing branch commit through2 November2026 at15:00 UTC (20:30 IST), and make that MIT source public by16:00 UTC (21:30 IST). Repository remains private; no publication or monitoring automation is scheduled.

## Separate Clicking Devils counters

Saved totals: respect3,123; devils10,371; pumpkins24; cans21 (total13,539). The visible demon is now level18. Reactions do not increase machine points. The clicker leader was observed above3.5 million; no finite maximum is shown and it has not been surpassed. A bulk pumpkin hold was blocked by automatic approval review due to spam/disqualification risk and stopped. See emoji-status.json and emoji-result.jpg.

[Exact board result](board-round15-offsets.json) · [Source identity](round15-final-source-match.json) · [Leader comparison](optimization-comparison.json) · [Entry audit](ENTRY-AUDIT.md) · [Official team board](https://speeddemon.dev/board/#red-jones-00c4a7)
