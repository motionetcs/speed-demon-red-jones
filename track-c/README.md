# Track C: quote-aware CSV join

Read `/data/records.csv` and `/data/regions.csv`; write only `/out/aggregates.txt`. Local `--data` and `--out` options are supported. No extra runtime dependencies.

The byte parser treats newlines inside quotes as field content, counts doubled quotes as one byte, preserves trailing spaces and empty names, and skips one BOM only at a record boundary. It also handles the grammar's final record without a terminator. Note lengths are counted without materializing the unescaped note. A parallel quote-parity scan finds true record boundaries for each worker, including escaped quotes and newlines inside fields.

A direct region lookup maps IDs to compact country IDs. Unknown regions go to `_UNMATCHED`. Money is signed integer cents throughout; sums and IDs are 64-bit. Formatting handles negative amounts below one unit without negative zero.

Distinct names are interned in a shared flat table with full byte equality. A name key is the raw interior of its CSV field, excluding enclosing quotes. This representation is canonical: encoding a decoded name by doubling every quote is injective; every legal quoted interior has exactly that encoding, and legal unquoted names contain no quote. Thus quoted and unquoted forms of a plain name compare equal, escaped quotes remain distinct correctly, and empty forms compare equal. Decoded byte lengths are counted independently, including one byte per doubled quote. Names are never counted by their encoded lengths.

Every key borrows stable bytes from the immutable mapping. Compact sixteen-byte entries store the full atomic hash plus uint32 input offset and length. Release/acquire publication protects those fields; full string comparison resolves collisions. The offset bound is checked explicitly. A separate atomic bitmap records exact country membership. Only the first thread setting a country's bit increments its local distinct count. Country counts above256 add bitmap words. Table saturation cancels and reparses with a larger table, rather than dropping names.

Work is O(input bytes + records), plus lookup and output sorting. The table starts at131,072 entries and grows; it has no fixed distinct-name cutoff. Worker-local numeric aggregates are reduced after joining. `SPEED_DEMON_THREADS=1` through `12` selects parallelism; twelve is the default.

Build: `clang++ -std=c++20 -O3 -pthread main.cpp -o solution`. The Dockerfile builds independently and offline. Verification covers official grammar/worked cases, generated seeds, exact full public hashes, and sanitizer runs. Numeric fields are parsed while consuming their delimiters, avoiding a second scan. Parallel splitting respects record boundaries inside quotes.

Specification: https://github.com/hackathon-raptors/speed-demon-2026/blob/main/specs/c-join.md

A read-only prefetch of the hashed lookup slot overlaps note/numeric parsing with the upcoming lookup. Key publication still uses acquire/release synchronization. With another24 hours: profile parsing versus lookup misses on Intel and compare further exact layouts on independent seeds; retain only measured total-score gains.

C uses the native-targeted GCC build without PGO. The delimiter-only and C PGO variants did not beat the preceding best board K. Canonical-name tests explicitly mix quoted/unquoted equivalents, escaped quotes, embedded newlines, BOMs, empty names, and exact decoded byte totals.
