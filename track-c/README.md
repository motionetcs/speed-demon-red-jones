# Track C: exact quote-aware CSV join

Read `/data/records.csv` and `/data/regions.csv`; write only `/out/aggregates.txt`. Development `--data`/`--out` options are supported. C++20/OS facilities only, no extra runtime libraries. `SPEED_DEMON_THREADS=1` through `12`; default12.

The parser respects commas, escaped quotes and CR/LF within quoted fields, both record terminators, optional final terminators, trailing spaces, empty names and BOMs at record boundaries. Bounded SIMD loads find the next quote inside quoted fields; a scalar tail handles the remaining bytes. Name escapes are decoded exactly into reusable scratch storage. Note lengths are counted without materializing notes. A parallel quote-parity scan finds valid record boundaries. Numeric fields consume delimiters directly. Money is signed integer cents throughout, including negative values below one unit.

Plain three-byte uppercase country codes use an exact26^3 index. Region IDs map to compact country IDs; unknown regions use `_UNMATCHED`. Local sums, extrema, byte totals and counts are reduced after workers join. Output keys are byte-sorted. A country without records produces no line. At most255 countries permit a one-byte region lookup with an unmatched sentinel;256 or more retain the exact two-byte format, selected once before processing.

A shared flat name table stores full atomic hashes and pointers to immutable exact name keys. Full byte equality resolves hash collisions; hashes alone never identify names. Each unique key is copied once into its publishing worker's stable arena. The same allocation holds its length, exactly enough atomic country-membership words, and its decoded name bytes. This improves locality instead of following scattered representative strings into the input mapping and a separate bitmap. Worker-owned64KiB blocks grow as needed; a larger key gets a larger block. Addresses remain stable when the block-pointer vector grows.

The winning thread initializes a complete key, including zero-valued country words, before release publication. Readers acquire that state before reading its pointer, metadata or name. A country's first atomic bit-set increments exactly one worker's distinct count. All other sets of that bit contribute zero. Countries above256 use additional words; no count is approximated. Table saturation cancels and reparses with a larger exact table. Workers join before any arena is released, including cancellation/error paths.

The key length is checked against uint32 capacity and size arithmetic is checked before allocation. Header and country words are aligned; the atomic array is constructed in-place and is trivially destructible. Name bytes preserve UTF-8, trailing spaces, literal quotes, empty values and embedded zero bytes. Decoded byte totals are independent of distinct counting.

Expected work is O(input bytes + records + copied distinct-name bytes), plus table probing and output sorting. Storage is O(table capacity + distinct-key bytes + actual country words). The initial table has131,072 entries and grows. An independently tested larger table saved about3% local time but added2.1MB RSS, so it was not selected.

Build: `clang++ -std=c++20 -O3 -pthread main.cpp -o solution`. The pinned GCC15 Docker build is offline and uses native targeting. Profile training uses independently generated full seed1000003 and sample130363; only the executable enters the runtime image. No dataset, profile, cached answer or input-recognition code enters runtime.

Verification: official references/new seeds, exact published full hashes at1/6/12 workers, quoted seams/EOF, table resizing, more than256 countries, address/UB and race sanitizers, and restricted Linux runs. The independent name-store model covers deliberate full-hash collisions, stable allocation boundaries through1MiB keys, NUL/UTF-8/empty values, country-word boundaries through17,576 countries, and40,000 parallel updates checked against `std::set`. The first real board comparison improves C to64.406855 points with every gate passed. Local timings do not establish board gains; see `PERF.md` and `../docs/round6-*` for the exact candidate evidence and board decision.

With another24 hours: profile the retained layout on Intel, test parsing and lookup changes independently, and retain only higher real K with exact outputs.

Specification: https://github.com/hackathon-raptors/speed-demon-2026/blob/main/specs/c-join.md

The older unquoted-delimiter SIMD scanner scored lower and was rejected. The later quoted-field scanner plus direct country map passed all official gates at65.139069 points/K20.080817, including source cost. These scan different field forms; the rejected helper remains outside the scored folder. See PERF.md for exact source identities, run records and decisions.
