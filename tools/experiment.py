#!/usr/bin/env python3
"""Build isolated A/D candidates; alternate sequential runs and compare exact bytes."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import shutil
import statistics
import subprocess

import verify

ROOT = verify.ROOT
WORK = ROOT / ".build/experiments"


def build():
    base = WORK / "baseline"
    base.mkdir(parents=True, exist_ok=True)
    for tr in "ad":
        source = (ROOT / "tools/experiment-baselines" / ("track-" + tr + ".cpp")).read_text()
        source = source.replace("AFTERBURNER_THREADS", "SPEED_DEMON_THREADS")
        (base / ("track-" + tr + ".cpp")).write_text(source)
        if tr == "a":
            replacement = """if (values.size() < 64) std::sort(values.begin(), values.end());
                else {
                    size_t first = 0;
                    for (size_t percentile : {50, 95, 99}) {
                        size_t rank = (percentile * values.size() + 99) / 100 - 1;
                        if (rank >= first) {
                            std::nth_element(values.begin() + first, values.begin() + rank, values.end());
                            first = rank + 1;
                        }
                    }
                }"""
            source = source.replace("std::sort(values.begin(), values.end());", replacement)
            variant = "selection"
        else:
            variant = "radix"
            source = '#include "radix_heap.hpp"\n' + source
            source = source.replace("std::vector<Item> heap;", "RadixHeap heap;")
            source = source.replace("            auto greater = std::greater<Item>{};\n", "")
            source = source.replace("heap.emplace_back(0, source);", "heap.push({0, source});")
            source = source.replace("std::pop_heap(heap.begin(), heap.end(), greater);\n                    auto [d, u] = heap.back(); heap.pop_back();", "auto [d, u] = heap.pop();")
            source = source.replace("heap.emplace_back(candidate, edge.to);\n                            std::push_heap(heap.begin(), heap.end(), greater);", "heap.push({candidate, edge.to});")
        folder = WORK / variant
        folder.mkdir(parents=True, exist_ok=True)
        (folder / ("track-" + tr + ".cpp")).write_text(source)
        for location in (base, folder):
            verify.command(["clang++", "-std=c++20", "-O3", "-DNDEBUG", "-pthread", "-I", ROOT / ("track-" + tr),
                            "-I", ROOT / "tools", location / ("track-" + tr + ".cpp"), "-o", location / ("track-" + tr)])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--tracks", default="ad")
    parser.add_argument("--cases", nargs="+", default=["sample-seed1", "sample-seed19"])
    parser.add_argument("--report", type=Path, default=ROOT / "docs/experiments-local.json")
    args = parser.parse_args()
    build()
    report = {"created_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "official_score": False, "hypotheses": {
                  "a": "Exact selection in larger groups reduces comparison work while preserving the three output ranks.",
                  "d": "A monotone integer radix heap reduces priority-queue comparisons at the cost of source size."},
              "method": "warm once; alternate baseline and variant; 7 runs per dataset/configuration; exact output check every run",
              "experiments": []}
    for tr, variant in [("a", "selection"), ("d", "radix")]:
        if tr not in args.tracks:
            continue
        for label in args.cases:
            data = ROOT / ".data" / tr / label
            reference = ROOT / ".out" / tr / label / "reference" / verify.OUTPUTS[tr]
            if reference.exists():
                expected_hashes = [verify.digest(reference)]
            else:
                assert label == "public-full-seed1"
                expected_hashes = json.loads((ROOT / "docs/public-sha256.json").read_text())["tracks"][tr]["expected_output_sha256"]
            for threads in ([1] if tr == "a" else [1, 3, 6]):
                results = {"baseline": [], variant: []}
                for round_number in range(-1, 7):
                    order = ["baseline", variant] if round_number % 2 else [variant, "baseline"]
                    for name in order:
                        verify.BIN_DIR = WORK / name
                        out = ROOT / ".out/experiments" / (tr + "-" + name)
                        run = verify.execute(tr, data, out, threads)
                        assert verify.digest(out / verify.OUTPUTS[tr]) in expected_hashes
                        if round_number >= 0:
                            results[name].append(run)
                summary = {name: {"median_seconds": statistics.median(r["wall_seconds_including_launch"] for r in runs),
                                  "maximum_rss_bytes": max(r["peak_process_rss_bytes"] for r in runs), "runs": runs}
                           for name, runs in results.items()}
                report["experiments"].append({"track": tr, "case": label, "threads": threads, "results": summary})
                print(tr, label, threads, {name: round(result["median_seconds"], 5) for name, result in summary.items()}, flush=True)
    report["source_sha256"] = {str(p.relative_to(ROOT)): verify.digest(p) for p in WORK.glob("*/*.cpp")}
    args.report.write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
