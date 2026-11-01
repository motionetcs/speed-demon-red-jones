#!/usr/bin/env python3
"""Independent CSV oracle for genuine low32 fingerprints sharing a routed owner."""
import argparse,hashlib,json
from pathlib import Path
import verify

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--binary-dir',type=Path,required=True)
    parser.add_argument('--model-report',type=Path,required=True)
    parser.add_argument('--run-id',required=True)
    parser.add_argument('--report',type=Path,required=True)
    args=parser.parse_args();model=json.loads(args.model_report.read_text());assert model['passed']
    pair=model['actual_collision'];left,right=pair['left'],pair['right'];assert left!=right
    verify.BIN_DIR=args.binary_dir.resolve();verify.ACTIVE_TRACKS={'c'}
    verify.THREADS=list(range(1,13));verify.RUN_ID=args.run_id
    oracle=verify.load('test_c_join');checks=[]
    for countries in [1,257]:
        codes=[chr(65+i//676)+chr(65+i//26%26)+chr(65+i%26) for i in range(countries)]
        regions=('region_id,country\n'+''.join(f'{i+1},{code}\n' for i,code in enumerate(codes))).encode()
        for count in [1,512,513,8193]:
            rows=['\ufeffid,name,note,region_id,amount\r\n']
            for i in range(count):
                name=[left,right][i%2];note='line,"quoted"\nnext\ufeff'
                quote=lambda value:'"'+value.replace('"','""')+'"'
                region=[1,countries,9999999][i%3];amount=['-0.05','0.00','12.34'][i%3]
                ending='' if i==count-1 and count%2 else '\r\n' if i%2 else '\n'
                rows.append(('\ufeff' if i and i%37==0 else '')+f'{i*3+1},{quote(name)},{quote(note)},{region},{amount}'+ending)
            records=''.join(rows).encode();expected=oracle.run_reference(records,regions)
            row=verify.check('c',f'c-real-hash-collision-{countries}-{count}',{'records.csv':records,'regions.csv':regions},expected)
            row['reference_sha256']=hashlib.sha256(expected.encode() if isinstance(expected,str) else expected).hexdigest()
            row['inputs_sha256']={name:hashlib.sha256(data).hexdigest() for name,data in [('records.csv',records),('regions.csv',regions)]}
            checks.append(row)
    report={'official_score':False,'passed':True,'scope':'Actual compiler-specific production std::hash low32 fingerprint pair with the unchanged modulo4 owner, exercised through fresh group4 storage/probing, found by the routing model; both names quoted with unchanged raw bytes. Official reference distinct-name counts, narrow/wide country lookup, every1..12 requested worker,512/513 partial/EOF and8193 pressure, unmatched regions, BOM/quoted LF/quotes/UTF8 bytes and exact signed cents. Native and GCC std::hash implementations may differ; each model pair is labeled for its own compiler, and both byte fixtures are replayed independently in current GCC/image modes. No runtime hash injection or answer catalogue.',
            'model_report':str(args.model_report),'actual_collision':pair,'checks':checks,'expected_failures':[],'binary_sha256':verify.digest(verify.BIN_DIR/'track-c')}
    args.report.write_text(json.dumps(report,indent=2)+'\n');print('PASS independent group4 collision CSV references',flush=True)

if __name__=='__main__':main()
