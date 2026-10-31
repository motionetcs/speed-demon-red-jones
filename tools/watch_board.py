#!/usr/bin/env python3
"""Wait for genuine live-board results for one exact pushed commit."""
import argparse
import datetime
import json
from pathlib import Path
import subprocess
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
URL = "https://s3.amazonaws.com/raptors.dev/speeddemon.dev/2026/board/board.json"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--commit", default="HEAD")
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--tracks", default="acd")
    parser.add_argument("--timeout", type=int, default=900)
    args = parser.parse_args()
    commit = subprocess.check_output(["git", "rev-parse", args.commit], cwd=ROOT, text=True).strip()
    deadline, previous = time.monotonic() + args.timeout, None
    snapshot = ROOT / ".out/board-watch/latest.json"
    snapshot.parent.mkdir(parents=True, exist_ok=True)
    while time.monotonic() < deadline:
        try:
            request = urllib.request.Request(URL + "?v=" + str(time.time_ns()), headers={"User-Agent": "speed-demon-team-watch/1.0", "Cache-Control": "no-cache"})
            with urllib.request.urlopen(request, timeout=25) as response:
                feed = json.load(response)
            team = next((t for t in feed["teams"] if t["team"].strip().casefold() == "red jones"), None)
            state, records = "awaiting registry", {}
            if team:
                snapshot.write_text(json.dumps({"generated_at": feed["generated_at"], "team": team}, indent=2) + "\n")
                for tr in args.tracks:
                    latest = team.get("tracks", {}).get(tr, {}).get("latest")
                    if latest and latest.get("commit") == commit:
                        records[tr] = latest
                flight = team.get("queue", {}).get("in_flight") or {}
                queued = team.get("queue", {}).get("queued") or {}
                state = json.dumps({"head": team.get("watch", {}).get("head"), "watch_error": team.get("watch", {}).get("error"),
                                    "in_flight": flight.get("state"), "track": flight.get("track"),
                                    "queued": queued.get("commit"), "results": {tr: r.get("stage") for tr, r in records.items()}}, sort_keys=True)
                failed = any(r.get("ok") is False for r in records.values())
                passed = len(records) == len(args.tracks) and all(r.get("ok") and r.get("stage") == "scored" and all(r["gates"].values()) for r in records.values())
                if failed or passed:
                    report = {"observed_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                              "feed_generated_at": feed["generated_at"], "source": URL, "commit": commit,
                              "team": team["team"], "slug": team["slug"], "tracks": records, "passed": passed,
                              "scope": "Official public-seed live board; final holdout and judging are separate"}
                    args.report.parent.mkdir(parents=True, exist_ok=True)
                    args.report.write_text(json.dumps(report, indent=2) + "\n")
                    print("SCORED" if passed else "FAILED", json.dumps(records), flush=True)
                    return 0 if passed else 2
            if state != previous:
                print(feed["generated_at"], state, flush=True)
                previous = state
        except (OSError, ValueError, KeyError) as exc:
            print("temporary feed issue:", type(exc).__name__, str(exc)[:160], flush=True)
        time.sleep(15)
    print("timeout waiting for exact commit", commit, flush=True)
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
