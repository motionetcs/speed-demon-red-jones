# Speed Demon — fresh Red Jones entry

Fresh C++20 implementations for Tracks A (request-log aggregation), C (hostile CSV join), and D (directed shortest paths). This project was created during the event from the official specifications. It uses no extra runtime libraries.

All three tracks have real all-gates-passing board records. Historical best scores, exact retained source identities, current leader comparisons and rejected changes are recorded in [current results](docs/RESULTS.md). The leaders remain ahead; final holdout scoring and judging are separate. [Red Jones on the live board](https://speeddemon.dev/board/#red-jones-00c4a7).

The reusable AI execution prompt is [CODEX_PROMPT.md](CODEX_PROMPT.md). The [strategy](docs/STRATEGY.md) contains the ideas, track decisions, current-rule research, and public competitor observations. The [owner briefing](docs/OWNER-BRIEFING.md) explains the techniques in plain language.

## Build and check

```sh
make -j3
make test
make sample
make sanitize
```

The programs accept `--data /path/to/input` and `--out /path/to/output`. Defaults are `/data` and `/out`, as required by the organizers. Each writes only its named output file. Track D accepts `SPEED_DEMON_THREADS=1` through `12`; the current default is twelve workers.

```sh
.build/track-a --data .data/a/sample-seed1 --out .out/manual-a
.build/track-c --data .data/c/sample-seed1 --out .out/manual-c
.build/track-d --data .data/d/sample-seed1 --out .out/manual-d
```

Native development needs C++20, Make, and Python 3.9 or newer. On this machine, collecting macOS process-memory measurements requires execution access to the timing counter; a sandboxed `/usr/bin/time -l` may fail before reporting metrics.

## Full public data and offline Linux validation

```sh
python3 tools/fetch_public.py
python3 tools/verify.py --public --skip-adversarial --report docs/validation-public-full.json
python3 tools/container_verify.py --public --report docs/validation-containers-full.json
```

`fetch_public.py` downloads official data and rejects any input with the wrong published hash. The container tool checks Dockerfile policy, builds each track offline for `linux/amd64`, checks image size, and runs as an unprivileged user with no network and a read-only root. On an Apple ARM host, that architecture is emulated. These checks establish build/output behavior; only the event's own machine establishes official timings and scores.

Official references and generators are pinned under `tools/official`, outside the scored track folders. Temporary data, binaries, and generated output are ignored by Git. Each track folder is independently buildable.

## Read before submitting

See [working state](docs/STATE.md), [submission status](docs/SUBMISSION.md), and each track's `PERF.md`. Reports distinguish observed local validation from completed external steps. No official board run or prize is claimed without evidence.

The [official rules](https://speeddemon.dev/) set freeze at **2 November 2026, 8:30 PM IST (15:00 UTC)** and require public OSI-licensed source within one hour afterward. MIT attribution is preserved in `LICENSE`.

## Final runtime selection

The selected A/C/D runtime is unchanged from the real passing original396 source. The final evidence commit collects results and rejected experiments; it adds no runtime optimization. [Finalization record](docs/FINALIZATION.md) explains source identity, the15:00UTC freeze, the approved publication window and why postcommit board verification is recorded separately. Historical best points and unchanged-source repeats remain separate in [results](docs/RESULTS.md).
