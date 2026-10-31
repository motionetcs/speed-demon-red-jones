#!/usr/bin/env python3
"""Independent cross-block, bounded-batch, EOF and cancellation checks."""
import argparse
import json
import os
from pathlib import Path
import random
import subprocess

import verify


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--binary-dir', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--run-id', required=True)
    parser.add_argument('--threads', type=int, nargs='+', default=list(range(1, 13)))
    args = parser.parse_args()
    verify.BIN_DIR = args.binary_dir.resolve()
    verify.ACTIVE_TRACKS = {'d'}
    verify.THREADS = args.threads
    verify.RUN_ID = args.run_id
    ids = [0, 4095, 4096, 8191, 8192, 12288, 16384, 32768, 49152, 65535, 65536, 42]
    pattern = [(i, (i + 1) % 11, [0, 1, 2046, 2047, 65534, 65535, 4294967295][i % 7]) for i in range(11)]
    pattern += [(v, u, w + (w < 4294967295)) for u, v, w in pattern]
    pattern += [(0, 1, 63), (0, 1, 0), (1, 1, 0)]
    checks = []
    inf = 10**30
    for count in [0, 1, 511, 512, 513, 1025, 4097, 65544]:
        edges = [pattern[i % len(pattern)] for i in range(count)]
        random.Random(0x106000 + count).shuffle(edges)
        distance = [[0 if u == v else inf for v in ids] for u in ids]
        for u, v, weight in edges:
            distance[u][v] = min(distance[u][v], weight)
        for k in range(len(ids)):
            for u in range(len(ids)):
                for v in range(len(ids)):
                    distance[u][v] = min(distance[u][v], distance[u][k] + distance[k][v])
        graph = f'65537 {count}\n' + ''.join(f'{ids[u]} {ids[v]} {weight}\n' for u, v, weight in edges)
        if count % 2:
            graph = graph.rstrip('\n')
        pairs = [(u, v) for u in range(len(ids)) for v in range(len(ids))]
        queries = ''.join(f'{ids[u]} {ids[v]}\n' for u, v in pairs)
        expected = ''.join(f'{-1 if distance[u][v] == inf else distance[u][v]}\n' for u, v in pairs)
        checks.append(verify.check('d', 'd-pipeline-spread-batch-' + str(count), {'graph.txt': graph, 'queries.txt': queries}, expected))
    failures = []
    for label, tail, declared in [('number', '0 4096 bad\n', 65545), ('node', '65537 0 1\n', 65545), ('truncated', '0 4096', 65545), ('count', '', 65545)]:
        data = verify.ROOT / '.data/cases' / (args.run_id + '-d-pipeline-error-' + label)
        data.mkdir(parents=True, exist_ok=True)
        prefix = ''.join(f'{ids[u]} {ids[v]} {weight}\n' for u, v, weight in (pattern * 2622)[:65544])
        (data / 'graph.txt').write_text(f'65537 {declared}\n' + prefix + tail)
        (data / 'queries.txt').write_text('0 4096\n')
        for threads in args.threads:
            out = verify.ROOT / '.out/cases' / data.name / str(threads)
            out.mkdir(parents=True, exist_ok=True)
            result = subprocess.run([str(verify.BIN_DIR / 'track-d'), '--data', str(data), '--out', str(out)], capture_output=True, timeout=30,
                                    env=dict(os.environ, SPEED_DEMON_THREADS=str(threads), UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1'))
            stderr = result.stderr.decode(errors='replace')
            assert result.returncode == 1 and stderr.startswith('track-d:'), (label, threads, result.returncode, stderr)
            assert not any(word in stderr for word in ['Sanitizer', 'runtime error:', 'DEADLYSIGNAL']), stderr
            failures.append({'case': label, 'threads': threads, 'returncode': result.returncode, 'stderr': stderr})
    args.report.write_text(json.dumps({'official_score': False, 'scope': 'Independent Floyd reference on sparse65537-node IDs across every block owner, zero/maximum weights, parallel/self edges, serial and bounded512-event seams/large full queues, optional final newline. Malformed streams must cancel promptly and return a normal error with no sanitizer diagnostic.',
                                      'binary_sha256': verify.digest(verify.BIN_DIR / 'track-d'), 'checks': checks, 'malformed': failures, 'passed': True}, indent=2) + '\n')
    print('PASS graph pipeline cross-block/reference/progress/cancellation', flush=True)


if __name__ == '__main__':
    main()
