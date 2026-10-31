#!/usr/bin/env python3
"""Black-box CSV/reference and bounded-progress tests for every worker topology."""
import argparse,csv,hashlib,json,os,subprocess
from pathlib import Path
import verify

def inputs(count,shape='mixed'):
    rows=['\ufeffid,name,note,region_id,amount\r\n']
    for i in range(count):
        if shape=='skew':name='same, "quoted"\n名 '
        elif shape=='diverse':name='unique/'+str(i)+' 名 '
        elif shape=='long' and i==0:name='L'*1048576+'"名'
        else:name=['','plain','trailing ','a"b','comma,name','UTF-8 名','\ufeffdata'][i%7]
        note=('line\r\n"inside",next\ufeff' if i%3 else 'pressure')
        quote=lambda v:'"'+v.replace('"','""')+'"'
        ending='' if i==count-1 and count%2 else '\r\n' if i%2 else '\n'
        rows.append(('\ufeff' if i and i%37==0 else '')+str(i*7+1)+','+quote(name)+','+quote(note)+','+str(i%5)+','+('-0.05' if i%3 else '12.34')+ending)
    return ''.join(rows).encode(),b'region_id,country\n1,AAA\n3,BBB\n'

def main():
    p=argparse.ArgumentParser();p.add_argument('--binary-dir',type=Path,required=True);p.add_argument('--run-id',required=True);p.add_argument('--threads',type=int,nargs='+',default=list(range(1,13)));p.add_argument('--report',type=Path,required=True);a=p.parse_args()
    csv.field_size_limit(4*1024*1024) # Test-only capacity for the synthetic1MiB field; official reference source is unchanged.
    oracle=verify.load('test_c_join');binary=a.binary_dir.resolve()/'track-c';checks=[];failures=[]
    cases=[('mixed-'+str(n),n,'mixed') for n in [0,1,63,64,65,127,128,129,255,256,257,511,512,513,1025,8193]]+[('skew-pressure',20000,'skew'),('diverse-pressure',30000,'diverse'),('long-record',5,'long')]
    for label,count,shape in cases:
        records,regions=inputs(count,shape);expected=oracle.run_reference(records,regions);expected=expected.encode() if isinstance(expected,str) else expected
        ident=a.run_id+'-c-coop-'+label;folder=verify.ROOT/'.data/cases'/ident;folder.mkdir(parents=True,exist_ok=True);(folder/'records.csv').write_bytes(records);(folder/'regions.csv').write_bytes(regions);runs=[]
        for threads in a.threads:
            out=verify.ROOT/'.out'/a.run_id/label/str(threads);out.mkdir(parents=True,exist_ok=True)
            for old in out.iterdir():assert old.is_file();old.unlink()
            env=dict(os.environ,SPEED_DEMON_THREADS=str(threads),ASAN_OPTIONS='halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1',TSAN_OPTIONS='halt_on_error=1')
            result=subprocess.run([str(binary),'--data',str(folder),'--out',str(out)],capture_output=True,env=env,timeout=30);stderr=result.stderr.decode(errors='replace');assert result.returncode==0 and 'Sanitizer' not in stderr,(ident,threads,result.returncode,stderr)
            assert sorted(x.name for x in out.iterdir())==['aggregates.txt'];actual=(out/'aggregates.txt').read_bytes();assert actual==expected,(ident,threads)
            runs.append({'requested_threads':threads,'sha256':hashlib.sha256(actual).hexdigest(),'returncode':result.returncode})
        checks.append({'track':'c','case':ident,'inputs_sha256':{n:hashlib.sha256(v).hexdigest() for n,v in [('records.csv',records),('regions.csv',regions)]},'reference_sha256':hashlib.sha256(expected).hexdigest(),'runs':runs});print('PASS cooperative reference/progress',ident,flush=True)
    records,regions=inputs(20000,'skew')
    bad=records.replace(b'1,',b'x,',1)
    # Final money has no quoted-field ambiguity, so the error is after queue pressure.
    last=records.rfind(b',');bad_money=records[:last+1]+b'bad\r\n'
    for label,data in [('bad-first-id',bad),('bad-late-money',bad_money)]:
        assert data!=records;ident=a.run_id+'-'+label;folder=verify.ROOT/'.data/cases'/ident;folder.mkdir(parents=True,exist_ok=True);(folder/'records.csv').write_bytes(data);(folder/'regions.csv').write_bytes(regions)
        for threads in a.threads:
            out=verify.ROOT/'.out'/a.run_id/label/str(threads);out.mkdir(parents=True,exist_ok=True);env=dict(os.environ,SPEED_DEMON_THREADS=str(threads),ASAN_OPTIONS='halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1',TSAN_OPTIONS='halt_on_error=1')
            result=subprocess.run([str(binary),'--data',str(folder),'--out',str(out)],capture_output=True,env=env,timeout=30);stderr=result.stderr.decode(errors='replace');assert result.returncode==1 and 'track-c:' in stderr and 'Sanitizer' not in stderr,(label,threads,result.returncode,stderr)
            failures.append({'case':label,'data_case':ident,'inputs_sha256':{'records.csv':hashlib.sha256(data).hexdigest(),'regions.csv':hashlib.sha256(regions).hexdigest()},'threads':threads,'returncode':result.returncode,'stderr':stderr})
        print('PASS cooperative normal cancellation',label,flush=True)
    a.report.write_text(json.dumps({'official_score':False,'oracle_csv_field_size_limit_bytes':4*1024*1024,'scope':'Official reference source unchanged; test wrapper raises Python CSV field capacity for synthetic1MiB keys. Independent official-reference output, all requested1..12 worker topologies,64/128/256/512 batch seams and EOF, highly skewed names,30000 distinct names,1MiB quoted records, BOM/UTF8/embedded-newline/CRLF/optional EOF/money/unmatched groups;30s progress bound per invocation, normal cancellation before data and after pressure. No implementation internal state is used by the oracle.','checks':checks,'expected_failures':failures,'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'passed':True},indent=2)+'\n')
if __name__=='__main__':main()
