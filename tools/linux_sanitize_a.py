#!/usr/bin/env python3
"""Exercise Linux-only A mapping behavior under GCC ASAN/UBSAN, not timing."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import shlex
import subprocess

ROOT = Path(__file__).resolve().parents[1]
IMAGE = 'gcc:15@sha256:eb5e64286ad47187b32bda75c6b6916166ecb41da56559b8b09e0001748d2cce'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--context-root', type=Path, required=True)
    p.add_argument('--source-report', type=Path, action='append', required=True)
    p.add_argument('--report', type=Path, required=True)
    args = p.parse_args()
    context = args.context_root.resolve().relative_to(ROOT)
    cases = {}
    for source in args.source_report:
        data = json.loads(source.read_text())
        assert data['passed']
        for row in data['checks']:
            if row['track'] != 'a':
                continue
            label = row['case']
            folder = ROOT / '.data/cases' / label
            if not folder.is_dir():
                folder = ROOT / '.data/a' / label
            assert folder.is_dir()
            expected = row.get('reference_sha256') or row['runs'][0]['sha256']
            cases[label] = (folder.relative_to(ROOT), expected)
    out = ROOT / '.out/linux-asan-a' / args.report.stem
    out.mkdir(parents=True, exist_ok=True)
    out.chmod(0o777)
    header = '#include <sys/mman.h>\n#ifndef MAP_POPULATE\n#error Linux prefault flag unavailable\n#endif\nstatic_assert((MAP_PRIVATE | MAP_POPULATE) != MAP_PRIVATE);\n'
    cpp = '/repo/' + str(context / 'track-a/main.cpp')
    script = ['set -eu', 'export UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1',
              "cat > /tmp/linux-mapping.hpp <<'HEADER'\n" + header + 'HEADER',
              'g++ -std=c++20 -O1 -g -pthread -fsanitize=address,undefined -include /tmp/linux-mapping.hpp ' + shlex.quote(cpp) + ' -o /tmp/solution']
    jobs = []
    for label, (folder, expected) in cases.items():
        for threads in [1, 6, 12]:
            ident = label + '-t' + str(threads)
            script.append('SPEED_DEMON_THREADS=' + str(threads) + ' /tmp/solution --data ' + shlex.quote('/repo/' + str(folder)) + ' --out ' + shlex.quote('/out/' + ident))
            jobs.append((label, threads, ident, expected))
    command = ['docker', 'run', '--rm', '--platform', 'linux/amd64', '--network=none', '--read-only',
               '--memory=8g', '--memory-swap=8g', '--pids-limit=512', '--cap-drop=ALL',
               '--security-opt=no-new-privileges', '--user', '65534:65534', '--tmpfs', '/tmp:rw,exec,size=1g',
               '-v', str(ROOT) + ':/repo:ro', '-v', str(out) + ':/out:rw', IMAGE, '/bin/sh', '-c', '\n'.join(script)]
    result = subprocess.run(command, capture_output=True, text=True, timeout=600)
    if result.returncode:
        raise RuntimeError(result.stdout + result.stderr)
    rows = []
    for label, threads, ident, expected in jobs:
        folder = out / ident
        assert sorted(p.name for p in folder.iterdir()) == ['summary.txt']
        actual = digest(folder / 'summary.txt')
        assert actual == expected, (label, threads)
        rows.append(dict(track='a', case=label, threads=threads, sha256=actual))
    report = dict(observed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), official_score=False,
                  scope='GCC15/Linux strict ASAN/UBSAN integration; MAP_POPULATE availability asserted; emulated correctness only',
                  image=IMAGE, script=script, checks=rows, diagnostics=result.stderr, passed=True,
                  source_sha256={str(f.relative_to(ROOT)): digest(f) for f in (ROOT / context / 'track-a').iterdir() if f.is_file()})
    args.report.write_text(json.dumps(report, indent=2) + '\n')
    print('PASS GCC15/Linux A ASAN/UBSAN', len(rows), 'exact-output runs', flush=True)


if __name__ == '__main__':
    main()
