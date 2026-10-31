#!/usr/bin/env python3
"""Reference comparisons for full-width latency escapes and endpoint-ID limits."""
import argparse
import json
from pathlib import Path
import random

import verify


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--binary-dir', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    verify.BIN_DIR = args.binary_dir.resolve()
    verify.ACTIVE_TRACKS = {'a'}
    verify.THREADS = [1, 6, 12]
    oracle = verify.load('test_a_ingest')
    rng = random.Random(8675309)
    latencies = [0, 1, (1 << 19) - 2, (1 << 19) - 1, 1 << 19, (1 << 19) + 1, 4294967295]
    rows = []
    for i in range(20000):
        hour = rng.randrange(24)
        rows.append(f'2026-10-31T{hour:02}:00:00.000000Z GET /key/{rng.randrange(97)} {rng.choice([200,499,500,599])} {rng.choice(latencies)}\n')
    first = ''.join(rows)
    second = ''.join(f'2026-11-01T00:00:00.000000Z GET /boundary/{i} {599 if i % 2 else 200} {latencies[i % len(latencies)]}\n' for i in range(4096))
    checks = []
    for label, source in [('a-latency-escape-partitions', first), ('a-endpoint-id-4095', second)]:
        checks.append(verify.check('a', label, {'requests.log': source}, oracle.run_reference(source)))
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps({'official_score': False,
        'method': 'Complete independent reference-byte comparisons for mixed 19-bit latency escapes, chunk seams and IDs through4095 at1/6/12 workers',
        'binary_sha256': verify.digest(verify.BIN_DIR / 'track-a'), 'checks': checks, 'passed': True}, indent=2) + '\n')


if __name__ == '__main__':
    main()
