from pathlib import Path
import hashlib,json,random,sys

ROOT=Path(sys.argv[1]).resolve();OUT=ROOT/'subset';OUT.mkdir(parents=True,exist_ok=True)
cases=[]
def add(name,k,edges,pins,minimum=0,maximum=-1,shared=False,wide=False,workers=None,all_pairs=False,query_pairs=None):
    rng=random.Random(0x262AC71+len(cases))
    n=(1<<21)+1 if wide else (65537 if len(cases)%3==1 else k)
    ids=rng.sample(range(n),k)
    if wide:ids=rng.sample(range(n-1),k-1)+[1<<21]
    queries=list(query_pairs) if query_pairs is not None else [(a,b) for a in pins for b in pins]
    if all_pairs:queries=[(a,b) for a in range(k) for b in range(k)]
    rng.shuffle(queries);queries+=queries[:3]
    rng.shuffle(edges)
    inf=10**40;distance=[[0 if a==b else inf for b in range(k)] for a in range(k)]
    for a,b,cost in edges:distance[a][b]=min(distance[a][b],cost)
    for middle in range(k):
        for a in range(k):
            for b in range(k):distance[a][b]=min(distance[a][b],distance[a][middle]+distance[middle][b])
    folder=OUT/name;folder.mkdir(exist_ok=True)
    (folder/'graph.txt').write_text(f'{n} {len(edges)}\n'+''.join(f'{ids[a]} {ids[b]} {cost}\n' for a,b,cost in edges))
    (folder/'queries.txt').write_text(''.join(f'{ids[a]} {ids[b]}\n' for a,b in queries))
    expected=''.join(str(-1 if distance[a][b]>=inf else distance[a][b])+'\n' for a,b in queries)
    (ROOT/'expected').mkdir(exist_ok=True);answer=ROOT/'expected'/(name+'.txt');answer.write_text(expected)
    item={'case':name,'nodes':n,'logical_nodes':k,'ids':ids,'edges':edges,'queries':queries,'minimum_selected':minimum,'maximum_selected':maximum,'require_shared_hub':shared,'workers':workers or list(range(1,13)),'data_folder':str(folder),'expected_file':str(answer),'reference_sha256':hashlib.sha256(answer.read_bytes()).hexdigest(),'inputs_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.iterdir()}}
    cases.append(item)

def hub(weights):
    edges=[]
    for node in [2,3,4]:
        a,b,c,d=weights(node)
        edges += [(0,node,a),(node,0,b),(1,node,c),(node,1,d)]
    return edges

for variant in range(4):
    weights=(lambda _: (0,0,0,0)) if variant==0 else (lambda v:(v+1,v*3+1,v*7+2,v*11+3))
    add(f'd262-hubs-{variant}',6,hub(weights),[0,1,5],3,3,True)
add('d262-empty-queries',6,hub(lambda v:(v+1,v+2,v+3,v+4)),[],3,3,True)
add('d262-all-pinned-control',6,hub(lambda v:(v+1,v+2,v+3,v+4)),list(range(6)),0,0,False,all_pairs=True)
for shift in range(4):
    chain=[(0,2),(2,3),(3,4),(4,5),(5,1)]
    edges=[]
    for index,(a,b) in enumerate(chain):edges += [(a,b,index*13+shift),(b,a,index*7+shift)]
    edges += [(0,6,100),(6,1,100),(1,6,300),(6,0,300)]
    add(f'd262-adjacent-chain-{shift}',8,edges,[0,1,6,7],1)
for delta in [0,1,2]:
    limit=2047
    edges=[(0,2,limit-2+delta),(2,0,3),(2,1,1),(1,2,4)]
    add(f'd262-inline-sum-{delta}',3,edges,[0,1],1 if delta==0 else 0,1 if delta==0 else 0)
for name,weights in [('edge-at-limit',(2047,1,1,1)),('max-full64',(4294967295,4294967295,4294967295,4294967295))]:
    a,b,c,d=weights;add('d262-'+name,3,[(0,2,a),(2,0,b),(1,2,c),(2,1,d)],[0,1],0,0)
base=[(0,2,2),(2,0,3),(1,2,5),(2,1,7)]
add('d262-self-loop-skip',3,base+[(2,2,0)],[0,1],0,0)
add('d262-parallel-skip',3,base+[(0,2,1)],[0,1],0,0)
add('d262-nonreciprocal-skip',4,[(0,2,2),(2,0,3),(3,2,5),(2,1,7)],[0,1,3],0,0)
for degree in [64,65]:
    edges=base[:]
    for node in range(3,degree+2):edges += [(0,node,11),(node,0,13)]
    pins=[0,1]+list(range(3,degree+2))
    # Same-node queries also protect every auxiliary neighbour while keeping q bounded.
    add(f'd262-hub-degree-{degree}',degree+2,edges,pins,1 if degree==64 else 0,1 if degree==64 else 0,workers=[1,6,12],query_pairs=[(0,1),(1,0)]+[(v,v) for v in pins])
add('d262-active-with-full64-island',9,base+[(4,5,4294967295),(5,6,4294967295),(6,4,1),(0,7,0),(7,0,0)],[0,1,4,6,8],1)
for wide,delta in [(True,-1),(True,0),(True,1),(True,2)]:
    limit=65535
    value=limit-2+delta
    add(f'd262-wide-limit-{delta+1}',3,[(0,2,value),(2,0,3),(2,1,1),(1,2,4)],[0,1],1 if value+1<limit else 0,1 if value+1<limit else 0,wide=wide,workers=[1,6,12])
add('d262-wide-query-active',4,base+[(3,0,4294967295),(0,3,4294967295)],[0,1,3],1,1,wide=True,workers=[1,6,12])
for seed in range(80):
    rng=random.Random(0x262D0F1+seed);k=rng.randrange(8,23);pins=[0,1,2,k-1];edges=[]
    choices=[0,1,2,31,63,127,511,1023,2046,2047,4294967295]
    for node in range(3,k-1):
        u,v=rng.sample([0,1,2],2)
        edges += [(u,node,rng.choice(choices)),(node,u,rng.choice(choices)),(v,node,rng.choice(choices)),(node,v,rng.choice(choices))]
        if seed%11==0:edges.append((node,node,0))
        if seed%13==0:edges.append((u,node,1))
    edges += [(0,1,rng.choice(choices)),(1,2,rng.choice(choices)),(2,0,rng.choice(choices))]
    add(f'd262-random-subset-{seed}',k,edges,pins,workers=[seed%12+1])

# This simple text stream is consumed by the C++ model, which recomputes its own
# all-pairs oracle on the original logical graph before including the exact block.
lines=[str(len(cases))]
for item in cases:
    lines.append(' '.join(map(str,[item['case'],item['nodes'],item['logical_nodes'],len(item['edges']),len(item['queries']),item['minimum_selected'],item['maximum_selected'],int(item['require_shared_hub']),len(item['workers'])])))
    lines.append(' '.join(map(str,item['ids'])));lines.append(' '.join(map(str,item['workers'])))
    lines += [' '.join(map(str,row)) for row in item['edges']]
    lines += [' '.join(map(str,row)) for row in item['queries']]
(ROOT/'cases.txt').write_text('\n'.join(lines)+'\n')
(ROOT/'cases.json').write_text(json.dumps({'official_score':False,'scope':'Independent original-graph Python Floyd oracle with sparse protected endpoint subsets; runtime source never used to derive expected answers. All-pinned cases explicitly controls.','cases':cases},indent=2)+'\n')
print('Prepared',len(cases),'independent sparse/control cases,',sum(len(x['workers']) for x in cases),'topology runs')
