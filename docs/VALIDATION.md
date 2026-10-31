# Validation evidence

All listed checks completed successfully on 31 October 2026. The local reports are correctness/build checks and development experiments. Actual official live-board evidence is listed separately below; final holdout and judge scores remain unavailable.

| Evidence | What passed |
| --- | --- |
| `validation-tiny.json` | Initial three-seed A/C/D comparisons plus adversarial cases: 32 cases, repeated outputs |
| `validation-sample.json` | Two sample-scale seeds for A/C/D plus adversarial cases: 29 cases |
| `validation-sanitizers.json` | Final adopted source, address/undefined-behavior sanitizers, seeds 3 and 13, official grammar/examples, and 12 random all-pairs graph cases: 29 cases |
| `validation-public-full.json` | All public input hashes verified; full A/C/D outputs match both official references and published hashes; two native runs per track |
| `validation-containers-full.json` | Final offline Linux x86-64 builds, allowlisted digest-pinned images, image-size gate, restricted non-root containers, and full A/C/D output hashes |
| `experiments-local.json` | Seven alternating baseline/candidate runs per sample/worker configuration; exact outputs checked on every run |
| `experiments-d-full.json` | Full-public binary-heap versus radix-heap experiment at one, three, and six workers; seven alternating runs per configuration |
| `first-board-run.json` | Official live board: A/C/D all scored on commit `788ae3b`, passing check/build/correctness/timeout/sandbox gates; actual run IDs, T/M/S/D/K, and machine points retained |

The independent graph oracle is Floyd–Warshall, rather than another copy of our Dijkstra implementation. The CSV grammar checks include embedded UTF-8 bytes, BOMs within quoted data, escaped quotes, CR/LF inside quotes, and EOF without a terminator from the official grammar fixtures. Exact percentile ranks, duplicate requests, timestamp boundaries, empty input, parallel edges, zero weights, and 64-bit distances are covered.

## Full-public outputs

| Track | Output | SHA-256 |
| --- | --- | --- |
| A | summary.txt | `495ca09682b9673ef836a506496177680bb4a3af54255174befddb1f83481cd3` |
| C | aggregates.txt | `d8088b1cd42ba1338b1345b107b55db7b96ef1f5066f3ff64fd26a8912a0f536` |
| D | distances.txt | `a23dbdf0a3e49cc8901310a9ee1dc6a9a569a85297b6da75c2a7002cb2ed277e` |

The published manifest is retained in `public-sha256.json`. Input data and generated output are ignored by Git and can be downloaded/regenerated with the supplied tools. The final container report records image IDs and source fingerprints.

## Limits

The local execution host is Apple ARM. Native timings include process launch; process RSS is not the official cgroup `memory.peak`. x86-64 container validation used emulation. The live-board report supplies actual Intel-box measurements on the public dataset; it is not final holdout scoring or judging. Registration and app access are complete as documented in `SUBMISSION.md`; public-source publication by the required deadline is still a future step.
