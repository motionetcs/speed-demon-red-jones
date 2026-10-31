#!/usr/bin/env python3
"""Check observable entry requirements; never certify organizer eligibility."""
import datetime
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
KICKOFF = datetime.datetime(2026, 10, 30, 15, tzinfo=datetime.timezone.utc)
FREEZE = datetime.datetime(2026, 11, 2, 15, tzinfo=datetime.timezone.utc)
PUBLIC_DUE = FREEZE + datetime.timedelta(hours=1)


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def main():
    now = datetime.datetime.now(datetime.timezone.utc)
    spec = importlib.util.spec_from_file_location('policy', ROOT / 'tools/official/harness/dockerfile_check.py')
    policy = importlib.util.module_from_spec(spec); spec.loader.exec_module(policy)
    images = json.loads((ROOT / 'docs/allowlist.json').read_text())['images']
    repo = json.loads(subprocess.check_output(['gh','repo','view','motionetcs/speed-demon-red-jones',
        '--json','nameWithOwner,isPrivate,defaultBranchRef,licenseInfo'], text=True))
    checks = []
    def check(name, passed, evidence):
        checks.append({'requirement':name,'passed':bool(passed),'evidence':evidence})
    check('Correct repository', repo['nameWithOwner']=='motionetcs/speed-demon-red-jones',repo['nameWithOwner'])
    check('Required branch', git('branch','--show-current')=='speed-demon' and repo['defaultBranchRef']['name']=='speed-demon',git('branch','--show-current'))
    check('OSI license present', (repo.get('licenseInfo') or {}).get('key')=='mit' and 'MIT License' in (ROOT/'LICENSE').read_text(),'Root LICENSE and GitHub license detection')
    commits=[]
    for line in git('log','--reverse','--format=%H%x09%aI%x09%cI').splitlines():
        sha,author,committer=line.split('\t'); times=[datetime.datetime.fromisoformat(t) for t in [author,committer]]
        commits.append({'commit':sha,'author_time':author,'committer_time':committer})
        check('Observed commit timestamps inside event: '+sha[:7], all(KICKOFF<=t<=FREEZE for t in times),[author,committer])
    for track in 'acd':
        folder=ROOT/('track-'+track)
        for name in ['Dockerfile','README.md','PERF.md','.speed-demon.toml','main.cpp','io.hpp']:
            check(track.upper()+' required file '+name,(folder/name).is_file(),str((folder/name).relative_to(ROOT)))
        metadata=(folder/'.speed-demon.toml').read_text()
        check(track.upper()+' metadata',bool(re.search(r'^track\s*=\s*"'+track+'"',metadata,re.M)) and 'team = "Red Jones"' in metadata and 'dependency_count = 0' in metadata,metadata.splitlines())
        errors=policy.check((folder/'Dockerfile').read_text(),images)
        check(track.upper()+' allowlisted offline Docker policy',not errors,errors or 'Pinned allowlisted images; approved COPY/build policy')
        files=[p.name for p in folder.iterdir() if p.is_file()]
        module={'a':'a_ingest','c':'c_join','d':'d_traverse'}[track]
        official_generator=ROOT/'tools/official/generators'/(module+'.py')
        def source_file(name):
            if name=='Dockerfile' or Path(name).suffix in ['.cpp','.hpp','.md','.toml']: return True
            return name=='training_generator.py' and (folder/name).read_bytes()==official_generator.read_bytes()
        check(track.upper()+' no dataset/binary in build context',all(source_file(n) for n in files),files)
    check('Source public by publication deadline',not repo['isPrivate'] or now<PUBLIC_DUE,
        'Private is allowed now; public MIT source still required by '+PUBLIC_DUE.isoformat())
    report={'observed_at_utc':now.isoformat(),'scope':'Observable repository/history/build-policy checks, not an organizer eligibility certificate',
        'source_commit':git('rev-parse','HEAD'),'dirty_paths':git('status','--porcelain').splitlines(),'repository':repo,
        'checks':checks,'all_current_checks_passed':all(x['passed'] for x in checks),'history':commits,
        'future_requirements':[{'item':'Final passing speed-demon source at freeze','due_utc':FREEZE.isoformat()},
          {'item':'Make recorded source public under MIT','due_utc':PUBLIC_DUE.isoformat(),'complete':not repo['isPrivate']}],
        'human_or_organizer_facts':{'individual_registration':'Entrant confirmed complete; not independently certified',
          'team_registration':'Accepted live-board team Red Jones, A/C/D scored',
          'human_understanding':'Owner briefing provided; no invented attestation of personal code review'},
        'review_notes':['Reviewed solution source uses standard C++ and OS input/output only.',
          'No baked answers, seed recognition, or pre-event implementation was imported into this fresh repository.',
          'Byte-identical synthetic input/output hashes are checks outside scored runtime folders, not answer caches in the images.',
          'User-requested emoji reactions used visible board controls; the separate Clicking Devils totals do not change machine scores. No direct counter edits, identity changes or rate-limit bypass were used. A bulk pumpkin hold was blocked by automatic review and stopped.']}
    (ROOT/'docs/ENTRY-AUDIT.json').write_text(json.dumps(report,indent=2)+'\n')
    print('PASS' if report['all_current_checks_passed'] else 'FAIL',len(checks),'observable checks; publication still pending' if repo['isPrivate'] else 'observable checks; source public')
    return 0 if report['all_current_checks_passed'] else 1


if __name__=='__main__':
    raise SystemExit(main())
