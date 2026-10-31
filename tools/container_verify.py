#!/usr/bin/env python3
"""Offline x86-64 build and sandbox/output validation, not an official timing."""
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = {"a": "summary.txt", "c": "aggregates.txt", "d": "distances.txt"}


def run(args, timeout=600):
    result = subprocess.run(list(map(str, args)), capture_output=True, text=True, timeout=timeout)
    if result.returncode:
        raise RuntimeError("command failed: " + repr(args) + "\n" + result.stdout + result.stderr)
    return result.stdout


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--public", action="store_true")
    parser.add_argument("--context-root", type=Path, default=ROOT)
    parser.add_argument("--skip-build", action="store_true")
    parser.add_argument("--tracks", default="acd")
    parser.add_argument("--threads", type=int, default=12)
    parser.add_argument("--report", type=Path, default=Path("docs/validation-containers.json"))
    args = parser.parse_args()
    spec = importlib.util.spec_from_file_location("official_dockerfile_check", ROOT / "tools/official/harness/dockerfile_check.py")
    policy = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(policy)
    allowlist = json.loads((ROOT / "docs/allowlist.json").read_text())["images"]
    manifest = json.loads((ROOT / "docs/public-sha256.json").read_text()) if args.public else None
    report = {"created_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "official_score": False, "target_platform": "linux/amd64", "runs": [],
              "scope": "offline build, image size, restricted container, exact output; host is Apple ARM, x86-64 is emulated"}
    for tr in args.tracks:
        folder = args.context_root.resolve() / ("track-" + tr)
        problems = policy.check((folder / "Dockerfile").read_text(), allowlist)
        if problems:
            raise RuntimeError("Dockerfile policy: " + repr(problems))
        tag = "speed-demon-fresh/track-" + tr + ":validated"
        build_start = time.perf_counter()
        if not args.skip_build:
            run(["docker", "build", "--platform", "linux/amd64", "--network=none", "-t", tag, folder])
        build_seconds = time.perf_counter() - build_start
        info = json.loads(run(["docker", "image", "inspect", tag]))[0]
        assert info["Architecture"] == "amd64", "wrong image architecture"
        assert info["Size"] <= 2 * 1024**3, "image size exceeds limit"
        label = "public-full-seed1" if args.public else "tiny-seed1"
        data = ROOT / ".data" / tr / label
        if args.public:
            for name, expected in manifest["tracks"][tr]["inputs_sha256"].items():
                assert hashlib.sha256((data / name).read_bytes()).hexdigest() == expected
            expected_hashes = manifest["tracks"][tr]["expected_output_sha256"]
        else:
            reference = ROOT / ".out" / tr / label / "reference" / OUTPUT[tr]
            expected_hashes = [hashlib.sha256(reference.read_bytes()).hexdigest()]
        with tempfile.TemporaryDirectory(prefix="afterburner-container-") as tmp:
            out = Path(tmp) / "out"
            out.mkdir(mode=0o777)
            os.chmod(out, 0o777)
            started = time.perf_counter()
            run(["docker", "run", "--rm", "--platform", "linux/amd64", "--network=none", "--read-only",
                 "--tmpfs", "/tmp:rw,size=1g,exec", "--memory=8g", "--memory-swap=8g", "--pids-limit=512",
                 "--cap-drop=ALL", "--security-opt=no-new-privileges", "--user", "65534:65534",
                 "--ulimit", "nofile=8192:8192", "-e", "TRACK=" + tr, "-e", "SPEED_DEMON_THREADS=" + str(args.threads),
                 "-v", str(data) + ":/data:ro", "-v", str(out) + ":/out:rw", tag])
            wall = time.perf_counter() - started
            assert sorted(p.name for p in out.iterdir()) == [OUTPUT[tr]], "output file contract"
            output_hash = hashlib.sha256((out / OUTPUT[tr]).read_bytes()).hexdigest()
            assert output_hash in expected_hashes, "output hash mismatch"
        report["runs"].append({"track": tr, "case": label, "sha256": output_hash,
                               "image_id": info["Id"], "image_bytes": info["Size"], "build_seconds": build_seconds,
                               "container_wall_seconds_including_startup": wall,
                               "source_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                                 for p in folder.iterdir() if p.is_file()}})
        print("PASS linux/amd64", tr, label, output_hash, flush=True)
    report["passed"] = True
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
