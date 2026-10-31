# Scored optimization results

Official complete snapshot: 2026-10-31T09:28:41Z. These are public practice-board machine points; final holdout and human judging remain separate.

Best-three machine-point mean: **64.902963 → 66.095609** during this pass. Current rank **32/68**. Overall leader Cause Of Death: **80.505463**. We are not in first place; the gap remains material.

| Track | Starting best | Current best | Rank | Track leader |
| --- | ---: | ---: | ---: | --- |
| A | 70.144504 | 72.105578 | 32/84 | Cause Of Death 86.226860 |
| C | 64.904735 | 66.473216 | 29/71 | NickTrapp 81.521123 |
| D | 60.051455 | 60.242402 | 22/73 | Cause Of Death 72.994274 |

## Retained changes and actual decisions

A parses each request once into exact four-byte records, with a full uint32 escape for large latencies. It uses a shared full-equality endpoint dictionary, allocates only touched hour buckets, releases dictionary metadata after retaining input views, and uses sort cutoff32. Best K rises25.286579 →27.676524. The exact escape, ID and lifetime boundaries are tested; no value is rounded.

C retains exact quoted-field SIMD scanning, a direct uppercase-country map, one-byte region IDs only when at most255 countries fit (otherwise the full two-byte format), and direct XOR quote parity for record splitting. Best K rises19.865280 →21.353266. The higher observations66.040306 and66.473216 are repeats of the same retained code after the parity change; they are not extra algorithm changes.

D retains twelve query workers, sparse exact labels, band64/batch8 queues and the compact loader/edge layout. Best K rises15.886532 →16.026845 in the twelve-worker comparison. Six workers/band32 score lower and are reverted. The later balanced-minimum policy passes all correctness gates but scores59.245827/K15.307933, below retained60.242402/K16.026845; reverted. Direct-array labels, owner-routed/compact-pointer C and other local losers remain outside scored folders. Patches, raw reports and validation limits are preserved honestly.

All decisions use total real K, including charged memory and canonical source. Paired Apple trials screen candidates; background host/browser activity was not fully isolated. Same-source board time and memory also vary. Historical best observations and the latest confirmation are kept separate.

## Exact final combination

Commit `71a023706495a99867f32a3e1856317f0d9e73bb` passes **check, build, correctness, timeout and sandbox** for all A/C/D. All27 current runtime/build/track metadata inputs match that exact scored commit in round32-final-source-match.json. Further changes are documentation/evidence only. No unscored runtime experiment remains.

| Track | Confirmation run | Time | Charged memory | K | Points |
| --- | --- | ---: | ---: | ---: | ---: |
| A | `run-aea59f5857c9` | 0.051652 s | 34,152,448 B | 27.343411 | 71.842634 |
| C | `run-e562a54a2e3f` | 0.077215 s | 11,071,488 B | 21.353266 | 66.473216 |
| D | `run-4dba3dfffd2a` | 0.303599 s | 94,232,576 B | 15.871484 | 60.030877 |

## Verification and entry requirements

A retained source passes fresh929/937 ASAN/UBSAN,941 TSAN, latency escape/ID4095 references, full-public1/6/12-worker hashes,39 exact-image Linux replays and actual default entrypoints. C passes fresh947/953 ASAN/UBSAN,967 TSAN, country widths0/1/254/255/256/257/17576, quoted seams/BOM/EOF/growth cases, full-public hashes,54 exact-image Linux replays and actual defaults. D restores the exact previously sanitized/reference-tested twelve-worker/band64 source, including its independent graph, loader, wide-distance and full-public checks; the final real run confirms every gate. The rejected frontier policy separately passed256 independent graphs/85,871 answers and843 Linux replays before its lower score caused rejection.

The observable entry audit passes; it does not certify organizer eligibility. Registration is entrant-confirmed, the accepted team/app scope is repository-only, MIT attribution is retained, AI assistance is disclosed, and no personal-understanding attestation is invented.

**Still required:** preserve the final passing branch at2 November2026,15:00 UTC /20:30 IST, and make that MIT source public by16:00 UTC /21:30 IST. The repository remains private. Publication and future monitoring are not scheduled.

## Separate emoji target

The user clarified the target is overall #1, rather than the separate clicker leader. The verified row shows respect5,848 /devils13,290 /pumpkins38 /cans37, total19,213; all four exceed observed overall leader Cause Of Death369/75/28/8. The target is met. Reactions do not change machine points; demon level remains18. Intended visible controls were used, and public counts can also grow from other visitors. No finite maximum or overall victory is claimed. Details and proof are in emoji-status.json and emoji-result.jpg.

[Final real run](board-round32-retained-final.json) · [All27 source identities](round32-final-source-match.json) · [Complete leader comparison](round32-final-comparison.json) · [Entry audit](ENTRY-AUDIT.md) · [Official team board](https://speeddemon.dev/board/#red-jones-00c4a7)
