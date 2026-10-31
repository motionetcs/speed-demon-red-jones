#!/usr/bin/env python3
"""Independent output-order and normal sink-error checks for the A publisher."""
import argparse,datetime,hashlib,json,os,random,subprocess
from pathlib import Path
import verify

def main():
 p=argparse.ArgumentParser();p.add_argument('--binary-dir',type=Path,required=True);p.add_argument('--run-id',required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args();verify.BIN_DIR=a.binary_dir.resolve();verify.ACTIVE_TRACKS={'a'};verify.THREADS=list(range(1,13));verify.RUN_ID=a.run_id;oracle=verify.load('test_a_ingest');start=datetime.datetime(2026,10,30,18,tzinfo=datetime.timezone.utc);stamps=[(start+datetime.timedelta(hours=h)).strftime('%Y-%m-%dT%H:00:00.000000Z') for h in range(72)];rng=random.Random(0x163b014)
 cases={}
 rows=[f'{stamps[0]} GET /lag/{i%1999} {599 if i%7 else 200} {(i*104729)&0xffffffff}\n' for i in range(40000)]
 rows +=[f'{stamps[h]} OPTIONS /late 499 {h}\n' for h in range(71,0,-1)];cases['a-first-hour-lag']=''.join(rows)
 cases['a-empty-prefix-and-holes']=f'{stamps[71]} PUT /last 500 4294967295\n'+f'{stamps[30]} HEAD /gap 499 0\n'
 rows=[f'{stamps[h]} GET /random/{i%97} {rng.choice([100,499,500,599])} {rng.choice([0,9,99,999,9999,99999,999999,9999999,99999999,999999999,4294967295])}\n' for h in range(72) for i in range(257)];rng.shuffle(rows);cases['a-unordered-publish']=''.join(rows)
 checks=[]
 for label,data in cases.items():
  expected=oracle.run_reference(data);row=verify.check('a',label,{'requests.log':data},expected);row['reference_sha256']=hashlib.sha256(expected.encode() if isinstance(expected,str) else expected).hexdigest();row['inputs_sha256']={'requests.log':hashlib.sha256(data.encode()).hexdigest()};checks.append(row)
 data=verify.ROOT/'.data/cases'/(a.run_id+'-a-empty-prefix-and-holes');failures=[]
 for threads in [1,6,12]:
  out=verify.ROOT/'.out'/a.run_id/'normal-open-error'/str(threads);out.mkdir(parents=True,exist_ok=True);(out/'summary.txt').mkdir(exist_ok=True)
  result=subprocess.run([str(verify.BIN_DIR/'track-a'),'--data',str(data),'--out',str(out)],capture_output=True,text=True,timeout=30,env=dict(os.environ,SPEED_DEMON_THREADS=str(threads),UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1'))
  assert result.returncode==1 and 'track-a:' in result.stderr and 'Sanitizer' not in result.stderr,(result.returncode,result.stderr)
  failures.append({'data_case':data.name,'threads':threads,'returncode':result.returncode,'stderr':result.stderr,'kind':'normal output-open error, no waiting/hang'})
 a.report.write_text(json.dumps({'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'official_score':False,'passed':True,'scope':'Independent complete official-reference bytes for40k-row lagging first hour, empty leading/interior hours and arbitrarily shuffled72-hour output with every latency digit width/fulluint32 and error rates, at all1..12 workers. Normal output-open errors at1/6/12 must return1 within30s. These supplement, not replace, public/untrained/parser/allocator/strict/race checks.','binary_sha256':verify.digest(verify.BIN_DIR/'track-a'),'checks':checks,'expected_failures':failures},indent=2)+'\n')
if __name__=='__main__':main()
