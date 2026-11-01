from pathlib import Path
import hashlib,json,sys
ROOT=Path(sys.argv[1]).resolve();OUT=ROOT/'subset';OUT.mkdir(parents=True,exist_ok=True);(ROOT/'expected').mkdir(exist_ok=True)
cases=[]
def add(name,k,edges,pins,minimum,maximum,shared=False):
    ids=list(range(k));queries=[(a,b) for a in pins for b in pins];queries+=queries[:3]
    inf=10**40;distance=[[0 if a==b else inf for b in range(k)] for a in range(k)]
    for a,b,w in edges:distance[a][b]=min(distance[a][b],w)
    for middle in range(k):
        for a in range(k):
            for b in range(k):distance[a][b]=min(distance[a][b],distance[a][middle]+distance[middle][b])
    data=OUT/name;data.mkdir(exist_ok=True)
    (data/'graph.txt').write_text(f'{k} {len(edges)}\n'+''.join(f'{a} {b} {w}\n' for a,b,w in edges))
    (data/'queries.txt').write_text(''.join(f'{a} {b}\n' for a,b in queries))
    answer=ROOT/'expected'/(name+'.txt');answer.write_text(''.join(str(-1 if distance[a][b]>=inf else distance[a][b])+'\n' for a,b in queries))
    cases.append({'case':name,'nodes':k,'logical_nodes':k,'ids':ids,'edges':edges,'queries':queries,'minimum_selected':minimum,'maximum_selected':maximum,'require_shared_hub':shared,'workers':list(range(1,13)),'data_folder':str(data),'expected_file':str(answer),'reference_sha256':hashlib.sha256(answer.read_bytes()).hexdigest(),'inputs_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in data.iterdir()}})
edges=[]
for node in [2,3,4]:edges += [(0,node,node+1),(node,0,node+3),(1,node,node*3+1),(node,1,node*5+2)]
edges += [(0,1,1),(1,0,4294967295),(0,0,0)]
add('d262-supp-shared-existing-routes',6,edges,[0,1,5],3,3,True)
add('d262-supp-degree2-parallel-skip',3,[(0,2,1),(0,2,9),(2,0,2),(2,0,8)],[0,1],0,0)
add('d262-supp-degree2-self-skip',3,[(0,2,1),(2,0,2),(2,2,0)],[0,1],0,0)
edges=[]
for a,b in [(0,2),(2,3),(3,4),(4,5),(5,1)]:edges += [(a,b,3),(b,a,7)]
add('d262-supp-pinned-middle-active',6,edges,[0,3,1],2,2)
lines=[str(len(cases))]
for x in cases:
    lines.append(' '.join(map(str,[x['case'],x['nodes'],x['logical_nodes'],len(x['edges']),len(x['queries']),x['minimum_selected'],x['maximum_selected'],int(x['require_shared_hub']),len(x['workers'])])))
    lines.append(' '.join(map(str,x['ids'])));lines.append(' '.join(map(str,x['workers'])))
    lines += [' '.join(map(str,row)) for row in x['edges']];lines += [' '.join(map(str,row)) for row in x['queries']]
(ROOT/'cases.txt').write_text('\n'.join(lines)+'\n');(ROOT/'cases.json').write_text(json.dumps({'official_score':False,'scope':'Additional independent originalgraph Floyd cases reaching exactdegree2duplicate/self guards and mixed pinned/active topology; original frozen model/binaries unchanged.','cases':cases},indent=2)+'\n')
print('Prepared4 focused supplemental cases,48topologyruns')
