# Track C: quote-aware CSV join

Read `/data/records.csv` and `/data/regions.csv`; write only `/out/aggregates.txt`. Local `--data` and `--out` options are supported. No extra runtime dependencies.

The byte parser treats newlines inside quotes as field content, counts doubled quotes as one byte, preserves trailing spaces and empty names, and skips one BOM only at a record boundary. It also handles the grammar's final record without a terminator. Note lengths are counted without materializing the unescaped note. A parallel quote-parity scan finds true record boundaries for each worker, including escaped quotes and newlines inside fields.

A direct region lookup maps IDs to compact country IDs. Unknown regions go to `_UNMATCHED`. Money is signed integer cents throughout; sums and IDs are 64-bit. Formatting handles negative amounts below one unit without negative zero.

Distinct names are interned in a shared flat table using full byte equality. Ordinary names borrow immutable bytes from the mapped input. Names containing doubled quotes are decoded and copied into stable worker-owned strings before atomic release publication; readers acquire that publication before comparing bytes. Compact sixteen-byte lookup entries store input offsets and lengths separately from atomic country-membership words. Escaped names use a separate stable-pointer array, published with the key; full string equality remains mandatory. Only the first thread to set a country's bit increments its local distinct count. Hash collisions cannot merge names. Worker-local aggregates are reduced after joining. Table saturation cancels the current attempt and reparses with a larger table, preserving exactness; country groups above 256 use additional membership words.

Expected work is O(input bytes + records), plus hash-table lookup work and sorting output keys. The common table starts at 131,072 lookup entries; the separate bitmap has enough words for the actual country count. Only newly interned escaped names require owned strings. It grows rather than imposing a distinct-name limit. `SPEED_DEMON_THREADS=1` through `12` selects parallelism; the default is 12 workers. Memory estimates are not official cgroup measurements.

Build: `clang++ -std=c++20 -O3 -pthread main.cpp -o solution`. The Dockerfile builds independently and offline. Verification covers official grammar/worked cases, generated seeds, exact full public hashes, and sanitizer runs. Numeric fields are parsed while consuming their delimiters, avoiding a second scan. Parallel splitting respects record boundaries inside quotes.

Specification: https://github.com/hackathon-raptors/speed-demon-2026/blob/main/specs/c-join.md

A read-only prefetch of the hashed lookup slot overlaps note/numeric parsing with the upcoming lookup. Key publication still uses acquire/release synchronization. With another24 hours: profile parsing versus lookup misses on Intel and compare further exact layouts on independent seeds; retain only measured total-score gains.

Current experiment isolates profile-guided compilation on the stronger d2 algorithm. The byte-identical official generator trains two independent sample seeds104729/130363 inside an offline builder. Only the executable is copied into the final image; all answers are recomputed at runtime. Prior PGO comparisons also carried rejected allocator/delimiter changes, so they do not establish the effect on this restored algorithm. Real board K decides retention.
