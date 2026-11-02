from pathlib import Path
import datetime
import hashlib
import json
import re

r = Path.cwd()
w = r / '.build/round376-review'
c = r / '.build/round376'
base = r / '.build/round371/submitted-source'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
preflight = c / 'preflight.json'
pre = json.loads(preflight.read_text())
assert pre['source_parent'] == '83630432c7acd216b9813027a2e863fe0fd8aaee'
for relative, digest in pre['source_sha256'].items():
    assert sha(c / 'source' / relative) == digest, relative
assert sha(base / 'track-a/main.cpp') == '02661f93bc65fc35d359c80e19d82578968ab68725e8b325e48c630c3e27310c'
assert sha(c / 'source/track-a/main.cpp') == '7c815fe835a41a7d82dedd5b55dd14136b34ee957e35b14c14688a3a6c2826ff'

def apply_recorded_patch(before, patch):
    # Pure source-text reconstruction; no solution or scheduler model executes.
    source = before.splitlines(keepends=True)
    lines = patch.splitlines(keepends=True)
    assert lines[0].startswith('--- ') and lines[1].startswith('+++ ')
    result = []
    position = 0
    i = 2
    while i < len(lines):
        match = re.fullmatch(r'@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@[^\n]*\n?', lines[i])
        assert match, lines[i]
        old_start = int(match[1]) - 1
        old_count = int(match[2]) if match[2] is not None else 1
        new_start = int(match[3]) - 1
        new_count = int(match[4]) if match[4] is not None else 1
        assert position <= old_start
        result.extend(source[position:old_start])
        position = old_start
        assert len(result) == new_start
        consumed = produced = 0
        i += 1
        while i < len(lines) and not lines[i].startswith('@@ '):
            line = lines[i]
            assert line[0] in ' +-'
            if line[0] in ' -':
                assert source[position] == line[1:]
                position += 1
                consumed += 1
            if line[0] in ' +':
                result.append(line[1:])
                produced += 1
            i += 1
        assert (consumed, produced) == (old_count, new_count)
    result.extend(source[position:])
    return ''.join(result)

patch_bindings = []
for name in ('main.cpp', 'README.md'):
    original = base / 'track-a' / name
    patch = c / (name + '.patch')
    actual = c / 'source/track-a' / name
    assert apply_recorded_patch(original.read_text(), patch.read_text()) == actual.read_text()
    patch_bindings.append({'path': str(patch.relative_to(r)), 'sha256': sha(patch),
                           'reconstructs': str(actual.relative_to(r)),
                           'original_sha256': sha(original), 'candidate_sha256': sha(actual)})
unchanged = {}
for relative in pre['source_sha256']:
    if relative not in ('track-a/main.cpp', 'track-a/README.md', 'track-a/PERF.md'):
        assert sha(c / 'source' / relative) == sha(base / relative), relative
        unchanged[relative] = sha(base / relative)
old = (base / 'track-a/main.cpp').read_text()
new = (c / 'source/track-a/main.cpp').read_text()
old_tail = old[old.index('        std::vector<std::string_view> paths('):]
new_tail = new[new.index('        std::vector<std::string_view> paths('):]
assert old_tail == new_tail
marker_start = '                if (limit - p < 28)'
marker_end = '                if (latency >= latency_escape) chunk.wide[hour].push_back(static_cast<uint32_t>(latency));'
def parser_body(text):
    return text[text.index(marker_start):text.index(marker_end) + len(marker_end)]
assert parser_body(old) == parser_body(new)
assert 'constexpr size_t parse_block_bytes = size_t(1) << 22;' in new
assert new.count('next_part.fetch_add(1, std::memory_order_relaxed)') == 1
files = [preflight, base / 'track-a/main.cpp', c / 'source/track-a/main.cpp',
         c / 'source/track-a/PERF.md', r / 'tools/official/specs/a-ingest.md',
         Path(__file__), w / 'review.md']
report = {
    'observed_at_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'official_score': False,
    'scope': 'Static source/patch/hash review only; no compiler/model/input/profile/generator/oracle/benchmark/Docker/Git/board/runtime execution or edits.',
    'source_parent': pre['source_parent'],
    'candidate_source_sha256': pre['source_sha256'],
    'unchanged_runtime_build_metadata_files': unchanged,
    'record_parser_body_byte_identical': True,
    'post_parse_aggregation_and_output_byte_identical': True,
    'patch_bindings': patch_bindings,
    'static_conclusion': 'No concrete counterexample found for exact newline coverage, equal/empty ranges, unique monotone atomic claims, private state, earliest-hour offsets, wide-escape association or exception/join behavior. Fresh source-specific executed proof and official score remain required.',
    'preparation_provenance': 'Original preparation was a logged inline Python command, not a saved pre-execution script. Recorded371+main/README patches+frozenPERF reconstruct exact source. This newly saved static binding helper is not that original driver.',
    'files': [{'path': str(p.relative_to(r)), 'bytes': p.stat().st_size, 'sha256': sha(p)} for p in files],
}
p = w / 'binding.json'
assert not p.exists()
p.write_text(json.dumps(report, indent=2) + '\n')
print(json.dumps({'binding_sha256': sha(p), 'review_sha256': sha(w / 'review.md'),
                  'script_sha256': sha(Path(__file__)),
                  'unchanged_files': len(unchanged)}, indent=2))
