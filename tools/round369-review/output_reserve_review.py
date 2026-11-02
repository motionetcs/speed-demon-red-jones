from pathlib import Path
import collections
import datetime
import hashlib
import json

root = Path.cwd()
work = root / '.build/round369'
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
anchor = root / 'docs/round363-final-source-match.json'
selected = json.loads(anchor.read_text())
assert selected['passed'] and selected['actual_all_gates_passed']
sources = {row['path']: row['sha256'] for row in selected['inputs']
           if row['path'].startswith('track-a/')}
for relative, digest in sources.items():
    assert sha(root / relative) == digest, relative
main = (root / 'track-a/main.cpp').read_text()
assert main.count('out.bytes.reserve(order.size() * 100)') == 1
assert main.count('std::vector<uint16_t> order(paths.size())') == 1
assert main.count('auto& out = writer.hours[hour]') == 1
assert main.count('writer.publish(hour)') == 2
prior = root / '.build/round359/diagnostic/report.json'
diagnostic = json.loads(prior.read_text())
assert diagnostic['passed']
rows = []
for old in diagnostic['runs']:
    path = root / '.build/round359/diagnostic/outputs' / old['case'] / 'summary.txt'
    payload = path.read_bytes()
    digest = hashlib.sha256(payload).hexdigest()
    assert digest == old['output_sha256'] == old['expected_output_sha256']
    assert old['passed'] and payload.endswith(b'\n')
    # Work with raw bytes: UTF-8 code points do not each cost one output byte.
    hours = {}
    global_paths = set()
    groups = 0
    requests = 0
    last = None
    for line in payload.splitlines(keepends=True):
        assert line.endswith(b'\n') and b'\r' not in line
        fields = line[:-1].split(b' ')
        assert len(fields) == 8
        label, endpoint = fields[:2]
        assert len(label) == 20 and label.endswith(b':00:00Z')
        assert last is None or (label, endpoint) > last
        last = (label, endpoint)
        values = [int(value) for value in fields[2:]]
        assert values[0] > 0
        assert all(str(value).encode() == field for value, field in zip(values, fields[2:]))
        hour = hours.setdefault(label, {'output_bytes': 0, 'groups': 0, 'requests': 0})
        hour['output_bytes'] += len(line)
        hour['groups'] += 1
        hour['requests'] += values[0]
        global_paths.add(endpoint)
        groups += 1
        requests += values[0]
    assert sum(hour['output_bytes'] for hour in hours.values()) == len(payload)
    assert requests == old['output_records'] == old['totals']['direct']['calls']
    assert requests == old['totals']['cuckoo']['calls']
    assert 0 < len(global_paths) <= 4096 and len(hours) <= 72
    requested_reserve = len(global_paths) * 100
    per_hour = []
    for label, hour in sorted(hours.items()):
        assert hour['groups'] <= len(global_paths)
        per_hour.append({'hour': label.decode('ascii'), **hour,
                         'requested_reserve_bytes': requested_reserve,
                         'bytes_beyond_requested_reserve': max(0, hour['output_bytes'] - requested_reserve),
                         'fits_requested_reserve': hour['output_bytes'] <= requested_reserve})
    crossing = [hour for hour in per_hour if not hour['fits_requested_reserve']]
    rows.append({'case': old['case'], 'validated_output': str(path.relative_to(root)),
                 'output_sha256': digest, 'output_bytes': len(payload),
                 'groups': groups, 'request_count': requests,
                 'global_distinct_endpoint_count': len(global_paths),
                 'requested_reserve_per_nonempty_hour_bytes': requested_reserve,
                 'nonempty_hours': len(hours), 'empty_hours': 72 - len(hours),
                 'max_hour_bytes': max(hour['output_bytes'] for hour in per_hour),
                 'min_requested_capacity_margin_bytes': min(requested_reserve - hour['output_bytes'] for hour in per_hour),
                 'hours_exceeding_requested_reserve': len(crossing),
                 'hour_details': per_hour,
                 'input_hashes_reused_without_reading_raw_input': old['inputs_sha256']})
crossing = sum(row['hours_exceeding_requested_reserve'] for row in rows)
report = {
    'observed_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'scope': 'GO369 read-only raw-byte accounting of already validated359 output summaries. No input read or solution/compiler/model/generator/oracle/profile/benchmark/board execution.',
    'official_score': False,
    'source_binding': sources,
    'source_anchor': str(anchor.relative_to(root)),
    'source_anchor_sha256': sha(anchor),
    'prior_diagnostic_report': str(prior.relative_to(root)),
    'prior_diagnostic_report_sha256': sha(prior),
    'script_sha256': sha(Path(__file__)),
    'runs': rows,
    'total_hours_exceeding_requested_reserve': crossing,
    'decision': 'REJECT_BEFORE_IMPLEMENTATION_NO_CAPACITY_CROSSING' if crossing == 0 else 'CROSSING_OBSERVED_NOT_PROOF_OF_ACTUAL_REALLOCATION',
    'reasoning': 'Each endpoint in the input has a positive output group in some hour; the union of exact endpoint bytes therefore yields paths.size() and order.size(). Every nonempty hour starts with its own empty Output string, receives reserve(order.size()*100), only appends, and is published once. Standard reserve guarantees capacity at least the request; if final byte size fits that request all intermediate append sizes fit too. Actual capacity can exceed reserve, so crossing the request alone would not prove allocation. Empty hours skip reserve and produce no bytes.',
    'memory_limit': 'Untouched anonymous mmap reserve is virtual capacity, not measured resident or official charged memory. A lower reserve that still fits output cannot establish an RSS gain. No runtime allocation trace, library capacity measurement, copy-cost, RSS, peak overlap, Intel time or official K inference is made.',
    'prior306': 'The archived306 patch changes to numeric Summary arrays, decimal-width exact byte counts, prefix offsets and a second formatting parallel phase into mapped final output. It is broader than reserve-only, but its weak/mixed native result does not establish reserve-growth benefit. This369 gate avoids repeating it.',
}
destination = work / 'output-reserve-review.json'
assert not destination.exists()
destination.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'path': str(destination), 'sha256': sha(destination),
                  'decision': report['decision'],
                  'runs': [{key: row[key] for key in ('case', 'global_distinct_endpoint_count', 'requested_reserve_per_nonempty_hour_bytes', 'nonempty_hours', 'max_hour_bytes', 'min_requested_capacity_margin_bytes', 'hours_exceeding_requested_reserve')} for row in rows]}, indent=2))
