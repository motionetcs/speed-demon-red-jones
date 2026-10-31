#!/usr/bin/env python3
"""Download official public A/C/D data and verify SHA-256 before accepting it."""
import concurrent.futures
import hashlib
import json
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://s3.amazonaws.com/raptors.dev/speeddemon.dev/2026/data/"


def fetch(url, destination, expected=None):
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_name(destination.name + ".download")
    h = hashlib.sha256()
    request = urllib.request.Request(url, headers={"User-Agent": "afterburner-validation/1.0"})
    with urllib.request.urlopen(request, timeout=120) as response, temporary.open("wb") as stream:
        for block in iter(lambda: response.read(1 << 20), b""):
            stream.write(block)
            h.update(block)
    if expected is not None and h.hexdigest() != expected:
        temporary.unlink()
        raise RuntimeError("input SHA-256 mismatch: " + url)
    temporary.replace(destination)
    print("verified", destination.relative_to(ROOT), flush=True)


def main():
    manifest_path = ROOT / "docs/public-sha256.json"
    fetch(BASE + "SHA256SUMS.json", manifest_path)
    manifest = json.loads(manifest_path.read_text())
    jobs = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        for tr in "acd":
            for name, expected in manifest["tracks"][tr]["inputs_sha256"].items():
                destination = ROOT / ".data" / tr / "public-full-seed1" / name
                jobs.append(pool.submit(fetch, BASE + "track-" + tr + "/full-seed1/" + name, destination, expected))
        for job in jobs:
            job.result()


if __name__ == "__main__":
    main()
