from pathlib import Path
import datetime, hashlib, json, shutil, subprocess

r = Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh')
w = r / '.build/round392'
read = lambda p: json.loads(Path(p).read_text())
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
digest = lambda b: hashlib.sha256(b).hexdigest()
def dump(p, obj): Path(p).write_text(json.dumps(obj, indent=2) + '\n')
def git(*args): return subprocess.check_output(['git', *args], cwd=r)

now = datetime.datetime.now(datetime.timezone.utc).isoformat()
head = git('rev-parse', 'HEAD').decode().strip()
assert head == '9a1dbc4b00846389bbba70d80c976a2407a70b54'
assert git('rev-parse', 'origin/speed-demon').decode().strip() == head
assert not git('diff', '--cached', '--name-only').strip()
assert not (w / 'finalized.json').exists()
actual = read(r / 'docs/board-round392-original-restored.json')
committed = read(r / 'docs/round392-committed-source-match.json')
prior = read(r / 'docs/round385-final-source-match.json')
comparison = read(r / 'docs/round392-confirmed-comparison.json')['current']
fp = read(r / 'docs/round392-feed-proof.json')
assert actual['passed'] and actual['commit'] == head == committed['source_commit']
assert fp['passed'] and sha(r / fp['raw_path']) == fp['sha256']
assert (r / fp['raw_path']).stat().st_size == fp['bytes']
rows = []
for old in prior['inputs']:
    p, h = old['path'], old['sha256']
    best = comparison['tracks'][p[6]]['best']
    checks = {
        'current': sha(r / p),
        'selected_git': digest(git('show', head + ':' + p)),
        'submitted392': sha(w / 'submitted-source' / p),
        'passing385': sha(r / '.build/round385/submitted-source' / p),
        'best_component_git': digest(git('show', best['commit'] + ':' + p)),
    }
    assert all(v == h for v in checks.values()), p
    rows.append({'path': p, 'sha256': h, 'image_id': prior['images'][p[6]],
                 'matches': checks, 'best_scored_commit': best['commit'],
                 'best_run_id': best['run_id'], 'selected_scored_commit': head,
                 'actual_run_id': actual['tracks'][p[6]]['run_id']})
assert len(rows) == 30
make = prior['Makefile_sha256']
assert sha(r / 'Makefile') == make == sha(w / 'submitted-source/Makefile') == digest(git('show', head + ':Makefile'))
for t, names in prior['complete_file_sets_excluding_PERF'].items():
    assert sorted(str(p.relative_to(r)) for p in (r / ('track-' + t)).iterdir()
                  if p.is_file() and p.name != 'PERF.md') == names
    assert sorted(p for p in git('ls-tree', '-r', '--name-only', head, 'track-' + t + '/').decode().splitlines()
                  if not p.endswith('/PERF.md')) == names
    p = 'track-' + t + '/README.md'
    assert sha(r / p) == prior['README_sha256'][t] == sha(w / 'submitted-source' / p) == digest(git('show', head + ':' + p))
    x = actual['tracks'][t]
    assert x['ok'] and x['stage'] == 'scored' and all(x['gates'].values())
    assert comparison['tracks'][t]['latest']['commit'] == head
    assert comparison['tracks'][t]['latest']['run_id'] == x['run_id']

proof = {'observed_at_utc': now, 'passed': True, 'official_score': False,
         'actual_board_confirmation_pending': False, 'source_commit': head,
         'selected_commit': head, 'source_parent': committed['source_parent'],
         'inputs': rows, 'Makefile_sha256': make, 'images': prior['images'],
         'complete_file_sets_excluding_PERF': prior['complete_file_sets_excluding_PERF'],
         'README_sha256': prior['README_sha256'],
         'actual_board_report': 'docs/board-round392-original-restored.json',
         'actual_records': actual['tracks'], 'actual_all_gates_passed': True,
         'actual_public_board_confirmed': True,
         'best_records': {t: comparison['tracks'][t]['best'] for t in 'acd'},
         'scope': 'Exact original A178/C175/D334 source30/Make/README/fullsets/current/Git/submitted392/passing385/per-track-best components after full A391 Docker/README/image rollback. Real latest records and one ordinary complete feed verified. Local images are replay identities, not organizer ELFs. Historical best/latest and unchanged-source repeat variation are separate. No new algorithm/ranking/causal gain or number-one/holdout/judging/eligibility/understanding/prize guarantee.'}
