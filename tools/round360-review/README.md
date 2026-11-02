# Round360 compiler feasibility evidence

Read-only original C263 production ELF/disassembly source binding and IFUNCPLT inspection; no compiler/program/profile/training/benchmark/image/board fetch. Four static equality PLT callsites in defaultnarrowworker, not dynamicfrequency/cost. Exact existing ELF/disassembly hashes retained, binaries not tracked. No A/D emittedpath evidence inferred.

Primary GCC documentation: https://gcc.gnu.org/onlinedocs/gcc/Code-Gen-Options.html . The option avoids a PLT stub via GOT calls where supported. Actual current-production callshape and target performance must be separately checked; static linking can retain IFUNC stubs for unchanged prebuilt libraries. No vendor or competitor implementation copied.
