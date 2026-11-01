"""Independent full-program stress for learned endpoint-length hints."""
import argparse,datetime,hashlib,json,os,random,subprocess
from pathlib import Path
import verify

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--binary-dir',type=Path,required=True)
    parser.add_argument('--run-id',required=True)
    parser.add_argument('--report',type=Path,required=True)
    args=parser.parse_args()
    verify.BIN_DIR=args.binary_dir.resolve();verify.RUN_ID=args.run_id
    verify.ACTIVE_TRACKS={'a'};verify.THREADS=list(range(1,13))
    oracle=verify.load('test_a_ingest');rng=random.Random(0x254a719)
    begin=datetime.datetime(2026,10,30,18,tzinfo=datetime.timezone.utc)
    stamps=[(begin+datetime.timedelta(hours=h)).strftime('%Y-%m-%dT%H:00:00.000000Z') for h in range(72)]
    prefix='/equal-prefix-16';assert len(prefix)==16
    paths=[]
    for i in range(4097):
        key=prefix+'/'+str(i)+'/'
        paths.append(key+'x'*([24,31,63,125][i%4]-len(key)))
    rows=[];methods=['GET','POST','PUT','PATCH','DELETE','HEAD','OPTIONS']
    values=[0,9,99,999,9999,99999,524286,524287,524288,9999999,99999999,999999999,4294967295]
    for repeat in range(4):
        for i,key in enumerate(paths[:4096]):
            rows.append(f'{stamps[(i*13+repeat*17)%72]} {methods[(i+repeat)%7]} {key} {rng.choice([100,499,500,599])} {values[(i+repeat)%len(values)]}\n')
    rng.shuffle(rows);text=''.join(rows)
    expected=oracle.run_reference(text)
    check=verify.check('a','a-span-prefix-aliases-id4095',{'requests.log':text},expected)
    check['reference_sha256']=hashlib.sha256(expected.encode() if isinstance(expected,str) else expected).hexdigest()
    check['inputs_sha256']={'requests.log':hashlib.sha256(text.encode()).hexdigest()}
    failures=[]
    prime=f'{stamps[0]} GET {paths[0]} 200 1\n'
    invalid={
        'missing-delimiter':prime+f'{stamps[0]} GET {paths[0]}',
        'missing-status':prime+f'{stamps[0]} GET {paths[0]} ',
        'truncated-latency':prime+f'{stamps[0]} GET {paths[0]} 200 4294967295',
        'overflow-latency':prime+f'{stamps[0]} GET {paths[0]} 200 4294967296\n',
        'endpoint-quota':''.join(f'{stamps[i%72]} GET {key} 200 1\n' for i,key in enumerate(paths)),
    }
    for label,data in invalid.items():
        folder=verify.ROOT/'.data/cases'/(args.run_id+'-'+label);folder.mkdir(parents=True,exist_ok=True)
        (folder/'requests.log').write_text(data)
        for workers in [1,6,12]:
            out=verify.ROOT/'.out'/args.run_id/label/str(workers)
            result=subprocess.run([str(verify.BIN_DIR/'track-a'),'--data',str(folder),'--out',str(out)],capture_output=True,text=True,timeout=30,env=dict(os.environ,SPEED_DEMON_THREADS=str(workers),UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1'))
            assert result.returncode==1 and result.stderr.startswith('track-a: ') and not result.stdout,(label,workers,result.returncode,result.stderr)
            assert not any(x in result.stderr for x in ['Sanitizer','runtime error:','DEADLYSIGNAL'])
            assert not out.exists() or not list(out.iterdir())
            failures.append({'case':folder.name,'threads':workers,'returncode':1,'stderr':result.stderr,'inputs_sha256':{'requests.log':hashlib.sha256(data.encode()).hexdigest()}})
    report={'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'passed':True,'official_score':False,'scope':'Independent complete reference at all1..12 workers:4096 exact endpoints sharing first16 bytes, differing lengths/suffixes through125bytes, every method/hour and latency width/fulluint32 escape, duplicates/shuffled chunks and ID4095. Deliberately adversarial hint collisions, not a speed benchmark. Primed prefix with missing delimiter/status/truncated/overflow latency plus4097-endpoint cancellation must return normal1/no sanitizer/no output/no hang at1/6/12.','binary_sha256':verify.digest(verify.BIN_DIR/'track-a'),'checks':[check],'expected_failures':failures}
    args.report.write_text(json.dumps(report,indent=2)+'\n')
    print('PASS span alias ID4095 all1..12 reference +15 normal errors')

if __name__=='__main__':main()
