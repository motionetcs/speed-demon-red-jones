#!/usr/bin/env python3
"""Replay independently checked cases inside the validated Linux images."""
import argparse
import datetime
import hashlib
import json
from pathlib import Path
import re
import shlex
import subprocess

ROOT=Path(__file__).resolve().parents[1]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--source-report',type=Path,action='append');parser.add_argument('--independent-report',type=Path);parser.add_argument('--report',type=Path,default=ROOT/'docs/round2-pgo-untrained-containers.json');args=parser.parse_args()
    reports=args.source_report or [ROOT/'docs'/name for name in ['round2-ac-sample.json','round2-ac-sanitizers.json','round2-cd-final-sample.json','round2-cd-final-sanitizers.json']]
    cases={}
    for name in reports:
        data=json.loads(Path(name).read_text()); assert data['passed']
        for row in data['checks']:
            tr,label=row['track'],row['case'];assert re.fullmatch('[a-z0-9-]+',label)
            expected=row.get('reference_sha256') or row['runs'][0]['sha256']
            folder=ROOT/'.data'/'cases'/label
            if not folder.is_dir():folder=ROOT/'.data'/tr/label
            assert folder.is_dir(); cases[tr,label]=(folder.relative_to(ROOT/'.data'),expected)
    if args.independent_report:
        independent=json.loads(args.independent_report.read_text());assert independent['passed']
        for row in independent['cases']:
            label='d-band-independent-'+str(row['seed']);folder=Path('cases')/label;assert (ROOT/'.data'/folder).is_dir()
            cases['d',label]=(folder,row['sha256'])
    report={'created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'official_score':False,
      'scope':'Emulated Linux output comparisons on independently checked untrained samples/adversarial fixtures; explicit development paths, restricted containers. Official default output contract is separately tested.','runs':[]}
    for tr in 'acd':
        tag='speed-demon-fresh/track-'+tr+':validated'
        image=json.loads(subprocess.check_output(['docker','image','inspect',tag],text=True))[0]
        out=ROOT/'.out/container-untrained'/tr;out.mkdir(parents=True,exist_ok=True);out.chmod(0o777)
        script=['set -eu']; jobs=[]
        for (track,label),(folder,expected) in cases.items():
            if track!=tr:continue
            for threads in [1,6,12]:
                ident=label+'-t'+str(threads)
                script.append('SPEED_DEMON_THREADS='+str(threads)+' /app/solution --data '+shlex.quote('/cases/'+str(folder))+' --out '+shlex.quote('/out/'+ident))
                jobs.append((label,threads,ident,expected))
        subprocess.run(['docker','run','--rm','--platform','linux/amd64','--network=none','--read-only','--memory=8g','--memory-swap=8g','--cap-drop=ALL','--security-opt=no-new-privileges','--user','65534:65534','--entrypoint','/bin/sh','-v',str(ROOT/'.data')+':/cases:ro','-v',str(out)+':/out:rw',tag,'-c','\n'.join(script)],check=True,timeout=600)
        output={'a':'summary.txt','c':'aggregates.txt','d':'distances.txt'}[tr]
        for label,threads,ident,expected in jobs:
            files=list((out/ident).iterdir()); assert [p.name for p in files]==[output]
            actual=hashlib.sha256(files[0].read_bytes()).hexdigest();assert actual==expected,(tr,label,threads)
            report['runs'].append({'track':tr,'case':label,'threads':threads,'sha256':actual,'image_id':image['Id']})
        print('PASS Linux untrained/adversarial',tr,len(jobs),'runs',flush=True)
    report['passed']=True
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__':main()
