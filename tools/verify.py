#!/usr/bin/env python3
"""Differential and independent correctness checks; native timings are local only."""
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import random
import re
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
BIN_DIR = ROOT / ".build"
OFFICIAL = ROOT / "tools/official"
MODULES = {"a": "a_ingest", "c": "c_join", "d": "d_traverse"}
OUTPUTS = {"a": "summary.txt", "c": "aggregates.txt", "d": "distances.txt"}
ACTIVE_TRACKS = set(MODULES)
THREADS = [1, 6, 12]


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load(name):
    spec = importlib.util.spec_from_file_location(name, OFFICIAL / "tests" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def command(args, env=None):
    result = subprocess.run(list(map(str, args)), capture_output=True, env=env, timeout=900)
    if result.returncode:
        raise RuntimeError("command failed: " + repr(args) + "\n" + result.stderr.decode(errors="replace"))
    return result


def execute(track, data, out, threads=6):
    out.mkdir(parents=True, exist_ok=True)
    if any(out.iterdir()):
        for file in out.iterdir():
            if not file.is_file():
                raise RuntimeError("unexpected directory in test output")
            file.unlink()
    env = dict(os.environ, SPEED_DEMON_THREADS=str(threads))
    args = [BIN_DIR / ("track-" + track), "--data", data, "--out", out]
    timer = ["/usr/bin/time", "-l" if sys.platform == "darwin" else "-v"]
    started = time.perf_counter()
    result = command(timer + args, env)
    elapsed = time.perf_counter() - started
    stderr = result.stderr.decode()
    if sys.platform == "darwin":
        match = re.search(r"(\d+)\s+maximum resident set size", stderr)
        rss = int(match.group(1)) if match else None
    else:
        match = re.search(r"Maximum resident set size \(kbytes\):\s*(\d+)", stderr)
        rss = int(match.group(1)) * 1024 if match else None
    if sorted(p.name for p in out.iterdir()) != [OUTPUTS[track]]:
        raise AssertionError("output contract failed: " + str(out))
    return {"wall_seconds_including_launch": elapsed, "peak_process_rss_bytes": rss,
            "requested_threads": threads, "sha256": digest(out / OUTPUTS[track])}


def check(track, label, inputs, expected, repeat=None):
    if track not in ACTIVE_TRACKS:
        return None
    data = ROOT / ".data" / "cases" / label
    data.mkdir(parents=True, exist_ok=True)
    for name, content in inputs.items():
        (data / name).write_bytes(content.encode() if isinstance(content, str) else content)
    expected = expected.encode() if isinstance(expected, str) else expected
    measurements = []
    for run, threads in enumerate(THREADS if repeat is None else THREADS[:repeat]):
        out = ROOT / ".out" / "cases" / label / str(run)
        measurements.append(execute(track, data, out, threads))
        assert (out / OUTPUTS[track]).read_bytes() == expected, label
    print("PASS", label, flush=True)
    return {"track": track, "case": label, "runs": measurements}


def adversarial():
    rows = []
    a, c, d = [load("test_" + tr + suffix) for tr, suffix in [("a", "_ingest"), ("c", "_join"), ("d", "_traverse")]]
    rows.append(check("a", "a-worked", {"requests.log": a.WORKED_INPUT}, a.WORKED_OUTPUT))
    rows.append(check("a", "a-official-edge-cases", {"requests.log": a.edge_input()}, a.EDGE_OUTPUT))
    rows.append(check("a", "a-empty", {"requests.log": b""}, b""))
    latencies = list(range(101))
    source = "".join("2026-11-01T00:59:59.999999Z GET /percentile 500 %d\n" % i for i in reversed(latencies))
    rows.append(check("a", "a-nearest-rank-101", {"requests.log": source},
                      "2026-11-01T00:00:00Z /percentile 101 50 95 99 101 1000000\n"))
    paths = ["/growth/%d/part" % i for i in range(2500)]
    source = "".join("2026-10-31T23:59:59.000000Z GET %s %d %d\n" % (path, 500 if i % 17 == 0 else 499, i)
                     for i, path in enumerate(paths))
    expected = "".join("2026-10-31T23:00:00Z %s 1 %d %d %d %d %d\n" %
                       (path, i, i, i, int(i % 17 == 0), 1000000 if i % 17 == 0 else 0)
                       for path, i in sorted((path, i) for i, path in enumerate(paths)))
    rows.append(check("a", "a-many-endpoints-partitions", {"requests.log": source}, expected))
    rows.append(check("c", "c-worked", {"records.csv": c.WORKED_RECORDS, "regions.csv": c.WORKED_REGIONS}, c.WORKED_OUTPUT))
    for label, records in [("eof", c.RULES_RECORDS), ("bom-eof", c.BOM + c.RULES_RECORDS),
                           ("lf", c.RULES_RECORDS + c.LF), ("crlf", c.RULES_RECORDS + c.CRLF)]:
        rows.append(check("c", "c-grammar-" + label, {"records.csv": records, "regions.csv": c.RULES_REGIONS}, c.RULES_OUTPUT))
    if "c" in ACTIVE_TRACKS:
        import csv
        import io
        stream = io.StringIO(newline="")
        writer = csv.writer(stream, lineterminator="\r\n")
        stream.write("\ufeff")
        writer.writerow(["id", "name", "note", "region_id", "amount"])
        for i in range(120000):
            number, letters = i, []
            for _ in range(4):
                letters.append(chr(97 + number % 26)); number //= 26
            if i and i % 37 == 0:
                stream.write("\ufeff")
            writer.writerow([i + 1, "name" + "".join(letters), 'first,"quoted"\nsecond\ufeff' if i % 13 == 0 else "note", 1, "-0.05" if i % 7 == 0 else "1.25"])
        records = stream.getvalue().encode()
        regions = b"region_id,country\n1,AAA\n"
        rows.append(check("c", "c-parallel-resize-and-seams", {"records.csv": records, "regions.csv": regions}, c.run_reference(records, regions)))
        countries = [chr(65 + i // 676) + chr(65 + i // 26 % 26) + chr(65 + i % 26) for i in range(300)]
        regions = ("region_id,country\n" + "".join("%d,%s\n" % (i + 1, name) for i, name in enumerate(countries))).encode()
        stream = io.StringIO(newline="")
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(["id", "name", "note", "region_id", "amount"])
        for i in range(600):
            writer.writerow([i + 1, 'same "name"', "line\none", i % 300 + 1, "0.00"])
        records = stream.getvalue().encode()
        rows.append(check("c", "c-wide-country-membership", {"records.csv": records, "regions.csv": regions}, c.run_reference(records, regions)))
    rows.append(check("d", "d-worked", {"graph.txt": d.EXAMPLE_GRAPH, "queries.txt": d.EXAMPLE_QUERIES}, d.EXAMPLE_OUTPUT))
    for seed in range(12):
        rng = random.Random(seed)
        n = rng.randrange(2, 28)
        edges = [(rng.randrange(n), rng.randrange(n), rng.choice([0, 1, 17, 4294967295, rng.randrange(1000)]))
                 for _ in range(rng.randrange(0, n * 5))]
        if edges:
            edges += [edges[0], (edges[0][0], edges[0][1], 0)]
        dist = [[None] * n for _ in range(n)]
        for i in range(n):
            dist[i][i] = 0
        for u, v, w in edges:
            dist[u][v] = w if dist[u][v] is None else min(w, dist[u][v])
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    if dist[i][k] is not None and dist[k][j] is not None:
                        candidate = dist[i][k] + dist[k][j]
                        if dist[i][j] is None or candidate < dist[i][j]:
                            dist[i][j] = candidate
        queries = [(i, j) for i in range(n) for j in range(n)] + [(0, 0)]
        graph = "%d %d\n" % (n, len(edges)) + "".join("%d %d %d\n" % e for e in edges)
        text = "".join("%d %d\n" % q for q in queries)
        expected = "".join(str(-1 if dist[i][j] is None else dist[i][j]) + "\n" for i, j in queries)
        rows.append(check("d", "d-floyd-warshall-%d" % seed, {"graph.txt": graph, "queries.txt": text}, expected))
    rows.append(check("d", "d-empty-queries", {"graph.txt": "1 0\n", "queries.txt": ""}, b""))
    if "d" in ACTIVE_TRACKS:
        n = 20000
        weights = [0 if i % 7 == 0 else 4294967295 if i % 31 == 0 else i % 17 for i in range(n - 1)]
        prefix = [0]
        edges = []
        for i, weight in enumerate(weights):
            prefix.append(prefix[-1] + weight)
            edges.append((i, i + 1, weight))
            if weight < 4294967295:
                edges.append((i, i + 1, weight + 1))
        queries = [(0, n - 1), (n - 1, 0)]
        for i in range(24):
            source, target = i * 271, n - 1 - i * 251
            queries.extend([(source, target), (target, source), (source, source)])
        graph = "%d %d\n" % (n, len(edges)) + "".join("%d %d %d\n" % e for e in edges)
        text = "".join("%d %d\n" % q for q in queries)
        expected = "".join(str(prefix[t] - prefix[s] if s <= t else -1) + "\n" for s, t in queries)
        rows.append(check("d", "d-long-chain-reused-workspaces", {"graph.txt": graph, "queries.txt": text}, expected))
    return [row for row in rows if row is not None]


def main():
    global BIN_DIR, ACTIVE_TRACKS, THREADS
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary-dir", type=Path, default=ROOT / ".build")
    parser.add_argument("--scale", choices=["tiny", "sample", "full"], default="tiny")
    parser.add_argument("--seeds", nargs="+", type=int, default=[1, 7, 31])
    parser.add_argument("--tracks", default="acd")
    parser.add_argument("--threads", nargs="+", type=int, default=[1, 6, 12])
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--skip-adversarial", action="store_true")
    parser.add_argument("--public", action="store_true", help="check downloaded public full data against official manifest")
    args = parser.parse_args()
    BIN_DIR = args.binary_dir.resolve()
    ACTIVE_TRACKS, THREADS = set(args.tracks), args.threads
    report = {"created_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "platform": platform.platform(), "python": sys.version,
              "memory_scope": "process RSS, not official cgroup memory.peak", "official_score": False,
              "binary_sha256": {tr: digest(BIN_DIR / ("track-" + tr)) for tr in args.tracks},
              "official_revision": (ROOT / "tools/official-revision.txt").read_text().strip(),
              "source_sha256": {str(p.relative_to(ROOT)): digest(p) for tr in args.tracks
                                for p in sorted((ROOT / ("track-" + tr)).glob("*")) if p.is_file()}, "checks": []}
    if args.public:
        manifest = json.loads((ROOT / "docs/public-sha256.json").read_text())
    for track in args.tracks:
        for seed in ([1] if args.public else args.seeds):
            label = ("public-full-seed1" if args.public else args.scale + "-seed" + str(seed))
            data = ROOT / ".data" / track / label
            data.mkdir(parents=True, exist_ok=True)
            if args.public:
                spec = manifest["tracks"][track]
                for name, expected in spec["inputs_sha256"].items():
                    assert digest(data / name) == expected, name + " input hash mismatch"
            else:
                command([sys.executable, OFFICIAL / "generators" / (MODULES[track] + ".py"),
                         "--seed", seed, "--scale", args.scale, "--out", data])
            ref_out = ROOT / ".out" / track / label / "reference"
            ref_out.mkdir(parents=True, exist_ok=True)
            cached_public = args.public and (ref_out / OUTPUTS[track]).exists() and digest(ref_out / OUTPUTS[track]) in spec["expected_output_sha256"]
            if not cached_public:
                command([sys.executable, OFFICIAL / "reference" / (MODULES[track] + ".py"),
                         "--data", data, "--out", ref_out])
            expected = (ref_out / OUTPUTS[track]).read_bytes()
            ref_hash = hashlib.sha256(expected).hexdigest()
            if args.public:
                assert ref_hash in spec["expected_output_sha256"], "reference/public hash disagreement"
            runs = []
            for run, threads in enumerate(THREADS):
                out = ROOT / ".out" / track / label / ("native-" + str(run))
                measurement = execute(track, data, out, threads)
                assert (out / OUTPUTS[track]).read_bytes() == expected, track + " " + label
                runs.append(measurement)
            report["checks"].append({"track": track, "case": label, "reference_sha256": ref_hash, "runs": runs})
            print("PASS", track, label, ref_hash, flush=True)
    if not args.skip_adversarial:
        report["checks"].extend(adversarial())
    report["passed"] = True
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print("PASS report:", args.report, flush=True)


if __name__ == "__main__":
    main()
