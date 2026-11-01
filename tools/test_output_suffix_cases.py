#!/usr/bin/env python3
"""Independent signed64 references for the six-number A output suffix."""
import argparse,hashlib,random
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);args=p.parse_args()
vals={0,1,9,10,99,100,999,1000,(1<<32)-1,(1<<63)-1,1<<63,(1<<64)-1}
for k in range(65):
 for delta in [-1,0,1]:
  v=(1<<k)+delta
  if 0<=v<(1<<64):vals.add(v)
for k in range(20):
 for delta in [-1,0,1]:
  v=10**k+delta
  if 0<=v<(1<<64):vals.add(v)
cases=[]
for v in sorted(vals):
 cases.append([v]*6)
 for pos in range(6):
  row=[0]*6;row[pos]=v;cases.append(row)
rng=random.Random(0x268c0de)
for _ in range(10000):cases.append([rng.getrandbits(64) for _ in range(6)])
rows=[]
for values in cases:
 signed=[v if v<(1<<63) else v-(1<<64) for v in values];rows.append(' '.join(map(str,values))+'|'+' '.join(['',*map(str,signed)])+'\n')
args.out.parent.mkdir(parents=True,exist_ok=True)
args.out.write_text(''.join(rows))
print(len(cases),hashlib.sha256(args.out.read_bytes()).hexdigest())
