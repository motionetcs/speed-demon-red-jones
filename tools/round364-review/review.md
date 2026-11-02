# A364: exact short-key encoding — read-only feasibility

## Decision

The proposed 4..12-byte encoding is algebraically exact, but the measured eligible request traffic is only 3.462%, 1.267% and 1.626% across public/1951/2221. Those are upper bounds on affected cache hits. Existing counters have no length-by-hit joint distribution, so the exact eligible-hit count is unavailable; its defensible lower bound is zero on all three cases. The scope is too small to justify adding a branch/encoding/source and full new proof at this point. Recommend DO NOT IMPLEMENT / READ-ONLY REJECT, with no speed or score claim.

These fractions come from actual request multiplicities in already-validated output group counts, not unique-endpoint lengths. The sum of group counts matches all 3,100,000 observed interner calls in each completed359 diagnostic. Raw inputs and program binaries were not reread/executed. The exact output hashes, source bindings, weighted length histogram and limitations are in traffic-review.json.

## Algebra

For n>=4 the original hash loads uint32 words a at offset0, b at floor((n-4)/2), and c at offset n-4. It computes, in unsigned 32-bit arithmetic:

    x = a XOR rotl(b,11) XOR rotl(c,23) XOR uint32(n)
    q = x * 0x9e3779b1 modulo 2^32
    h = q XOR (q >> 16)

For fixed a, b and n, this maps c bijectively to h. Rotation is a permutation, XOR with fixed words is a permutation, the multiplier is odd and therefore invertible modulo2^32, and the last operation is its own inverse: q=h XOR(h>>16). Consequently, equality of stored a/b, n and ALL32 bits of h proves c equality. This is a lossless encoding of the three loaded words, not a probabilistic hash-only equality shortcut.

For 4<=n<=12, the three 4-byte intervals cover every input byte. The middle starts no later than the end of the first interval, and its end reaches the start of the last interval. Overlap adds redundancy but loses no bytes. At n=13 there is an uncovered byte: the result MUST NOT be used for that length. For example, changing only that gap byte preserves the sampled words and hash while changing the full key.

The cached hash is the original full uint32, not31bits, not only its low bucket-index bits, and not a normalized nonzero hash. Values0,1 and high-bit-set hashes are valid here: only the cached ID UINT16_MAX indicates invalidity. Truncation, sentinel remapping, a changed multiplier or a different hash formula would invalidate this particular proof and require reconsideration.

Equal native uint32 words loaded with memcpy imply equal four-byte representations; endianness does not weaken equality when both keys use the same process representation. Packing a/b into a uint64 must cast before shifting32bits. A new implementation would need a deliberate, defined representation for the long-key pointer payload, preserving its valid pointer round trip on the supported64-bit platforms and never interpreting short-key bits as a pointer.

## Domain and testing limitations

The proposal preserves original FNV behavior and ordinary full-byte fallback for n<4, including empty values, and original pointer/full-byte comparisons for n>12. Keys above UINT16_MAX must keep the existing direct shared-interner fallback. All global full-key hashing/publication/IDs0..4095/overflow rules remain authoritative. Length mismatch and invalid-ID guards must precede any payload interpretation. No source or candidate was prepared in this read-only round.

If reconsidered later, proof would need actual fixed-hash collisions, especially n=12 strings constructed with equal h but different a/b; differing gap bytes at n13; 4/12/13 boundaries; empty/FNV/long paths; format-changing evictions; all full32 hashes; guard pages; and native/GNU/race/publication/current-main/image/default/official checks. A synthetic constant-hash replacement is a different hasher and cannot stand in for this fixed bijection-dependent encoder. Existing169/283 short-comparison proofs do not transfer.

## Duplicate review

No reversible/injective sampled-byte cache encoding was found in the own A PERF and endpoint-cache patches searched. A168 copies canonical bytes outside the private slot; A283 compares first/last blocks while retaining pointer/fingerprint metadata; A297 uses input-relative offsets; A348 changes hashing; A359 changes probe/relocation policy. This proposal instead retains direct mapping and the old hash while changing the payload representation. Distinctness alone does not justify implementation given the traffic result.

No raw requests.log pass, program/profile/compiler/benchmark/model/generator/oracle/image execution, board request, selected runtime, shared documentation or Git change occurred. This is a feasibility decision, not a failed runtime test or an official result.
