#!/usr/bin/env python3
"""Reproduce track ranks and the best-three machine-points comparison."""
import argparse
import datetime
import json
import math
import time
from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://s3.amazonaws.com/raptors.dev/speeddemon.dev/2026/board/board.json'


def valid_best(track):
    record = (track or {}).get('best') or {}
    return record if record.get('ok') and record.get('stage') == 'scored' else None


def summarize(feed, name):
    teams = feed['teams']
    ours = next(team for team in teams if team['team'].casefold() == name.casefold())
    result = {'generated_at': feed['generated_at'], 'team': ours['team'], 'slug': ours['slug'], 'tracks': {}}
    for track in 'acd':
        entries = [(team['team'], valid_best(team.get('tracks', {}).get(track))) for team in teams]
        entries = [(team, record) for team, record in entries if record]
        entries.sort(key=lambda pair: pair[1]['K'], reverse=True)
        best = valid_best(ours.get('tracks', {}).get(track))
        if not best:
            continue
        leader, record = entries[0]
        result['tracks'][track] = {'best': best, 'latest': ours['tracks'][track].get('latest'),
            'rank': 1 + sum(item['K'] > best['K'] for _, item in entries), 'scored_teams': len(entries),
            'leader': {'team': leader, **record}, 'points_gap_to_leader': record['points'] - best['points']}
    totals = []
    for team in teams:
        points = sorted([record['points'] for track in team.get('tracks', {}).values()
                         if (record := valid_best(track))], reverse=True)
        if len(points) >= 3:
            totals.append((math.prod(points[:3]) ** (1 / 3), team['team']))
    totals.sort(reverse=True)
    score = next((score for score, team in totals if team == ours['team']), None)
    if score is not None:
        result['best_three_machine_points'] = {'geometric_mean': score,
            'rank': 1 + sum(value > score for value, _ in totals), 'eligible_scored_teams': len(totals),
            'leader': {'team': totals[0][1], 'geometric_mean': totals[0][0]}}
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path)
    parser.add_argument('--team', default='Red Jones')
    parser.add_argument('--baseline', type=Path, default=ROOT / 'docs/optimization-baseline-board.json')
    parser.add_argument('--snapshot', type=Path, default=ROOT / 'docs/optimization-current-board.json')
    parser.add_argument('--report', type=Path, default=ROOT / 'docs/optimization-comparison.json')
    args = parser.parse_args()
    if args.input:
        feed = json.loads(args.input.read_text())
    else:
        for attempt in range(4):
            try:
                request = urllib.request.Request(URL + '?v=' + str(time.time_ns()),
                    headers={'Cache-Control': 'no-cache', 'User-Agent': 'speed-demon-team-compare/1.0'})
                with urllib.request.urlopen(request, timeout=25) as response:
                    feed = json.load(response)
                break
            except (OSError, ValueError):
                if attempt == 3:
                    raise
                print('Temporary feed download issue; retrying', flush=True)
                time.sleep(2)
    current, baseline = summarize(feed, args.team), summarize(json.loads(args.baseline.read_text()), args.team)
    report = {'observed_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'source': URL,
              'scope': 'Public practice-board best records; computed machine-points mean, not final holdout or judging totals',
              'current': current, 'baseline': baseline}
    args.snapshot.parent.mkdir(parents=True, exist_ok=True)
    args.snapshot.write_text(json.dumps(feed, indent=2) + '\n')
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + '\n')
    for track, entry in current['tracks'].items():
        old = baseline['tracks'][track]['best']
        print(track.upper(), f"{old['points']:.2f} -> {entry['best']['points']:.2f} points;",
              f"rank {entry['rank']}/{entry['scored_teams']}; leader {entry['leader']['team']} {entry['leader']['points']:.2f}")
    print('Best-three machine comparison:', current.get('best_three_machine_points'))


if __name__ == '__main__':
    main()
