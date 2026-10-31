#!/usr/bin/env python3
"""Run every requested topology/reference case and error in one explicit image."""
import argparse,datetime,hashlib,json,os,re,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser();p.add_argument('--build-report',type=Path,required=True);p.add_argument('--reference-report',type=Path,required=True);p.add_argument('--report',type=Path,required=True);p.add_argument('--run-id',required=True);a=p.parse_args()
    build=json.loads(a.build_report.read_text());ref=json.loads(a.reference_report.read_text());assert build['passed'] and ref['passed'];image=next(z['image_id'] for z in build['runs'] if z['track']=='c');rows=[];failures=[]
    def run(case,threads,label):
        assert re.fullmatch('[a-z0-9-]+',case) and 1<=threads<=12
        data=ROOT/'.data/cases'/case;out=ROOT/'.out'/a.run_id/label/str(threads);out.mkdir(parents=True,exist_ok=True);out.chmod(0o777)
        for old in out.iterdir():assert old.is_file();old.unlink()
        args=['docker','run','--rm','--platform','linux/amd64','--network=none','--read-only','--memory=8g','--memory-swap=8g','--pids-limit=512','--cap-drop=ALL','--security-opt=no-new-privileges','--user','65534:65534','-e','SPEED_DEMON_THREADS='+str(threads),'-v',str(data)+':/data:ro','-v',str(out)+':/out:rw',image]
        return subprocess.run(args,capture_output=True,text=True,timeout=30),out
    for row in ref['checks']:
        case=row['case'];data=ROOT/'.data/cases'/case
        for name,sha in row['inputs_sha256'].items():assert hashlib.sha256((data/name).read_bytes()).hexdigest()==sha
        for native in row['runs']:
            threads=native['requested_threads'];result,out=run(case,threads,case);assert result.returncode==0 and 'Sanitizer' not in result.stderr,(case,threads,result.returncode,result.stderr)
            assert sorted(z.name for z in out.iterdir())==['aggregates.txt'];sha=hashlib.sha256((out/'aggregates.txt').read_bytes()).hexdigest();assert sha==row['reference_sha256']
            rows.append({'track':'c','case':case,'threads':threads,'sha256':sha,'image_id':image,'inputs_sha256':row['inputs_sha256']})
        print('PASS exact image every topology',case,flush=True)
    for row in ref['expected_failures']:
        case=row['data_case'];data=ROOT/'.data/cases'/case
        for name,sha in row['inputs_sha256'].items():assert hashlib.sha256((data/name).read_bytes()).hexdigest()==sha
        result,out=run(case,row['threads'],case);assert result.returncode==1 and 'track-c:' in result.stderr and 'Sanitizer' not in result.stderr,(case,row['threads'],result.returncode,result.stderr)
        failures.append({'case':case,'threads':row['threads'],'returncode':result.returncode,'stderr':result.stderr,'image_id':image,'inputs_sha256':row['inputs_sha256']})
    a.report.write_text(json.dumps({'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'official_score':False,'scope':'Exact pinned production image, actual default/data/out paths, every1..12 requested worker topology for independently checked CSV fixtures. Bound30s per invocation; readonly/offline/unprivileged/capdrop/memory8GiB/pids512. Deterministically bound input SHA256 and official-reference output hashes include64/128/256/512 seams, empty/partial/EOF, skew/diverse names,1MiB quoted records and normal early/late cancellation. This is correctness/progress proof, not Intel performance.','image_id':image,'runs':rows,'expected_failures':failures,'passed':True},indent=2)+'\n')
if __name__=='__main__':main()