dump(r / 'docs/round392-final-source-match.json', proof)
dump(r / 'docs/round392-scored-source-match.json', proof)

loss = read(r / 'docs/board-round391-runtime8.json')['tracks']['a']
overall = comparison['best_three_machine_points']
summary = 'Original392 all tracks real-confirmed at ' + head + ': ' + '/'.join(t.upper() + str(actual['tracks'][t]['points']) for t in 'acd')
summary += '. A391 final default8 completely removed after real K' + str(loss['K']) + '/' + str(loss['points']) + ' below retained A32.070167/75.305061.'
summary += f" Feed {comparison['generated_at']}: rank {overall['rank']}/{overall['eligible_scored_teams']}, mean {overall['geometric_mean']:.6f}, leader {overall['leader']['team']} {overall['leader']['geometric_mean']:.6f}. Number one remains unachieved."

result = f"# Results — 2 November 2026\n\nFeed **{comparison['generated_at']}**: Red Jones **{overall['rank']}/{overall['eligible_scored_teams']}**, best-three geometric machine mean **{overall['geometric_mean']:.6f}**. Leader **{overall['leader']['team']} {overall['leader']['geometric_mean']:.6f}**. Number one remains unachieved; final holdout and judging are separate.\n\nSelected source **{head}**, `speed-demon`, PRIVATE/MIT: **A178/C175/D334**. Every actual check/build/correctness/timeout/sandbox gate passes for all three.\n\n| Track | Best points | Best K | Rank | Track leader |\n| --- | ---: | ---: | ---: | --- |\n"
for t in 'acd':
    x = comparison['tracks'][t]; b = x['best']; leader = x['leader']
    result += f"| {t.upper()} | {b['points']:.6f} | {b['K']:.6f} | {x['rank']}/{x['scored_teams']} | {leader['team']} {leader['points']:.6f} |\n"
result += '\n| Latest392 | Run | Time | Charged memory | S | K | Points |\n| --- | --- | ---: | ---: | ---: | ---: | ---: |\n'
for t in 'acd':
    x = actual['tracks'][t]
    result += f"| {t.upper()} | {x['run_id']} | {x['T_s']} | {x['M_bytes']} | {x['S']} | {x['K']} | {x['points']} |\n"
result += '''
These latest records use the fully restored original source. Historical bests and repeat variation remain separate; no new retained algorithm, causal or ranking gain is claimed.

[Exact selected source/image proof](round392-final-source-match.json), [real records](board-round392-original-restored.json), [leader comparison](round392-confirmed-comparison.json), [raw-feed integrity](round392-feed-proof.json).

A391 changed only the final image default to eight workers, retaining original generic A C++/headers, native CLI default12, build training default12 and the exact original production ELF. Native public/independent full comparisons traded 0.8–3.1% more time for 1.75–2.61MB less process RSS; this was a hypothesis about time and memory, not Intel or charged-memory evidence. Fresh cached source-exact ASAN29+2 and TSAN29+2 at8 passed. Cached GNU343 strict29+2 used its disclosed historical mtune flag for logic checks only; that flag was never deployed. The pinned offline image reused all compiler/training RUN steps, and ELF8dd0a2e5... matched original b57. Actual image38+2,29 true default8+2 normal errors+2 deferred sink failures, and cached actual Make/native15 passed. An initial output-open fixture omitted the required summary.txt directory; the valid empty input correctly succeeded, the assertion caught the setup error, failed evidence was preserved and setup was corrected in every mode. Completed work was reused.

Every actual A391 gate passed, but run-8a407cb43703 measured T.058275/M18710528/S498/K27.858751/72.248082, below retained K32.070167/75.305061. Lower observed memory did not offset slower time and the added source line. These comparisons are observations, not precise causal estimates. Dockerfile/README/image were fully restored. Eight fresh original-image public/saved untrained3911 replays at1/6/12/true default12 and cached actual Make/native12 passed without recompilation, new model, training or reference generation. The restored all-track392 runs above confirm every gate. [Rejected scored source](round391-scored-source-match.json), [proof archive](round391-proof-archive.json).

D386 blocked negative filter, A387 two-sample private cache hash, D389 smaller initial wide map and C390 main-owned pipeline buffer preallocation were screened once and rejected after weak/mixed native time or memory tradeoffs. Full public and saved independent outputs matched; no broad strict/image/actual proof or target gain is claimed for these rejected screens. D388 is an unscored native wide-map occupancy diagnostic, not a graph-domain bound or memory/performance result. Exact reports and executed drivers are under docs/round386-*, docs/round387-*, docs/round388-*, docs/round389-*, docs/round390-* and corresponding tools directories. Prior A376/C384 and other rejected changes remain historical; D334 remains the retained mapped-prefix gain.

Publication is authorized only for motionetcs/speed-demon-red-jones during2 November15:00–16:00UTC, after preserving the frozen passing source and completing the final privacy/history/image review. Stop risky starts14:00 and runtime/commits/pushes15:00UTC. Keep private before the window. Historical track README rollback is byte-exact; the current source/defaults and verified records in this report are authoritative.
'''
(w / 'RESULTS.before-finalize.md').write_text((r / 'docs/RESULTS.md').read_text())
(r / 'docs/RESULTS.md').write_text(result)
(r / 'docs/SUBMISSION.md').write_text('# Submission status — 2 November 2026\n\n' + summary + '\n\nSelected source30/Make/README/fullsets/images and real all-track records: docs/round392-final-source-match.json. A391 final default8 Docker/README/image completely removed. Best/latest/ranks remain separate in RESULTS.md. PRIVATE/MIT; publication only approved15:00–16:00UTC after preserving the passing frozen source and completing final history/privacy/image review. No human understanding or eligibility attestation is invented.\n')

