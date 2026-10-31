# Track C: quote-aware CSV join

Read `/data/records.csv` and `/data/regions.csv`; write only `/out/aggregates.txt`. Local `--data` and `--out` options are supported. No extra runtime dependencies.

The byte parser treats newlines inside quotes as field content, counts doubled quotes as one byte, preserves trailing spaces and empty names, and skips one BOM only at a record boundary. It also handles the grammar's final record without a terminator. Note lengths are counted without materializing the unescaped note. A parallel quote-parity scan finds true record boundaries for each worker, including escaped quotes and newlines inside fields.

A direct region lookup maps IDs to compact country IDs. Unknown regions go to `_UNMATCHED`. Money is signed integer cents throughout; sums and IDs are 64-bit. Formatting handles negative amounts below one unit without negative zero.

Distinct names are interned in a shared flat table using full byte equality. New keys are copied into stable worker-owned storage before atomic release publication; readers acquire that publication before comparing bytes. Each name owns atomic country-membership words. Only the first thread to set a country's bit increments its local distinct count. Hash collisions cannot merge names. Worker-local aggregates are reduced after joining. Table saturation cancels the current attempt and reparses with a larger table, preserving exactness; country groups above 256 use additional membership words.

Expected work is O(input bytes + records), plus hash-table lookup work and sorting output keys. The common table starts at 131,072 slots with four membership words per slot, plus stable names and lookup storage. It grows rather than imposing a distinct-name limit. `SPEED_DEMON_THREADS=1` through `12` selects parallelism; the initial candidate uses 12 workers. Memory estimates are not official cgroup measurements.

Build: `clang++ -std=c++20 -O3 -pthread main.cpp -o solution`. The Dockerfile builds independently and offline. Verification covers official grammar/worked cases, generated seeds, exact full public hashes, and sanitizer runs. Future tuning should profile country/name lookups and parser throughput; parallel splitting must respect record boundaries inside quotes.

Specification: https://github.com/hackathon-raptors/speed-demon-2026/blob/main/specs/c-join.md
