#!/usr/bin/env python3
"""Reference-test every specified method across cached and unordered UTC hours."""
import argparse,datetime,json,random
from pathlib import Path
import verify

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--binary-dir',type=Path,required=True);parser.add_argument('--report',type=Path,required=True);args=parser.parse_args()
    verify.BIN_DIR=args.binary_dir.resolve();verify.ACTIVE_TRACKS={'a'};verify.THREADS=[1,6,12]
    oracle=verify.load('test_a_ingest');rows=[]
    start=datetime.datetime(2026,10,30,18,tzinfo=datetime.timezone.utc)
    for hour in range(72):
        stamp=(start+datetime.timedelta(hours=hour)).strftime('%Y-%m-%dT%H:00:00.000000Z')
        for method in ['GET','POST','PUT','PATCH','DELETE','HEAD','OPTIONS']:
            for path in ['/','/ab','/v2/four','/'+'x'*124]:
                for latency in [0,1,524286,524287,524288,4294967295]:
                    for status in [100,499,500,599]:rows.append(f'{stamp} {method} {path} {status} {latency}\n')
    ordered=''.join(rows).encode();rng=random.Random(0x4ca738);rng.shuffle(rows);shuffled=''.join(rows).encode()
    checks=[]
    for label,data in [('a-method-hours-ordered',ordered),('a-method-hours-shuffled',shuffled)]:
        checks.append(verify.check('a',label,{'requests.log':data},oracle.run_reference(data.decode('ascii'))))
    args.report.write_text(json.dumps({'official_score':False,'method':'Every fixed method/72 hours/1..125-byte endpoints/status and latency escapes; sorted and arbitrarily shuffled input; full official reference bytes at1/6/12 workers','checks':checks,'passed':True},indent=2)+'\n')
if __name__=='__main__':main()
