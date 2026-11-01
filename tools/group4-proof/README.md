# Fresh C group4 proof sources

These are byte-identical copies of the files executed for round280. They are test/reference models outside the scored track, and never enter the runtime image. The actual table remains fully in track-c/names.hpp and pays its source cost.

From the repository root, compile with an explicit NAMES_HEADER macro pointing to the absolute track-c/names.hpp path, C++20, pthreads, strict warnings and Address/UndefinedBehaviorSanitizer. Run the resulting test binary; MODEL_FORCE_SCALAR additionally selects the actual generic header branch inside this test unit. The compiler backend remains its physical target. The model runs scalar lane references, protected-page loads, exact membership/arena/index models and every owner topology, and prints a genuine compiler-specific low32 fingerprint pair. Native libc++ and GCC libstdc++ pairs can differ.

The Python fixture helper requires PYTHONPATH=tools and the --binary-dir, --model-report, --run-id and --report arguments shown in the native/Linux reports. Its expected CSV bytes come from the independent official Python oracle. Initial model reference-field compile error and exact formatting/source scopes are recorded separately; no old linear/group8 pass is substituted.
