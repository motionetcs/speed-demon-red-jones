# Track C: quote-aware CSV join

Read `/data/records.csv` and `/data/regions.csv`; write only `/out/aggregates.txt`. Local `--data` and `--out` options are supported. No extra runtime dependencies.

The byte parser treats newlines inside quotes as field content, counts doubled quotes as one byte, preserves trailing spaces and empty names, and skips one BOM only at a record boundary. It also handles the grammar's final record without a terminator. Note lengths are counted without materializing the unescaped note. Names with escapes are decoded; all other names can reference the mapped input.

A direct region lookup maps IDs to compact country IDs. Unknown regions go to `_UNMATCHED`. Money is signed integer cents throughout; sums and IDs are 64-bit. Formatting handles negative amounts below one unit without negative zero.

Distinct names are interned by full byte equality. Each name owns a country-membership bitset, sized from the actual lookup's country count. Setting a previously clear bit increments that country's exact distinct count. Hash collisions still require byte equality and cannot merge names. Escaped names are kept in stable storage so references survive subsequent records.

Expected work is O(input bytes + records), plus hash-table lookup work and sorting a few hundred output keys. Membership storage is O(distinct names * countries/64), roughly 3.2 MB for 100,000 names and four 64-bit words per name, in addition to the lookup, hash table, decoded names, and aggregates. This is an allocation estimate, not an official memory measurement.

Build: `clang++ -std=c++20 -O3 -pthread main.cpp -o solution`. The Dockerfile builds independently and offline. Verification covers official grammar/worked cases, generated seeds, exact full public hashes, and sanitizer runs. Future tuning should profile country/name lookups and parser throughput; parallel splitting must respect record boundaries inside quotes.

Specification: https://github.com/hackathon-raptors/speed-demon-2026/blob/main/specs/c-join.md
