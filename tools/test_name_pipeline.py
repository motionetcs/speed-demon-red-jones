#!/usr/bin/env python3
"""Independent CSV/reference and progress checks for bounded name-owner queues."""
import argparse,hashlib,json,os,subprocess
from pathlib import Path
import verify

def inputs(count):
    regions=b'region_id,country\n1,AAA\n3,BBB\n';rows=['\ufeffid,name,note,region_id,amount\r\n'];names=['','plain','trailing ','a"b','comma,name','UTF-8 \u540d','\ufeffdata']
    for i in range(count):
        name=names[i%len(names)];name='"'+name.replace('"','""')+'"' if i%2 or any(c in name for c in ',"\r\n') else name
        note='"line,""quote""\nnext\ufeff"';ending='' if i==count-1 and count%2 else '\r\n' if i%2 else '\n'
        rows.append(('\ufeff' if i and i%37==0 else '')+f'{i+1},{name},{note},{i%4+1},{"-0.05" if i%3 else "99.99"}'+ending)
    return ''.join(rows).encode(),regions

def main():
    p=argparse.ArgumentParser();p.add_argument('--binary-dir',type=Path,required=True);p.add_argument('--run-id',required=True);p.add_argument('--threads',type=int,nargs='+',default=list(range(1,13)));p.add_argument('--report',type=Path,required=True);a=p.parse_args()
    verify.BIN_DIR=a.binary_dir.resolve();verify.RUN_ID=a.run_id;verify.ACTIVE_TRACKS={'c'};verify.THREADS=a.threads;oracle=verify.load('test_c_join');checks=[]
    for count in [0,1,511,512,513,1025,4097]:
        records,regions=inputs(count);checks.append(verify.check('c','c-pipeline-batch-'+str(count),{'records.csv':records,'regions.csv':regions},oracle.run_reference(records,regions)))
    records,regions=inputs(4097);failures=[]
    for label,data in [('bad-first-id',records.replace(b'1,,',b'x,,',1)),('bad-mid-money',records.replace(b'2049,',b'2049,',1))]:
        if label=='bad-mid-money':
            marker=data.index(b'2049,');end=data.index(b'\n',data.index(b'next',marker));data=data[:end].rsplit(b',',1)[0]+b',bad'+data[end:]
        assert data!=records
        folder=verify.ROOT/'.data/cases'/(a.run_id+'-'+label);folder.mkdir(parents=True,exist_ok=True);(folder/'records.csv').write_bytes(data);(folder/'regions.csv').write_bytes(regions)
        for threads in [2,6,12]:
            out=verify.ROOT/'.out'/a.run_id/label/str(threads);out.mkdir(parents=True,exist_ok=True)
            env=dict(os.environ,SPEED_DEMON_THREADS=str(threads),UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
            result=subprocess.run([str(verify.BIN_DIR/'track-c'),'--data',str(folder),'--out',str(out)],capture_output=True,env=env,timeout=20);stderr=result.stderr.decode(errors='replace')
            assert result.returncode!=0 and 'track-c:' in stderr and 'Sanitizer' not in stderr,(label,threads,result.returncode,stderr)
            failures.append({'case':label,'threads':threads,'returncode':result.returncode,'stderr':stderr})
    report={'official_score':False,'scope':'Independent official-reference bytes for empty/tiny/511/512/513/1025/4097 rows, every requested worker count, equivalent quoted/unquoted/escaped/Unicode/BOM/CRLF/EOF names, unmatched regions, exact cents; malformed input must exit promptly through normal exception handling without sanitizer diagnostics.','checks':checks,'expected_failures':failures,'binary_sha256':verify.digest(verify.BIN_DIR/'track-c'),'passed':True};a.report.write_text(json.dumps(report,indent=2)+'\n');print('PASS bounded pipeline progress/ownership/reference checks',flush=True)
if __name__=='__main__':main()
