# Five-minute owner briefing

You can use this to understand and explain the entry. Reading it is not a claim that you have reviewed the code; run the checks and ask about anything unclear.

## What the project does

This hackathon supplies three data-processing problems we are entering. Our programs compute exactly the same answers as the official reference programs, using C++20 and no extra runtime libraries. They do not need an AI API, a database, or a website to run.

## A: request logs

A prepass indexes request lines by UTC hour, then each worker processes one hour in a small reusable workspace. We group each HTTP request by its UTC hour and endpoint. We keep every latency, including duplicate requests, and calculate exact percentiles. For 101 sorted requests, p50 is the 51st value, p95 the 96th, and p99 the 100th. An HTTP 499 is not a server error; 500 through 599 are. Integer arithmetic prevents rounding differences in the reported error rate.

The log is not sorted. We keep all the hour buckets until the input is finished, so a late request still reaches the correct group. Output is sorted by hour and then endpoint bytes.

## C: CSV records

A line break inside quotes belongs to a field, so splitting the file on line breaks would be wrong. Our parser follows quoting rules, turns a doubled quote into one literal quote, preserves trailing spaces, and skips a BOM only at a record boundary. It joins region IDs to country codes; unknown regions are grouped as `_UNMATCHED`.

Money is integer cents: `-0.05` is the integer -5. This makes sums and formatting exact. Every distinct name gets an ID and a set of country membership bits. A bit is either present or absent, so distinct counts are exact without storing millions of separate country/name objects. Full names are compared before sharing an ID; hash collisions cannot merge different names.

## D: directed shortest paths

The retained version builds compact outgoing and incoming edge lists and searches from both ends. Dijkstra's algorithm explores the cheapest reachable distance first. A lower bound from the two frontiers tells us when their best meeting path is optimal. This is correct because every edge weight is non-negative, including zero. Edge direction matters, duplicate edges are retained, and distances use 64-bit integers because a path can exceed the largest 32-bit weight.

Workers answer separate queries and write to separate answer slots. The final output keeps the original query order. Reusable workspaces avoid allocating a large map for every query. Query tokens own shared primary cells; overlapping queries and large distances use private exact fallback, so workers cannot overwrite one another's results.

## What proof matters

An answer that looks right can still fail. The output file must match the reference byte for byte, including order, spaces, and final newlines. Reports record SHA-256 hashes and repeated comparisons. Small random graphs are also checked with an independent all-pairs algorithm, so we are not relying solely on the official Dijkstra reference.

Local native runs help choose changes, but they are not official scores. The board uses an Intel machine and a container memory counter; our Mac has a different CPU and reports process RSS. The final event score also includes code quality, technique, and the measured optimization log.

## Before the entry is complete

Every member needs individual registration. The team form must point to the correct fresh repository and selected tracks. The board app needs read access to that repository, real scored runs must be checked, and the source must be public under the required licence within the organizer's publication window. A successful local test does not complete those steps.

## What to say about AI and evidence

The code and experiment execution are AI-assisted with Codex. The logs report actual measurements, including rejected changes, rather than a fabricated personal development story. The event permits AI; judges still assess whether the entrant can explain the approach. This briefing prepares an explanation and does not attest that the owner has read or understood it.

The pumpkins, flames, reactions, and demon level on the board are presentation features. Our entry is the Red Jones row with three counted tracks. A blank B column is expected because we entered A/C/D. Real gate records, K, and machine points are the evidence that matters.
