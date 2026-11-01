#!/usr/bin/env python3
"""Exercise every valid three-letter country index and the unmatched group."""
import argparse
import csv
import io
import json
from pathlib import Path

import verify


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--binary-dir', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    verify.BIN_DIR = args.binary_dir.resolve()
    verify.ACTIVE_TRACKS = {'c'}
    verify.THREADS = [1, 6, 12]
    oracle = verify.load('test_c_join')
    codes = [chr(65 + i // 676) + chr(65 + i // 26 % 26) + chr(65 + i % 26) for i in range(17576)]
    rows = []
    for count in [0,1,54,55,56,57,62,63,64,65,118,119,120,121,246,247,248,249,254,255,256,257,17576]:
        regions = ('region_id,country\n' + ''.join(f'{i+1},{code}\n' for i, code in enumerate(codes[:count]))).encode()
        stream = io.StringIO(newline='')
        stream.write('\ufeff')
        writer = csv.writer(stream, lineterminator='\r\n')
        writer.writerow(['id', 'name', 'note', 'region_id', 'amount'])
        for i in range(count + 1):
            if i and i % 37 == 0: stream.write('\ufeff')
            names=['', 'same "name"', 'x'*254, 'x'*255, 'x'*256, 'x'*257, 'x'*253+'"', 'x'*254+'"']
            for variant,name in enumerate(names):
                writer.writerow([(i+1)*100+variant,name,'line\nnext\ufeff',i+1 if i<count else 9999999,'-0.05' if (i+variant)%2 else '0.00'])
        records = stream.getvalue().encode()
        row = verify.check('c', 'c-country-width-' + str(count), {'records.csv': records, 'regions.csv': regions}, oracle.run_reference(records, regions))
        rows.append(row)
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps({'official_score': False, 'method': 'Country widths cover packed56/spill64 boundaries through all17576, unmatched group, shared escaped name, embedded LF/BOM and negative cents; key lengths0/254/255/256/257 and escape-crossing quote interiors, full reference-byte checks at1/6/12 workers', 'checks': rows, 'passed': True}, indent=2) + '\n')


if __name__ == '__main__':
    main()
