from pathlib import Path
import argparse
import datetime
import hashlib
import json
import os
import shlex
import subprocess

r = Path.cwd()
w = r / '.build/round370-other-gnu'
c = r / '.build/round370'
read = lambda p: json.loads(Path(p).read_text())
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
now = lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
def dump(p, value):
    p.write_text(json.dumps(value, indent=2) + '\n')

parser = argparse.ArgumentParser()
parser.add_argument('mode', choices=['prepare', 'run'])
mode = parser.parse_args().mode
pre = read(c / 'preflight.json')
native = read(c / 'native-proof/report.json')
assert native['passed']
assert native['source_sha256'] == pre['source_sha256']
for relative, digest in pre['source_sha256'].items():
    assert sha(c / 'source' / relative) == digest, relative
for name, digest in native['model_files_sha256'].items():
    assert sha(c / name) == digest, name
for relative, digest in pre['root_selected_bindings'].items():
    assert sha(r / relative) == digest, relative

if mode == 'prepare':
    assert not (w / 'plan.json').exists()
    valid, invalid = {}, {}
    origins = []
    def add(row, origin, error=False):
        threads = int(row.get('threads', row.get('requested_threads', 0)))
        if threads not in (1, 6, 12):
            return
        folder = Path(row['data_folder']) if row.get('data_folder') else next(
            folder for folder in (r / '.data/cases' / row['case'], r / '.data/c' / row['case'])
            if folder.is_dir())
        folder = folder if folder.is_absolute() else r / folder
        folder = folder.resolve()
        folder.relative_to(r)
        hashes = {p.name: sha(p) for p in folder.iterdir() if p.is_file()}
        assert set(hashes) == {'records.csv', 'regions.csv'}
        if row.get('inputs_sha256'):
            assert hashes == row['inputs_sha256'], row['case']
        item = {'case': row['case'], 'data_folder': str(folder.relative_to(r)),
                'threads': threads, 'inputs_sha256': hashes, 'reference_source': origin}
        key = (tuple(sorted(hashes.items())), threads)
        if error:
            invalid[key] = item
        else:
            expected = row.get('expected_sha256') or row.get('reference_sha256') or row.get('sha256')
            assert expected
            item['expected_sha256'] = expected
            if key in valid:
                assert valid[key]['expected_sha256'] == expected
            valid[key] = item
    bank_path = c / 'native-proof/asan/matrix.json'
    bank = read(bank_path)
    assert bank['passed']
    origins.append({'path': str(bank_path.relative_to(r)), 'sha256': sha(bank_path),
                    'meaning': 'Only immutable input/reference bytes reused, not its target execution proof'})
    for row in bank['runs']:
        add(row, str(bank_path.relative_to(r)))
    for row in bank['expected_failures']:
        add(row, str(bank_path.relative_to(r)), error=True)
    for suite in native['fresh_suites']:
        path = r / suite['path']
        assert sha(path) == suite['sha256']
        proof = read(path)
        assert proof['passed']
        origins.append({'path': suite['path'], 'sha256': sha(path),
                        'meaning': 'Only source-independent generated input/reference bytes reused'})
        for check in proof['checks']:
            assert check['track'] == 'c'
            for trial in check['runs']:
                add({**check, 'threads': trial['requested_threads']}, suite['path'])
    screen_path = c / 'confirmation/report.json'
    screen = read(screen_path)
    assert screen['passed']
    origins.append({'path': str(screen_path.relative_to(r)), 'sha256': sha(screen_path),
                    'meaning': 'Only saved full input/reference identities reused'})
    for row in screen['cases']:
        for threads in (1, 6, 12):
            add({**row, 'threads': threads}, str(screen_path.relative_to(r)))
    plan = {'created_at_utc': now(), 'official_score': False, 'selected_in_root': False,
            'owner_chat': '01a1957f-561c-7ea2-8a0b-3d39c693e902',
            'scope': 'Only new GNU strict actual370 raw-field/numeric model and actual370 main replay. No new generation/oracle, PGO, production image, benchmarks, root source/docs/Git or board action. Original headers bound byte-for-byte, no new357 queue proof transferred.',
            'preflight_sha256': sha(c / 'preflight.json'),
            'source_sha256': pre['source_sha256'],
            'model_files_sha256': native['model_files_sha256'],
            'numeric_model': {'path': 'tools/test_csv_numeric.cpp', 'sha256': sha(r / 'tools/test_csv_numeric.cpp')},
            'origins': origins, 'runs': list(valid.values()),
            'expected_failures': list(invalid.values()), 'driver_sha256': sha(Path(__file__))}
    dump(w / 'plan.json', plan)
    print(json.dumps({'prepared': True, 'plan_sha256': sha(w / 'plan.json'),
                      'valid_calls': len(valid), 'normal_errors': len(invalid),
                      'no_compiler_or_solution_executed': True}, indent=2))
