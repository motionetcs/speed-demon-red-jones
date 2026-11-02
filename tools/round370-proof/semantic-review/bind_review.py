from pathlib import Path
import datetime
import hashlib
import json

r = Path.cwd()
w = r / '.build/round370-review'
candidate = r / '.build/round370/source'
preflight = r / '.build/round370/preflight.json'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
frozen = json.loads(preflight.read_text())
assert frozen['source_parent'] == '72b55e083ab3251e4687f1e03df32625bccfd6c1'
for relative, digest in frozen['source_sha256'].items():
    assert sha(candidate / relative) == digest, relative
old_path = r / '.build/round363/submitted-source/track-c/main.cpp'
new_path = candidate / 'track-c/main.cpp'
assert sha(old_path) == '8f1703c20ec7e17bb708abff7d7a88945e0dcd8b83acc00b137607a7ceee1b0d'
assert sha(new_path) == '06e04e95334417cb5e969cb19e85381c70e6c3fde4d30241f9e6eec587899d04'
old = old_path.read_text()
new = new_path.read_text()
# Mechanical source comparison only; no parser/model/solution is executed.
replacements = [
    ('struct Field { std::string_view value; size_t bytes; bool escaped; };',
     'struct Field { std::string_view value; size_t bytes; };'),
    ('Field field(std::string& scratch, bool decode)', 'Field field()'),
    ('static_cast<size_t>(p - start), false};', 'static_cast<size_t>(p - start)};'),
    ('        bool escaped = false;\n', ''),
    ('                if (decode) {\n                    if (!escaped) scratch.assign(start, quote - start);\n                    else scratch.append(segment, quote - segment);\n                    scratch.push_back(\'"\');\n                }\n', ''),
    ('                escaped = true;\n', ''),
    ('                if (decode && escaped) scratch.append(segment, quote - segment);\n                std::string_view value = escaped && decode ? std::string_view(scratch)\n                    : std::string_view(start, static_cast<size_t>(quote - start));\n                return {value, bytes, escaped};',
     '                return {{start, static_cast<size_t>(quote - start)}, bytes};'),
    ('Csv tail{quote+2,end};std::string unused;', 'Csv tail{quote+2,end};'),
    ('tail.field(unused,false)', 'tail.field()'),
    ('        std::string scratch;\n', ''),
    ('region_csv.field(scratch, false)', 'region_csv.field()'),
    ('header.field(scratch, true)', 'header.field()'),
    ('Csv csv{boundaries[worker],boundaries[worker+1]};std::string name_scratch,unused;',
     'Csv csv{boundaries[worker],boundaries[worker+1]};'),
    ('csv.field(name_scratch,false)', 'csv.field()'),
    ('csv.field(unused,false)', 'csv.field()'),
    ('if(finished[reader])continue;auto& queue=', 'if(finished[reader])continue;\n                                auto& queue='),
    ('if(!queue.ready.load(std::memory_order_acquire))continue;progress=true;',
     'if(!queue.ready.load(std::memory_order_acquire))continue;\n                                progress=true;'),
]
derived = old
for before, after in replacements:
    assert before in derived, before
    derived = derived.replace(before, after)
assert derived == new
assert new.count('.field()') == 6
assert 'scratch' not in new and 'decode' not in new and '.escaped' not in new
assert old.count('field(scratch, true)') == 1
for relative in frozen['unchanged_C_headers_sha256']:
    assert sha(candidate / relative) == sha(r / '.build/round363/submitted-source' / relative)
patches = [r / f'docs/prototype-patches/{name}' for name in (
    'round237-c-note-count-main.cpp.patch', 'round241-c-format-main.cpp.patch',
    'round300-c-raw-scanner-main.cpp.patch', 'round349-c-field-view-return-main.cpp.patch')]
files = [preflight, old_path, new_path, r / 'tools/official/specs/c-join.md',
         Path(__file__), w / 'review.md', *patches]
report = {
    'observed_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'scope': 'Static source equivalence/edge-case and own-prior-patch review only; no compiler/model/raw-input/solution/benchmark/image/training/generator/oracle/board/selected-source action.',
    'official_score': False,
    'source_parent': frozen['source_parent'],
    'candidate_source_sha256': frozen['source_sha256'],
    'mechanically_enumerated_diff_matches_actual_source': True,
    'field_call_sites': 6,
    'prior_decode_true_call_sites': 1,
    'unchanged_headers_match_original363': True,
    'static_conclusion': 'No semantic counterexample found for actual call sites. Raw record span/count/state transitions unchanged; quote-free header comparison equivalence shown. Not an executed or exhaustive proof, and no performance/official gain claim.',
    'files': [{'path': str(path.relative_to(r)), 'bytes': path.stat().st_size,
               'sha256': sha(path)} for path in files],
}
destination = w / 'binding.json'
assert not destination.exists()
destination.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'path': str(destination), 'sha256': sha(destination),
                  'review_sha256': sha(w / 'review.md'),
                  'script_sha256': sha(Path(__file__))}, indent=2))
