# Strategy and competitive research

Initial planning research: 31 October 2026, 03:25 UTC. Current completed setup/results are in SUBMISSION.md and RESULTS.md; the snapshot below predates registration. This is an engineering recommendation, not a prediction of winning.

## Evidence

The official [board JSON](https://s3.amazonaws.com/raptors.dev/speeddemon.dev/2026/board/board.json) snapshot generated at 03:25:34 UTC contains 79 teams. `board-snapshot.json` preserves the response. Red Jones / Afterburner / motionetc did not appear under those names. This does not prove that individual registration is incomplete.

Best K values observed in that snapshot:

| Track | Team | K | Board time | Memory charged | Source lines | Run ID |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| A | Cause Of Death | 51.063272 | 0.019 s | 18,178,048 B | 382 | run-fdf719950a16 |
| B | Kirk Mates | 27.670907 | 0.162416 s | 40,968,192 B | 1,198 | run-d5a0553c478c |
| C | NickTrapp | 34.472167 | 0.030947 s | 12,943,360 B | 415 | run-306df1cddee3 |
| D | Cause Of Death | 28.740511 | 0.123146 s | 67,264,512 B | 441 | run-aec36688eef9 |

These are public practice-board measurements, not final results. They cannot be compared directly with local Apple ARM timings. The feed identifies zero extra runtime dependencies for these runs (`D=1`). Scores do not establish which algorithms an entrant used.

A public GitHub repository search for `speeddemon.dev in:readme` found participant projects. The [Gigatron README](https://github.com/coreyjlord-dev/speed-demon) explicitly describes four zero-dependency C++ tracks. The [Flash README](https://github.com/christian-obi/flash) repeats the starter documentation; it does not establish a distinctive optimized implementation. Only these project overviews were inspected; no participant implementation was copied or used to derive this candidate. No access to private competitor code is claimed.

## Candidate ideas and decisions

| Track | Idea | Main risk | Measurement | Decision and fallback |
| --- | --- | --- | --- | --- |
| A | Intern endpoints; fixed hour buckets; exact integer percentiles | Rank boundaries, timestamp rollover, ordering | Parse vs percentile/output cost; sort vs selection | Implement first. Full sorting is the clear baseline; keep it if selection does not help. |
| C | Quote-aware byte parser; direct region lookup; intern names with exact country membership bits | Escaping, BOM, embedded LF, byte lengths, negative money | Whole-process throughput and memory | Implement second. Exact membership bits avoid millions of separately allocated country/name pairs. |
| D | Compact forward adjacency; Dijkstra with reused workspaces and query workers | Zero edges, direction, duplicate edges, 64-bit sums | Binary vs radix heap; worker count | Implement third. Keep forward Dijkstra as a dependable baseline; bidirectional storage is a later measured tradeoff. |
| B | Query-aware term/position index | ASCII tokenization, left-to-right Boolean expressions, phrase order, large posting lists | End-to-end indexing and query cost | Optional fourth-track hedge. Do after three verified tracks; no incomplete B folder is included. |

The overall title requires at least three tracks and uses the best three track totals. A/C/D deliver broad coverage with manageable implementation risk. C++20 matches the native toolchain and the allowlisted offline GCC image. More elaborate code must earn its source-size cost through measured time or memory improvements.

## Scoring objective

Use the frozen harness's scoring functions. K combines time, memory, source size, and dependencies with exponents 0.50, 0.20, 0.15, and 0.15 respectively; memory improvement is capped at 50 and source/dependency improvements at 1. Speed points are `clamp(50 * log10(K), 0, 100)`. Track total is 65% speed points plus 35% judging. Judge criteria contribute 15% code quality, 12% technique, and 8% optimization log to the total.

Useful experiment estimate, before caps: reducing time by a factor of 2 multiplies K by about 1.414; doubling source size costs a factor of about 0.901. Clear, documented optimizations can be worthwhile even when they add code. Formatting tricks do not remove the organizer's source-size measurement.

## Rules and provenance

The authoritative source is the [frozen specifications and harness](https://github.com/hackathon-raptors/speed-demon-2026), pinned at `ad1f06063a76bf94066f169e133ec0c2e1485b65`; local copies live under `tools/official`. The [current website](https://speeddemon.dev/), [kickstart guide](https://speeddemon.dev/kickstart/), [context](https://speeddemon.dev/speed-demon-context.md), and [image allowlist](https://speeddemon.dev/allowlist.json) were also read. Older promotional listings still describe five tracks and obsolete weights. The board's current feed says one dispatch per 300 seconds; an older clarification/video says 15 minutes. Use current harness/feed behavior and do not flood the queue.

Freeze: **2 November 2026, 15:00 UTC / 8:30 PM IST**. The public-source window ends one hour later, at **9:30 PM IST**. No scheduled publication has been created.

The implementation files here were written fresh during the event using the official specifications. No prior private implementation is included. Actual creation time and the official source revision are recorded in `provenance.json`.
