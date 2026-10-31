# Five-minute owner briefing

You can use this to understand and explain the entry. Reading it is not a claim that you have reviewed the code; run the checks and ask about anything unclear.

## What the project does

This hackathon supplies three data-processing problems we are entering. Our programs compute exactly the same answers as the official reference programs, using C++20 and no extra runtime libraries. They do not need an AI API, a database, or a website to run.

## A: request logs

A prepass indexes request lines by full UTC hour, then each worker processes one hour in a small reusable workspace. We keep every latency, including duplicate requests, and calculate exact nearest-rank percentiles. For101 sorted requests, p50 is the51st, p95 the96th and p99 the100th. An HTTP499 is not a server error;500 through599 are. Integer arithmetic makes parts per million exact.

The log is not sorted; every request still reaches its correct hour. Endpoint views refer to the mapped input and complete bytes are compared. We release each completed hour's line offsets and sort output by UTC hour and endpoint. A later two-pass/streaming design saved memory but scored lower and was rejected; the current source is the stronger hour-owned version.

## C: CSV records

A line break inside quotes belongs to a field, so splitting the file on line breaks would be wrong. Our parser follows quoting rules, decodes each doubled quote to one literal quote, preserves trailing spaces, and skips a BOM only at a record boundary. It joins region IDs to country codes; unknown regions are grouped as `_UNMATCHED`.

Money is integer cents: `-0.05` is the integer -5. This makes sums and formatting exact. Every distinct name is stored once in a stable worker-owned block beside a set of country membership bits. The name and its bits share one allocation for cache locality. A bit is either present or absent, so distinct counts are exact without storing millions of separate country/name objects. Full names are compared before sharing a key; hash collisions cannot merge different names. A release/acquire handoff makes the completed key visible before another worker reads it.

## D: directed shortest paths

The retained version builds compact outgoing and incoming edge lists and searches from both ends. Ordinary edges share a four-byte node/weight word; a sentinel retrieves any larger weight exactly. Large node spaces keep the older wider representation. The queue processes small distance bands while retaining every exact distance. An improved label is revisited even within the same band. Conservative lower bounds from the two frontiers tell us when their best meeting path is optimal; the algorithm checks that condition only after a whole batch finishes. This is correct because every edge weight is non-negative, including zero. Edge direction matters, duplicate edges are retained, and distances use 64-bit integers because a path can exceed the largest 32-bit weight.

Workers answer separate queries and write to separate answer slots. The final output keeps the original query order. Reusable workspaces avoid allocating a large map for every query. Each worker now owns compact exact distance maps. Ordinary distances fit in32 bits; larger distances keep a full64-bit fallback. No query writes another worker's labels. The loader uses atomic counters to assign unique CSR slots. Small degree counters recover every wrap in an exact spill map; smaller cursors are used only when the full block interval proves they cannot overflow. Larger blocks retain full32-bit cursors.

## What proof matters

An answer that looks right can still fail. The output file must match the reference byte for byte, including order, spaces, and final newlines. Reports record SHA-256 hashes and repeated comparisons. Small random graphs are also checked with an independent all-pairs algorithm, so we are not relying solely on the official Dijkstra reference.

Local native runs help choose changes, but they are not official scores. The board uses an Intel machine and a container memory counter; our Mac has a different CPU and reports process RSS. The final event score also includes code quality, technique, and the measured optimization log.

## Before the entry is complete

Every member needs individual registration. The team form must point to the correct fresh repository and selected tracks. The board app needs read access to that repository, real scored runs must be checked, and the source must be public under the required licence within the organizer's publication window. A successful local test does not complete those steps.

## What to say about AI and evidence

The code and experiment execution are AI-assisted with Codex. The logs report actual measurements, including rejected changes, rather than a fabricated personal development story. The event permits AI; judges still assess whether the entrant can explain the approach. This briefing prepares an explanation and does not attest that the owner has read or understood it.

The emoji reaction counts feed the separate Clicking Devils leaderboard. Demon level follows machine points, and the crown marks the top three overall. Reactions do not change K or the processing-program score. Our entry is the Red Jones row with three counted tracks; B is blank because we entered A/C/D. Real gate records, K, and machine points verify the program results. The saved emoji counts and screenshot are in emoji-status.json and emoji-result.jpg.
