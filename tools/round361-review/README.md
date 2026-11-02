# Round361 compiler feasibility evidence

One unshipped minimal staticIFUNC equality-call probe, two explicit pinnedGNU15.3 compiler/link modes baseline/fno-plt and smokeinvocations. Expected direct PLT call vs FF15 GOT call confirmed. No PGO, timing, source-production correctness, wholeproduction emission or official gain claim. No selected source changes, no source-dependent models repeated.

Primary GCC documentation: https://gcc.gnu.org/onlinedocs/gcc/Code-Gen-Options.html . The option avoids a PLT stub via GOT calls where supported. Actual current-production callshape and target performance must be separately checked; static linking can retain IFUNC stubs for unchanged prebuilt libraries. No vendor or competitor implementation copied.