for t in 'acd':
    x = actual['tracks'][t]; p = r / ('track-' + t) / 'PERF.md'
    p.write_text(p.read_text() + f"\n\nOriginal392/{head}, {x['run_id']}, every actual gatePASS: T{x['T_s']}/M{x['M_bytes']}/S{x['S']}/K{x['K']}/{x['points']} points after complete A391 final ENV8 Docker/README/image rollback. Source30/Make/README/fullsets/current/Git/submitted392/passing385/per-track-best/localimages exact in docs/round392-final-source-match.json. Unchanged-source repeat; historical best stays separate, no new algorithm/causal/ranking gain. Fresh original A image8/public+saved independent untrained3911 incl true defaults and cached Make/native12 passed without repeated compiler/model/training/reference.\n")

review = read(r / 'docs/PUBLICATION-REVIEW.json'); audit = read(r / 'docs/ENTRY-AUDIT.json')
assert audit['source_commit'] == head and audit['all_current_checks_passed']
assert audit['repository']['isPrivate'] and audit['repository']['licenseInfo']['key'] == 'mit'
assert review['reviewed_head'] == head and not review['credential_pattern_findings']
assert sha(r / 'docs/emoji-result.jpg') == '39c27548e6513e81ae0badc343f5ad862ad361b4a7319af368a7deed540e7573'

