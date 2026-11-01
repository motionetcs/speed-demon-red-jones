#!/usr/bin/env python3
"""Independent byte-reference cases for the production CSV monetary parser."""
import argparse,json,os,subprocess
from pathlib import Path
import verify

def records(count):
    amounts=['0.00','-0.00','0.01','-0.01','-999.99','99999.99','9.99','99.00','999.01','9999.90','000000001.23','00000000000000000000.09']
    rows=['\ufeffid,name,note,region_id,amount\r\n']
    for i in range(count):
        ending='' if i==count-1 and count%2 else '\n' if i%2 else '\r\n'
        rows.append(('\ufeff' if i and i%37==0 else '')+f'{i+1},"n ""quoted"" ","note\nnext",{i%4+1},{amounts[i%len(amounts)]}'+ending)
    return ''.join(rows).encode()

def main():
    p=argparse.ArgumentParser();p.add_argument('--binary-dir',type=Path,required=True);p.add_argument('--run-id',required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args()
    verify.BIN_DIR=a.binary_dir.resolve();verify.RUN_ID=a.run_id;verify.ACTIVE_TRACKS={'c'};verify.THREADS=list(range(1,13));oracle=verify.load('test_c_join');regions=b'region_id,country\n1,AAA\n3,BBB\n';checks=[]
    for count in [1,7,31,511,512,513,1025,4097]:
        data=records(count);checks.append(verify.check('c','c-amount-boundary-'+str(count),{'records.csv':data,'regions.csv':regions},oracle.run_reference(data,regions)))
    data=b'id,name,note,region_id,amount\n1,"","",1,92233720368547758.07\n2,,,3,-92233720368547758.07'
    checks.append(verify.check('c','c-defined-signed-cents',{'records.csv':data,'regions.csv':regions},oracle.run_reference(data,regions)))
    bad_inputs={
        'empty':b'1,"a","n",1,',
        'negative':b'1,"a","n",1,-',
        'short-fraction':b'1,"a","n",1,1.0',
        'invalid-fraction':b'1,"a","n",1,1.a0\r\n',
        'extra-suffix':b'1,"a","n",1,1.00x\r\n',
    };failures=[]
    for name,body in bad_inputs.items():
        label=a.run_id+'-bad-'+name;folder=verify.ROOT/'.data/cases'/label;folder.mkdir(parents=True,exist_ok=True);(folder/'records.csv').write_bytes(b'id,name,note,region_id,amount\r\n'+body);(folder/'regions.csv').write_bytes(regions)
        for threads in [1,2,6,12]:
            out=verify.ROOT/'.out'/a.run_id/name/str(threads);out.mkdir(parents=True,exist_ok=True)
            env=dict(os.environ,SPEED_DEMON_THREADS=str(threads),UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1')
            result=subprocess.run([str(verify.BIN_DIR/'track-c'),'--data',str(folder),'--out',str(out)],capture_output=True,env=env,timeout=20);stderr=result.stderr.decode(errors='replace')
            assert result.returncode==1 and stderr.startswith('track-c:') and not any(s in stderr for s in ['Sanitizer','runtime error:','DEADLYSIGNAL']), (label,threads,result.returncode,stderr)
            failures.append({'case':name,'data_case':label,'threads':threads,'returncode':result.returncode,'stderr':stderr})
    report={'official_score':False,'passed':True,'scope':'Fresh exact official-reference CSV monetary inputs at every1..12 workers, digit/dot/fraction/sign/negative-zero/leading-zero forms, BOM/quotedLF/CRLF/EOF around511/512/513/1025/4097 queue seams, unmatched groups. Defined INT64_MAX cents and its negative occur in separate countries to avoid aggregate overflow; broader2.1 syntax is not claimed generator output. Invalid monetary fields must exit normally and promptly at1/2/6/12 without sanitizer failures.','checks':checks,'expected_failures':failures,'binary_sha256':verify.digest(verify.BIN_DIR/'track-c')}
    a.report.write_text(json.dumps(report,indent=2)+'\n');print('PASS production amount reference/edge/error cases',flush=True)
if __name__=='__main__':main()
