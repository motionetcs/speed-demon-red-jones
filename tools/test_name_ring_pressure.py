#!/usr/bin/env python3
"""Independent reference checks across real ring fill/wrap and EOF boundaries."""
import argparse,csv,hashlib,io,json
from pathlib import Path
import verify

def main():
    p=argparse.ArgumentParser();p.add_argument('--binary-dir',type=Path,required=True);p.add_argument('--run-id',required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args()
    verify.BIN_DIR=a.binary_dir.resolve();verify.ACTIVE_TRACKS={'c'};verify.THREADS=list(range(1,13));verify.RUN_ID=a.run_id
    oracle=verify.load('test_c_join');checks=[]
    regions=b'region_id,country\n1,AAA\n2,BBB\n3,CCC\n4,DDD\n'
    for count in [4095,4096,4097,262161]:
        stream=io.StringIO(newline='');stream.write('\ufeffid,name,note,region_id,amount\r\n')
        writer=csv.writer(stream,lineterminator='\r\n')
        for i in range(count):
            if i and i%1009==0:stream.write('\ufeff')
            writer.writerow([i*3+1,'same "ring" \u540d ',['note','one\n"next"','\ufeffdata'][i%3],[1,2,3,4,9999999][i%5],['-0.05','0.00','12.34','99999.99','-999.99'][i%5]])
        records=stream.getvalue().encode();expected=oracle.run_reference(records,regions)
        row=verify.check('c','c-ring-pressure-'+str(count),{'records.csv':records,'regions.csv':regions},expected)
        row['inputs_sha256']={'records.csv':hashlib.sha256(records).hexdigest(),'regions.csv':hashlib.sha256(regions).hexdigest()}
        row['reference_sha256']=hashlib.sha256(expected.encode() if isinstance(expected,str) else expected).hexdigest();checks.append(row)
    a.report.write_text(json.dumps({'official_score':False,'passed':True,'scope':'Single canonical name routes to one owner, saturating every producer channel across multiple16x256 windows at all1..12 requested workers;4095/4096/4097 and262161 rows, partial last batch/ordered EOF, country/unmatched groups, escaped UTF8/trailing-space key, quoted LF and embedded/record BOM, exact signed cents. Full official reference bytes, not guessed performance or cached answers.','binary_sha256':verify.digest(verify.BIN_DIR/'track-c'),'checks':checks,'expected_failures':[]},indent=2)+'\n')
    print('PASS reference ring-pressure/wrap/EOF at every1..12 workers',flush=True)
if __name__=='__main__':main()
