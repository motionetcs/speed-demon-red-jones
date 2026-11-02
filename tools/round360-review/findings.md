# C360: read-only feasibility of a no-PLT compiler trial

No compiler, candidate, image, training workload, benchmark, generator, oracle or board request was run. `inspect.py` only reads the existing original C ELF/disassembly and saved source/image proofs. Its report is static evidence, not a profile.

## Duplicate check

No `-fno-plt` occurrence was found in the searched own A/C/D PERF files, archived prototype patches or tracked tool scripts. A local `git log --all -S'fno-plt'` over all three track Dockerfiles also returned no matching commit. This establishes the scope searched, rather than proving every untracked historical experiment absent.

The separate idea of plain pointer/hash/uint32-length/country 24-byte name events was inspected and rejected before any new implementation: it exactly matches the existing round202 and round263 event24 patches. It must not be rerun as a new design.

## Bound original C evidence

- Image: `sha256:263099fcbeecd9be03c762fc791651c246e2ec2ca2223f5940e186c13645dd63`.
- Existing `.build/c-original-abi/solution` SHA256: `406fe1f9130ba9f98b612caa08f83a75b1299466b4a34ac10d659f928a7ecc83`.
- Existing GNU disassembly SHA256: `0694720ed7e841485d0c0203facba00d4e888aae0c4e5608cf40c31944124321`.
- Prior extraction/tool/source binding: `docs/c-original-field-abi-inspection.json`; current restored C inputs match `docs/round353-final-source-match.json` and the original main hash in that inspection.
- The executable is ELF64/x86-64, static ET_EXEC. It is not claimed to be the organizer's unexposed ELF.

The binary contains 37 IFUNC PLT stubs despite static linking. Each relevant direct E8 call, its target FF25 stub, its RIP-relative GOT address, and its IRELATIVE resolver/symbol mapping were checked against actual ELF bytes. The default narrow worker was selected by its complete non-cold function name, excluding the parallel wrapper and wide/serial outlined functions.

That worker has five direct PLT call sites: memset at 0x40bf69 and bcmp/memcmp at 0x40c118, 0x40c1a1, 0x40c226 and 0x40c2a6. The four comparison sites share the IFUNC stub at 0x4010e8. Four static comparison sites do not mean four calls per input row. No dynamic frequency is measured here.

Seventeen other direct calls include std::_Hash_bytes, NameQueue::send, allocation/growth helpers and __sched_yield. The flag would not eliminate their already-direct call instructions. No existing indirect call instruction was found in this narrow function's disassembly.

## Assessment

There is a concrete call-shape hypothesis for C: a compiler-generated GOT-indirect call could avoid the extra PLT-stub jump for its comparisons. Static linking alone is not a reason to dismiss it. This is a small dispatch change, with no demonstrated cycle cost or meaningful end-to-end gain. Cache behavior, prediction, code layout, builtin lowering and linker relaxation can change the outcome.

The primary GCC manual describes GOT-based calls replacing PLT dispatch, principally for position-independent code, with only some targets also handling position-dependent code. ET_EXEC alone does not identify all compilation defaults or prove the flag will transform this build. An actual pinned-GNU call-shape check is required before spending a full image/training trial on it. The versioned 15.3/15.2 manual URLs were unavailable through the browsing tool; the generic current manual is the primary conceptual reference, not exact-version emitted-code proof.

If a later candidate is authorized, inspect the actual changed hot call sites after compilation. Do not require the whole ELF's PLT section to disappear: the prebuilt static standard-library and libc objects are unaffected by a flag applied only to our translation unit. Keep source, profile workloads and all other flags fixed. A real official K above the retained best would still be required for acceptance.

The original A image's recorded ELF hash is known from round212, but its actual existing production ELF/disassembly was not located in the named local extracts. Other files named gcc/solution are sanitizer or rejected-candidate artifacts and were not mislabeled as production controls. No A/D call-shape or performance claim is made from the C evidence.

Primary reference: [GCC code-generation options](https://gcc.gnu.org/onlinedocs/gcc/Code-Gen-Options.html).
