# A364 extension: 32-byte slot feasibility, no implementation

The saved weighted request-length dictionary gives 4..28-byte coverage of 44.712%, 40.409% and 53.359% for public/1951/2221. These are actual call multiplicities, not unique-key lengths. Exact hit-by-length counts remain absent. Subtracting at most all known direct-cache misses gives loose eligible-hit lower bounds of36.425%,33.320%,46.737%; the corresponding upper bounds are the eligible-call fractions. These bounds are not a joint measurement or timing result.

The proposed array payload doubles from4096*16 to4096*32 bytes per parser: +65,536B each, +786,432B at12. Those are exact slot-array payload sizes, not measured peak/RSS/official M. Over-aligned allocation, pages touched, lifetime overlap and heap reuse/unmapping need actual measurement. No score tradeoff can be decided from the size arithmetic alone.

## Exact representation by length

- n4..7: store complete first/last4-byte words. Their intervals overlap or meet and cover all n bytes. Any unused payload words must have a defined comparison policy; do not compare indeterminate bytes.
- n8..24: store first, middle and last8-byte words, with middle offset floor((n-8)/2). The first reaches the middle and the middle reaches the last throughout that interval. The tuple therefore contains every input byte, with harmless overlap. n=24 is exactly three consecutive8-byte blocks. Equality of all native words and length is full byte equality on any fixed endianness.
- n25..28: store the first24 bytes and retain the exact original full32-bit hash. Equality of the prefix establishes equality of the original a and b words: b is at offsets10..12 and ends no later than16. With equal a/b/n, the original rotate/XOR/odd-multiply/unsigned-XOR-shift hash is bijective in c, as reviewed in review.md. Equal full hashes therefore establish equality of the last4 bytes. Prefix[0,24) plus suffix[n-4,n) covers all bytes for n<=28.
- n29 must use the original full-byte fallback. Its first24 bytes and last4 leave byte24 uncovered. Two n29 values differing only at that byte can share both the prefix and the old sampled hash, so extending the special case would be incorrect.
- Empty and n<4 retain original FNV/full-key behavior; n>28 keeps complete pointer/length/byte equality. Keys above UINT16_MAX retain the original shared-interner fallback. No endpoint catalogue or seed is used, and ID4095/invalid-ID65535 behavior is preserved by design requirements.

For n25..28 all32 hash bits are essential, including0/1/high-bit values. Do not substitute31bits, bucket-index bits, sentinel remapping, a different hasher or multiplier. For n4..24 raw tuple completeness does not depend on hash injectivity, although the original hash can remain a rejection filter. Endianness does not weaken native-word equality; an optimized implementation deriving old4-byte hash words from new8-byte loads would additionally need explicit endian-correct extraction. Merely asserting that a compiler reuses those loads is not evidence of emitted code or cost.

All loads must remain inside their actual string views. A legacy pointer payload must preserve a defined pointer round trip and never reinterpret an encoded short key as a pointer. alignas(32) requires correct standard over-aligned allocation/deallocation; model/test instrumentation must not silently drop aligned-allocation coverage. All new mode transitions and eviction boundaries must be tested if implemented.

## Assessment and next gate

Coverage is materially broader than the rejected16-byte-slot4..12 case. It could justify one separately authorized native screen, but there is no gain established. Larger cache footprint, extra payload loads/branches, code size, allocator effects and performance on the competition's CPU can erase avoided canonical reads or libc calls. The original direct-mapped index and replacement policy should remain fixed so this tests representation alone.

No candidate/header/driver was prepared, no raw input/output files were reread for this extension (only the saved length dictionary), and no compiler/program/profile/model/benchmark/generator/oracle/image/board action occurred. Fresh exact-key/collision/4/7/8/24/25/28/29/long/guard/endian/overalignment/publication/strict/race/main/GNU/image/default/official proof would be required after a supported screen. Existing169/283 comparisons and359 probing proofs do not transfer.
