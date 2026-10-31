#!/usr/bin/env python3
"""Place legal request lines at exact offset-gap boundaries; compare the reference."""
import argparse
import json
from pathlib import Path

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
    first = '2026-10-31T00:00:00.000000Z GET /gap 500 4294967295\n'
    filler = '2026-10-31T01:00:00.000000Z GET /f 200 7\n'
    checks = []
    for gap in [65534, 65535, 65536, 131071, 1048576]:
        count, extra = divmod(gap - len(first), len(filler))
        assert count > 0
        padding = filler * (count - 1) + filler.replace('/f ', '/f' + 'x' * extra + ' ')
        assert len(first + padding) == gap
        # Several escapes separated by short deltas, including a first offset of zero.
        source = (first + padding) * 3 + first
        checks.append(verify.check('a', 'a-line-offset-gap-' + str(gap),
                                   {'requests.log': source}, oracle.run_reference(source)))
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps({'official_score': False,
        'method': 'Legal files with exact 65534/65535/65536 and larger gaps; complete reference-byte comparison at 1/6/12 workers',
        'binary_sha256': verify.digest(verify.BIN_DIR / 'track-a'),
        'checks': checks, 'passed': True}, indent=2) + '\n')


if __name__ == '__main__':
    main()
