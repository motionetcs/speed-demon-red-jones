# C308 forced inlining native screen and corrected target hypothesis

One optimized compile and118 exact-output native executions completed. The one-attribute original-header change and two pre-existing main queue-statement newline splits are frozen in `.build/round308`; patches and initial preflight preserve those exact bytes. The driver and compile record here are byte-identical copies. No input/reference generation, training or official run occurred.

The initial hypothesis used an out-of-line GNU `Names::first` symbol with six saved-register pushes. Follow-up read-only call-path inspection showed the ordinary narrow owner path already inlines that body; its sole narrow call is in the cold serial branch, while the other calls belong to the wide country path. This correction is separate from the preserved preflight/raw native measurements in the callsite review. Flat native results plus that correction led to rejection before candidate309 creation or broader compiler/model/PGO/image/default/official proof. No target frequency or causal timing claim follows from static disassembly.

The original passing runtime remains selected. Exact reports: `docs/round308-c-inline-first-screen.json`, `docs/round308-preflight.json`, `docs/round308-c-callsite-review.json`.
