# Five-minute owner briefing

You can use this to understand and explain the entry. Reading it is not a claim that you have reviewed the code; run the checks and ask about anything unclear.

## What the project does

This hackathon supplies three data-processing problems we are entering. Our programs compute exactly the same answers as the official reference programs, using C++20 and no extra runtime libraries. They do not need an AI API, a database, or a website to run.

## A: request logs

Workers parse each request once into a compact four-byte record: endpoint ID, error flag and latency tag. Large latencies use an explicit escape carrying their complete32-bit value; nothing is rounded. The endpoint dictionary compares full names after hashing, so collisions cannot merge names. It assigns IDs only from the current input, with no saved answer catalogue.

A worker then owns one complete hour, counts endpoints and scatters every latency into an exact per-endpoint range. Small ranges are sorted; larger ones use exact nearest-rank selection. For101 requests, p50 is the51st, p95 the96th and p99 the100th sorted value. Duplicate requests count twice. HTTP499 is not a server error;500 through599 are. Parts per million use exact integer arithmetic.

Input need not be sorted. Hour vectors allocate only when they receive records and are released by their hour owner. Endpoint views borrow the immutable input mapping. Output is sorted by UTC hour and endpoint. Earlier two-pass and compressed line-offset versions remain in history; the current fused parser avoids reading the same fields twice.

Each parser also keeps a4096-entry endpoint cache. A small sampled hash chooses a cache slot, but a hit must still match the full length and every byte. A miss uses the original exact shared dictionary. The shared entry publishes the first immutable input view for its assigned ID before making that entry visible. This avoids repeated global lookups without treating a hash collision as equality.

Record vectors now obtain pages directly from the operating system. After an hour is completely processed, its owner returns those pages immediately. This avoids retaining freed record buffers inside another thread's allocator. It changes storage ownership, not any answer. The latest real run uses about22.8% less charged memory; slightly slower execution and more source still give a higher total score.

## C: CSV records

A line break inside quotes belongs to a field, so splitting the file on line breaks would be wrong. Our parser follows quoting rules, counts a doubled quote as one literal byte, preserves trailing spaces, and skips a BOM only at a record boundary. A bounded scanner locates quotes while the parser still checks all quoting rules. It joins region IDs to country codes; unknown regions are grouped as `_UNMATCHED`.

The region lookup uses a smaller format only when all country IDs and the unmatched sentinel fit; larger country sets keep the wider format. Storage changes never change the joined country.

Money is integer cents: `-0.05` is the integer -5. This makes sums and formatting exact. Readers compute ordinary country totals while parsing each record once. Names go in bounded batches to hash-shard owners. At the default twelve workers, eight read and four own name tables. Each connection has one staging and one published batch, at most512 events each. Release/acquire hands the vector to its one consumer; an ordered empty batch finishes that stream. Exceptions cancel the pipeline so workers can exit instead of waiting forever. A one-worker run uses the same exact private name table directly.

Every name goes to one owner, so country membership bits need no shared update. Full key bytes decide equality; collisions cannot merge names. The internal key is the field interior with literal quotes doubled. This encoding is one-to-one: legal unquoted fields contain no quotes, so their bytes already match the same encoding. Quoted `plain` and unquoted `plain` therefore match; quoted-empty and empty also match. Decoded name/note byte lengths are still counted separately. Events borrow the immutable mapped input; each unique key is copied once into the owner's stable block beside its country bits. Each owner-table entry now occupies eight bytes: a32-bit rejection fingerprint and an encoded block/word index. Full length and every byte still decide equality, including hash collisions. Index0 means empty, so hash0/1 do not mean empty. Ordinary64KiB word blocks keep bytes stable, and long keys get dedicated blocks; checked19-bit block/13-bit word offsets prevent index wrap. The full64-bit hash still routes names to owners. Exact country words sit beside each stored name.

Worker partitions begin at proven record ends. A quote that can only close a text field gives a known field boundary; the full parser then advances to a real record terminator. If no safe anchor exists, that boundary becomes EOF. That can make one worker do more work, but it never guesses that a newline inside quotes ends a record.

## D: directed shortest paths

The retained version builds compact outgoing and incoming edge lists and searches from both ends. Ordinary edges share a four-byte node/weight word; a sentinel retrieves any larger weight exactly. Large node spaces keep the older wider representation. The queue processes up to32 entries from a64-distance band while retaining every exact distance. An improved label is revisited even within the same band. Conservative lower bounds from the two frontiers tell us when their best meeting path is optimal; the algorithm checks that condition only after a whole batch finishes. This is correct because every edge weight is non-negative, including zero. Edge direction matters, duplicate edges are retained, and distances use 64-bit integers because a path can exceed the largest 32-bit weight.

Twelve workers answer separate queries and write to separate answer slots. The final output keeps the original query order. Each worker owns forward and backward maps. Common labels use four-byte words: a bucket supplies the low node-ID bits, a tag supplies all remaining bits, and another field stores distance+1. Together the bucket and tag recover the complete ID. Zero means empty. This is exact packing, not an approximate fingerprint. Large IDs, large distances and full buckets use a normal full64-bit fallback. Growth and query resets preserve the same meaning. No query writes another worker's labels.

Up to twelve loaders process bounded sixteen-row scratch batches, prefetching degree counters, cursor addresses and edge locations before using them. Every row and edge is still handled exactly. Atomic counters assign unique CSR slots. Small degree counters recover every wrap in an exact spill map; smaller cursors are used only when the full block interval proves they cannot overflow. Larger blocks retain full32-bit cursors.

The Docker image caps glibc allocation arenas at two for this process. This is a memory-allocation setting inside our program’s container; it does not change the host or scoring harness. Actual run IDs and time/memory tradeoffs are preserved in PERF.md.

## What proof matters

An answer that looks right can still fail. The output file must match the reference byte for byte, including order, spaces, and final newlines. Reports record SHA-256 hashes and repeated comparisons. Small random graphs are also checked with an independent all-pairs algorithm, so we are not relying solely on the official Dijkstra reference.

Local native runs help choose changes, but they are not official scores. The board uses an Intel machine and a container memory counter; our Mac has a different CPU and reports process RSS. The final event score also includes code quality, technique, and the measured optimization log.

## Before the entry is complete

Every member needs individual registration. The team form must point to the correct fresh repository and selected tracks. The board app needs read access to that repository, real scored runs must be checked, and the source must be public under the required licence within the organizer's publication window. A successful local test does not complete those steps.

## What to say about AI and evidence

The code and experiment execution are AI-assisted with Codex. The logs report actual measurements, including rejected changes, rather than a fabricated personal development story. The event permits AI; judges still assess whether the entrant can explain the approach. This briefing prepares an explanation and does not attest that the owner has read or understood it.

The emoji reaction counts feed the separate Clicking Devils leaderboard. Demon level follows machine points, and the crown marks the top three overall. Reactions do not change K or the processing-program score. Our entry is the Red Jones row with three counted tracks; B is blank because we entered A/C/D. Real gate records, K, and machine points verify the program results. The saved emoji counts and screenshot are in emoji-status.json and emoji-result.jpg.