else:
    plan = read(w / 'plan.json')
    assert plan['driver_sha256'] == sha(Path(__file__))
    assert plan['preflight_sha256'] == sha(c / 'preflight.json')
    assert plan['numeric_model']['sha256'] == sha(r / plan['numeric_model']['path'])
    for origin in plan['origins']:
        assert sha(r / origin['path']) == origin['sha256']
    for row in plan['runs'] + plan['expected_failures']:
        folder = r / row['data_folder']
        assert {p.name: sha(p) for p in folder.iterdir() if p.is_file()} == row['inputs_sha256']
    out = w / 'result'
    assert not out.exists(), 'Never duplicate a launched or completed proof stage'
    out.mkdir(mode=0o777)
    out.chmod(0o777)
    report = {**plan, 'started_at_utc': now(), 'plan_sha256': sha(w / 'plan.json'),
              'status': 'running', 'passed': False}
    dump(out / 'partial.json', report)
    flags = 'g++ -std=c++20 -O3 -g -march=native -Wall -Wextra -Wpedantic -Werror -pthread -fsanitize=address,undefined -fno-sanitize-recover=all -fno-omit-frame-pointer '
    model_header = '/repo/.build/round370/csv_model.hpp'
    script = ['set -eu', 'mkdir -p /out/stdio',
              'export ASAN_OPTIONS=halt_on_error=1',
              'export UBSAN_OPTIONS=halt_on_error=1:print_stacktrace=1',
              'g++ --version >/out/gcc.txt',
              flags + '/repo/.build/round370/source/track-c/main.cpp -o /out/solution',
              'sha256sum /out/solution >/out/solution.sha256',
              flags + '/repo/.build/round370/raw_fields_model.cpp -o /out/raw-fields',
              '/out/raw-fields >/out/raw-fields.out 2>/out/raw-fields.err',
              flags + shlex.quote('-DCSV_MODEL_HEADER="' + model_header + '"') + ' /repo/tools/test_csv_numeric.cpp -o /out/numeric',
              '/out/numeric >/out/numeric.out 2>/out/numeric.err']
    for error, rows in ((False, plan['runs']), (True, plan['expected_failures'])):
        prefix = 'error-' if error else ''
        for n, row in enumerate(rows):
            label = prefix + str(n)
            dest = ('error-' if error else 'valid-') + str(n)
            script += ['set +e', 'SPEED_DEMON_THREADS=' + str(row['threads']) +
                       ' /out/solution --data ' + shlex.quote('/repo/' + row['data_folder']) +
                       ' --out /out/' + dest + ' >/out/stdio/' + label + '.out 2>/out/stdio/' + label + '.err',
                       'code=$?', 'set -e', 'echo "$code" >/out/stdio/' + label + '.code',
                       'test "$code" -eq ' + ('1' if error else '0')]
    script_text = '\n'.join(script) + '\n'
    (out / 'executed.sh').write_text(script_text)
    compiler = 'gcc:15@sha256:eb5e64286ad47187b32bda75c6b6916166ecb41da56559b8b09e0001748d2cce'
    argv = ['docker', 'run', '--rm', '--pull=never', '--platform', 'linux/amd64',
            '--network=none', '--read-only', '--memory=8g', '--memory-swap=8g',
            '--pids-limit=512', '--cap-drop=ALL', '--security-opt=no-new-privileges',
            '--user', '65534:65534', '--tmpfs', '/tmp:rw,exec,size=1g',
            '-i', '--entrypoint', '/bin/sh', '-v', str(r) + ':/repo:ro',
            '-v', str(out) + ':/out:rw', compiler, '-s']
    report.update(argv=argv, strict_flags=flags, executed_script_sha256=sha(out / 'executed.sh'))
    dump(out / 'partial.json', report)
    print('RUN370 GNU current raw-field/numeric/main, under shared exclusive lane', flush=True)
    with (out / 'docker.stdout').open('w') as stdout, (out / 'docker.stderr').open('w') as stderr:
        proc = subprocess.run(argv, input=script_text, text=True, stdout=stdout, stderr=stderr, timeout=1800)
    report['returncode'] = proc.returncode
    dump(out / 'partial.json', report)
    assert proc.returncode == 0, (proc.returncode, (out / 'docker.stderr').read_text()[-3500:])
    assert not (out / 'docker.stderr').read_bytes()
    for name in ('raw-fields', 'numeric'):
        assert (out / (name + '.out')).read_text().startswith('PASS')
        assert not (out / (name + '.err')).read_bytes()
    for error, rows in ((False, plan['runs']), (True, plan['expected_failures'])):
        prefix = 'error-' if error else ''
        for n, row in enumerate(rows):
            label = prefix + str(n)
            assert (out / 'stdio' / (label + '.code')).read_text().strip() == ('1' if error else '0')
            assert not (out / 'stdio' / (label + '.out')).read_bytes()
            stderr = (out / 'stdio' / (label + '.err')).read_text()
            if error:
                assert stderr.startswith('track-c:')
                assert not any(word in stderr for word in ('Sanitizer', 'runtime error:', 'DEADLYSIGNAL'))
                row['stderr'] = stderr
            else:
                assert not stderr
                dest = out / ('valid-' + str(n))
                assert [p.name for p in dest.iterdir()] == ['aggregates.txt']
                row['sha256'] = sha(dest / 'aggregates.txt')
                assert row['sha256'] == row['expected_sha256'], row['case']
    for relative, digest in pre['source_sha256'].items():
        assert sha(c / 'source' / relative) == digest, relative
    for relative, digest in pre['root_selected_bindings'].items():
        assert sha(r / relative) == digest, relative
    for row in plan['runs'] + plan['expected_failures']:
        folder = r / row['data_folder']
        assert {p.name: sha(p) for p in folder.iterdir() if p.is_file()} == row['inputs_sha256']
    report.update(passed=True, status='complete', completed_at_utc=now(),
                  compiler_version=(out / 'gcc.txt').read_text(),
                  compiled_binary_sha256=sha(out / 'solution'),
                  raw_field_model_stdout=(out / 'raw-fields.out').read_text(),
                  numeric_model_stdout=(out / 'numeric.out').read_text())
    dump(out / 'report.json', report)
    print(json.dumps({'passed': True, 'valid_calls': len(plan['runs']),
                      'normal_errors': len(plan['expected_failures']),
                      'compiler_version': report['compiler_version'].splitlines()[0],
                      'report_sha256': sha(out / 'report.json')}, indent=2), flush=True)
