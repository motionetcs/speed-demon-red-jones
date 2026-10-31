#!/usr/bin/env python3
"""Independent all-pairs checks for band ordering, light cycles, and 64-bit paths."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess

ROOT=Path(__file__).resolve().parents[1]


def main():
    p=argparse.ArgumentParser();p.add_argument('--binary',type=Path,required=True);p.add_argument('--report',type=Path,required=True);p.add_argument('--count',type=int,default=256);a=p.parse_args()
    binary=a.binary.resolve();cases=[]
    weights=[0,1,2,31,32,63,64,65,127,128,129,255,256,257,65535,4294967295]
    for seed in range(a.count):
        rng=random.Random(0x4ca700+seed);n=rng.randrange(4,29);edges=[];inf=10**40
        distance=[[0 if u==v else inf for v in range(n)] for u in range(n)]
        # A cheaper path arrives after a larger label within one band.
        edges.extend([(0,1,50),(0,2,1),(2,1,1),(1,3,1)])
        for _ in range(rng.randrange(n,n*n//2+1)):
            edges.append((rng.randrange(n),rng.randrange(n),rng.choice(weights)))
        rng.shuffle(edges)
        for u,v,w in edges:distance[u][v]=min(distance[u][v],w)
        for k in range(n):
            for u in range(n):
                for v in range(n):distance[u][v]=min(distance[u][v],distance[u][k]+distance[k][v])
        data=ROOT/'.data/cases'/('d-band-independent-'+str(seed));data.mkdir(parents=True,exist_ok=True)
        out=ROOT/'.out/band-independent'/str(seed);out.mkdir(parents=True,exist_ok=True)
        (data/'graph.txt').write_text(str(n)+' '+str(len(edges))+'\n'+''.join(f'{u} {v} {w}\n' for u,v,w in edges))
        queries=[(u,v) for u in range(n) for v in range(n)];queries+=queries[:10]
        (data/'queries.txt').write_text(''.join(f'{u} {v}\n' for u,v in queries))
        expected=''.join(str(-1 if distance[u][v]>=inf else distance[u][v])+'\n' for u,v in queries).encode()
        threads=[1,6,12][seed%3]
        subprocess.run([str(binary),'--data',str(data),'--out',str(out)],env=dict(os.environ,SPEED_DEMON_THREADS=str(threads)),check=True,timeout=30)
        actual=(out/'distances.txt').read_bytes();assert actual==expected,(seed,n,threads)
        cases.append({'seed':seed,'nodes':n,'edges':len(edges),'queries':len(queries),'threads':threads,'sha256':hashlib.sha256(actual).hexdigest()})
    a.report.parent.mkdir(parents=True,exist_ok=True)
    a.report.write_text(json.dumps({'official_score':False,'method':'independent Floyd-Warshall, boundary-weight and delayed-improvement graphs, complete output-byte comparisons','binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest(),'cases':cases,'passed':True},indent=2)+'\n')
    print('PASS',len(cases),'independent graphs and',sum(c['queries'] for c in cases),'query outputs',flush=True)


if __name__=='__main__':main()