state_old = (r / 'docs/STATE.md').read_text()
(w / 'STATE.before-finalize.md').write_text(state_old)
tail = state_old[state_old.index('Previous376 A dynamic4MiB jobs,'):]
tail = tail.replace('ALL compiler/model/generator/oracle/PGO/benchmark/watcher sessions terminal; no pending work.', 'ALL compiler/model/generator/oracle/PGO/benchmark/watcher sessions through392 terminal; no pending work.')
tail = tail.replace('Next fresh round386 if materially novel idea and enough time;', 'Next fresh round393 only if materially novel idea and enough time;')
tail = tail.replace('Audit current385 PRIVATE/MIT/all current observable checksPASS. History 5197blobs/207396170B,', f"Audit current392 PRIVATE/MIT/all current observable checksPASS. History {review['blobs']}blobs/{review['total_uncompressed_object_bytes']}B,")
tail = tail.replace('Pending post385 docs/audits/results/PERFs', 'Pending post392 docs/audits/results/PERFs')
tail = tail.replace('Complete ordinary current full feed generated2026-11-02T10:41:22Z, 938713B/SHA5692569960af23421472b83e2a7c41cb16c5940edd49d4e2a7acaf50c2c1b1de, saved BEFORE parse at.out/board-watch/round385-current-full.json.', f"Complete ordinary current full feed generated{fp['feed_generated_at']}, {fp['bytes']}B/SHA{fp['sha256']}, saved BEFORE parse at{fp['raw_path']}.")
state = '# Original392 real-confirmed; no active jobs\n\n' + summary + '\n\n'
state += f'HEAD/origin {head}, speed-demon, PRIVATE/MIT. A178/C175/D334 exact original385 preserved. Source30/Make/README/fullsets/current/Git/submitted392/passing385/per-track-best/localimages: docs/round392-final-source-match.json. All A391 Docker/README/image changes removed. Selected snapshot .build/round392/submitted-source. Latest real records docs/board-round392-original-restored.json. Results and historical best/latest remain separate.\n\n'
state += 'Bests ' + '; '.join(f"{t.upper()}{comparison['tracks'][t]['best']['points']:.6f}/K{comparison['tracks'][t]['best']['K']:.6f}, {comparison['tracks'][t]['best']['run_id']}/{comparison['tracks'][t]['best']['commit']}" for t in 'acd') + '.\n\n'
state += 'A391 final image ENV8 only was locally fully proved but LOST real totalK27.858751/72.248082 against retained32.070167/75.305061. Original source restored and real-confirmed392. Exact unchanged original ELF/source bindings, fresh ASAN29+2/TSAN29+2/GNU29+2, image38+2/true-default29+2/deferredsink2/Make15 historical391. GNU cached historical343 mtune logic-only flag was not deployed. Initial output-open fixture setup failure preserved; corrected directory setup passed in every mode without repeating completed work. Final README-only tested-to-submitted caption differences preserved in initial/final source proof, then original rollback392. No runtime parser/source change or new compiler/model/training in391/392. New 392 true-default original A controls8 and actual cached Make/native12 passed. Do not retry eight or nearby worker counts blindly.\n\n'
state += '386 D blocked negativefilter rejected native ratios1.00245/1.01123/.99513,387 A two-samplehash .99497/1.00229/1.00945,389 D wideinitial256 .99188/.99276/.99668 withmixedRSS,390 C mainalloc both queue/staging vectors .98780/1.02226/.97310/1.00386. Each isolated once-compiled native fullhash screen rejected before broad strict/GNU/image/default/actual proof.388 diagnostic maxima607/478/435 used wide labels at12 on public/1823/2633 are observations, never a domain bound or claimed target memory saving. Exact reports/tools archived391. No rejected code selected.\n\n'
state += 'C384 prior four-word specialization lost actualK22.616733/67.721494 below23.033578/68.118071; fully removed through385. Prior378/381D loading,382C unselected one-word path,383A offsets,379ELF analysis and380native phase diagnostics remain historical, not selected or organizer performance evidence. See round-specific reports and PERF history.\n\n' + tail
(r / 'docs/STATE.md').write_text(state)

for name in ['fetch.py', 'finalize.py']:
    shutil.copy2(w / name, r / 'tools/round392-proof' / name)
archive = read(r / 'docs/round392-proof-archive.json')
archive.update(observed_at_utc=now, actual_all_gates_passed=True,
               actual_board_report='docs/board-round392-original-restored.json',
               final_source_proof='docs/round392-final-source-match.json',
               drivers={str(p.relative_to(r)): sha(p) for p in (r / 'tools/round392-proof').iterdir() if p.is_file()},
               scope='Exact full A391 rollback. Fresh original image and native controls plus cooled real all-track392 confirmation. No new compiler/model/training/reference. Historical best/latest and repeat variation separate. Executed historical private_push392 receipt scope mistakenly says370loser; actual parent/rejected source is391 and assertions bind it correctly; driver preserved unchanged.')
dump(r / 'docs/round392-proof-archive.json', archive)
dump(w / 'ACTIVE.json', {'status': 'original_real_confirmed', 'commit': head, 'all_tracks_passed': True, 'runtime_pending': False, 'summary': summary})
dump(r / '.build/round391/ACTIVE.json', {'status': 'rejected_real_score_fully_restored_confirmed', 'rejected_commit': committed['source_parent'], 'passing_selected_commit': head, 'S': loss['S'], 'K': loss['K'], 'points': loss['points'], 'no_active_work': True})
dump(w / 'finalized.json', {'observed_at_utc': now, 'commit': head, 'all_tracks_passed': True, 'rank': overall['rank'], 'eligible_scored_teams': overall['eligible_scored_teams'], 'runtime_modified_by_finalizer': False, 'publication_action': False})
print(json.dumps({'confirmed': head, 'all_tracks_passed': True, 'rank': overall['rank'], 'teams': overall['eligible_scored_teams'], 'retained_gain': False, 'publication_action': False}), flush=True)
