# Review of a 32-bit owner epoch for the C357 candidate

This is a read-only protocol argument for the C356-shaped pipeline, not a model result, formal verification, or a performance measurement. No production source or test was changed here. It assumes C357 changes only the epoch value type and preserves the exact ordering described below. The argument does not depend on file size, row count, seed, or execution speed.

## Conclusion

I found no counterexample to using an unsigned 32-bit epoch in this specific bounded SPSC protocol. Backpressure and release/acquire ordering bound the number of epoch modifications that can separate the modification observed by an owner snapshot from its idle wait, even if the acquire snapshot is stale. The bound is at most `2 * readers + cancellation_calls`, conservatively at most 37 with 12 readers and 13 cancellation calls. It is far below 2^32. This is not a claim that arbitrary 32-bit event counters are ABA-safe.

## Required protocol facts

- Each owner has one queue per reader; each queue has exactly one producer and that owner as its sole consumer.
- For batch k on a channel, the producer publishes state 1 with release semantics, then increments the owner epoch with a release RMW, then returns from send. It cannot start the next send on that channel before that increment.
- A producer cannot publish its next batch until the owner has retired the previous one to state 0. The owner acquires the published state before accessing rows. Cancellation state 2 is terminal and cannot be overwritten by publication or retirement.
- An owner takes a new acquire epoch snapshot at the beginning of EVERY scan. It waits with that snapshot only after a progress=false scan. Such a scan has consumed/retired no queue. A progress=true scan discards its snapshot and starts another iteration.
- All epoch changes while workers run are release fetch_add operations. No thread resets or stores an arbitrary epoch value. Initialization/wrap-seam setup is before threads in tests only.
- cancel_pipeline is noexcept. Each worker catch can call it once and then rethrows out of that worker; the launch-loop catch can add at most one call before joining. It signals every owner once per invocation. There is no external unbounded cancellation loop or retry that reuses this same owner epoch.

## Stale snapshots and delayed increments

For reader r, name its batch publication P(r,k), subsequent epoch increment E(r,k), the owner's acquire observation A(r,k), and retirement R(r,k).

The previous signal E(r,k-1) is sequenced before the next publication P(r,k). When the owner acquires P(r,k), E(r,k-1) happens before that acquire and therefore before a later owner snapshot. Atomic write/read coherence prevents that snapshot from observing a modification earlier in the epoch modification order than E(r,k-1). This is stronger than merely assuming an acquire load reads the latest value.

Let k be the last batch consumed on that channel before the snapshot. E(r,k) may still be delayed: publication can be consumed before its following increment occurs. One next batch, k+1, may also have been published and signaled after retirement of k. Thus, relative to the modification observed by the snapshot, at most these TWO increments from this reader can remain after it. If the owner has never consumed this channel, backpressure permits only its first publication and signal.

For a snapshot actually used by wait, the intervening scan retired no queue. No reader can advance through further batches without another owner retirement. Delaying a signal does not create an unbounded backlog because send cannot return before signaling, so the same reader cannot enqueue the next signal first. Other owners cannot retire this owner's queues.

Summing over readers gives at most 2*readers publication signals after the snapshot's observed modification. Add the finite worker/launch cancellation signals. This bounds the relevant modification-order distance, not just the wall-clock interval between load and wait. Unsigned wrapping cannot restore the same bit pattern through a full 2^32 cycle in that distance.

## A publication that the queue scan appears to miss

There are two cases. If its signal is later than the snapshot's observed modification, the epoch must differ at the wait check, or a later signal will wake the wait. If its signal is included in that observed modification, acquire ordering must make the preceding publication visible.

In particular, release fetch_add operations form release sequences through subsequent RMWs. An owner acquire that observes another reader's later epoch RMW also synchronizes with earlier release signals in that sequence. It must not read an earlier empty state before a publication that happens before its queue load. It can read a later legitimately retired empty state, in which case that batch has already been consumed. This argument requires the release RMW chain and acquire snapshot to remain intact.

For cancellation, the global flag and terminal queue states are set before owner signaling. An owner either observes cancellation directly, observes a signal whose release sequence orders cancellation before its subsequent checks, or sees a changed epoch at wait. A canceled producer cannot resume arbitrary new publications because state 2 is sticky. Delayed already-published signals and secondary worker catches remain within the finite bound above.

## Checks still needed

New C357 source-bound models should cover UINT32_MAX-1/MAX/0 transitions, publication before snapshot and after each queue scan, publication consumed before its delayed signal, signal before an observed next publication, all readers with one outstanding batch, stale-snapshot ordering arguments, EOF signals, multiple cancellations and launch failure, and actual wait/notify races. A deterministic scheduling model can enumerate a small modular counter with modulus GREATER than the derived bound; a tiny modulus below the bound deliberately admits ABA and must not be used to claim a production counterexample.

Normal strict/race suites and separate plain allocation/pthread-create failures remain necessary, as do pinned GCC, exact-image/default checks and the actual board result. Ordinary tests cannot force every weak-memory stale read or establish exhaustive liveness. Scheduling/library forward progress is assumed; bounded ABA safety does not promise OS fairness.

The GNU15.2 header is primary-source evidence for a possible target advantage, not measured target cost: 4-byte scalar waits use the direct Linux futex path; larger values use a pooled version word, and generic pooled notification wakes all. Verify the actual pinned library macros/path before calling that emitted-code evidence. No implementation from the library is copied into production.

Primary source: https://raw.githubusercontent.com/gcc-mirror/gcc/releases/gcc-15.2.0/libstdc%2B%2B-v3/include/bits/atomic_wait.h
