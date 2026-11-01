from pathlib import Path
import datetime,hashlib,json,os,random,subprocess,sys
r=Path.cwd();w=r/'.build/round286';s=w/'source';out=w/'native-proof';out.mkdir(exist_ok=True);read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();pre=read(w/'preflight.json');report={'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'official_score':False,'selected_in_root':False,'scope':'Fresh exact D286 main with querycap6, original graph loaders/requested-budget validation preserved. Actual changed main compiled once per strict ASAN/UBSAN and TSAN. Independent targeted query-count/all-budget and fresh Floyd refs plus sample/public/graph-pipeline/error cases execute. Exact original unchanged map/heap/degree/cursor/edge/numeric primitive source proofs retained, no redundant model compilation or changed-source proof relabeling. No target time/memory/K or organizer ELF claim.','source_sha256':pre['source_sha256'],'retained_primitive_inputs':pre['retained_unchanged_primitive_inputs'],'compiles':[],'runs':[],'direct_runs':[]}
def save():(out/'partial.json').write_text(json.dumps(report,indent=2)+'\n')
for rel,h in pre['source_sha256'].items():assert sha(s/rel)==h
# Generate each independent small graph and its Python Floyd result once for both strict modes and later image replays.
refbank=out/'reference-cases.json'
if refbank.exists():bank=read(refbank)
else:
 bank=[];rng=random.Random(0x286031)
 def add(label,n,edges,queries,kind,threads):
  inf=10**40;ids=sorted(set([u for u,v,a in edges]+[v for u,v,a in edges]+[u for u,v in queries]+[v for u,v in queries]));index={x:i for i,x in enumerate(ids)};d=[[0 if i==j else inf for j in range(len(ids))] for i in range(len(ids))]
  for u,v,a in edges:d[index[u]][index[v]]=min(d[index[u]][index[v]],a)
  for k in range(len(ids)):
   for i in range(len(ids)):
    for j in range(len(ids)):d[i][j]=min(d[i][j],d[i][k]+d[k][j])
  expected=''.join(str(-1 if d[index[u]][index[v]]==inf else d[index[u]][index[v]])+'\n' for u,v in queries).encode();folder=r/'.data/cases'/('round286-'+label);folder.mkdir();(folder/'graph.txt').write_text(f'{n} {len(edges)}\n'+''.join(f'{u} {v} {a}\n' for u,v,a in edges));(folder/'queries.txt').write_text(''.join(f'{u} {v}\n' for u,v in queries));bank.append({'case':folder.name,'kind':kind,'data_folder':str(folder.relative_to(r)),'inputs_sha256':{p.name:sha(p) for p in folder.iterdir()},'expected_sha256':hashlib.sha256(expected).hexdigest(),'queries':len(queries),'threads':threads})
 edges=[(0,1,0),(1,2,4294967295),(2,3,1),(0,3,4294967295),(3,1,63),(4,5,2047),(5,6,65535),(6,7,4294967295),(7,4,1),(8,9,0),(8,9,17),(9,8,1),(8,8,0),(10,11,4294967295)]
 pairs=[(0,3),(3,0),(4,4),(0,10),(5,7),(8,9),(1,7),(10,0),(7,4),(0,3),(11,10),(9,8),(2,1)]+[(i,j) for i in range(12) for j in range(12)]
 for count in [0,1,2,5,6,7,11,12,13,25]:add('query-budget-'+str(count),12,edges,pairs[:count],'query-count-and-budget',list(range(1,13)))
 add('empty-graph',0,[],[],'query-count-and-budget',list(range(1,13)))
 weights=[0,1,2,31,32,63,64,65,127,128,129,255,256,257,2046,2047,65535,4294967295]
 for number in range(256):
  n=rng.randrange(4,29);ids=rng.sample(range(65537),n);nodes=65537
  if number%64==0:ids[-1]=(1<<21)+1;nodes=(1<<21)+2
  raw=[(0,1,50),(0,2,1),(2,1,1),(1,3,1)]+[(rng.randrange(n),rng.randrange(n),rng.choice(weights)) for _ in range(rng.randrange(n,n*n//2+1))];rng.shuffle(raw);edges=[(ids[a],ids[b],c) for a,b,c in raw];queries=[(ids[i],ids[j]) for i in range(n) for j in range(n)];queries+=queries[:10];add('fresh-floyd-'+str(number),nodes,edges,queries,'fresh-floyd',[number%12+1])
 refbank.write_text(json.dumps(bank,indent=2)+'\n')
report['reference_bank_sha256']=sha(refbank);report['reference_cases']=len(bank);save()
env=dict(os.environ,ASAN_OPTIONS='halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1',TSAN_OPTIONS='halt_on_error=1',PYTHONPATH=str(r/'tools'))
def suite(cmd,label,path):
 if path.exists():assert read(path)['passed'];report['runs'].append({'suite':label,'command':cmd,'report':str(path.relative_to(r)),'returncode':0,'reuse':'Existing terminal passing sub-suite in this same unchanged candidate, no repeated invocation'});save();return
 print('RUN286',label,flush=True);q=subprocess.run(cmd,capture_output=True,text=True,env=env,timeout=1000);(out/(label+'.stdout')).write_text(q.stdout);(out/(label+'.stderr')).write_text(q.stderr);report['runs'].append({'suite':label,'command':cmd,'report':str(path.relative_to(r)),'returncode':q.returncode});save();assert q.returncode==0,(label,q.returncode,q.stdout[-1800:],q.stderr[-1800:]);assert read(path)['passed']
for mode,flags in [('asan',['-fsanitize=address,undefined','-fno-sanitize-recover=all']),('tsan',['-fsanitize=thread'])]:
 folder=out/mode;folder.mkdir(exist_ok=True);binary=folder/'track-d';marker=folder/'compile.json';cmd=['clang++','-std=c++20','-O1','-g','-Wall','-Wextra','-Wpedantic','-Werror','-pthread','-fno-omit-frame-pointer',*flags,str(s/'track-d/main.cpp'),'-o',str(binary)]
 if marker.exists():compiled=read(marker);assert compiled['command']==cmd and compiled['binary_sha256']==sha(binary) and compiled['returncode']==0
 else:
  q=subprocess.run(cmd,capture_output=True,text=True,timeout=240);compiled={'mode':mode,'command':cmd,'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr};(folder/'compile-attempt.json').write_text(json.dumps(compiled,indent=2)+'\n');assert q.returncode==0 and not q.stdout and not q.stderr,(mode,q.returncode,q.stderr[-1500:]);compiled['binary_sha256']=sha(binary);marker.write_text(json.dumps(compiled,indent=2)+'\n')
 report['compiles'].append(compiled);save()
 seed='3023' if mode=='asan' else '3041';path=r/f'docs/round286-d-{mode}-sample.json';suite(['python3','tools/verify.py','--run-id','round286-'+mode+'-sample','--source-root',str(s),'--binary-dir',str(folder),'--tracks','d','--threads','1','6','12','--scale','sample','--seeds',seed,'--report',str(path)],mode+'-sample',path)
 path=r/f'docs/round286-d-{mode}-pipeline.json';suite(['python3','tools/test_graph_pipeline.py','--binary-dir',str(folder),'--run-id','round286-'+mode+'-pipeline','--report',str(path)],mode+'-pipeline',path)
 chosen=[x for x in bank if x['kind']!='fresh-floyd' or int(x['case'].rsplit('-',1)[1])<(256 if mode=='asan' else 36)];rows=[]
 for item in chosen:
  data=r/item['data_folder'];assert {p.name:sha(p) for p in data.iterdir()}==item['inputs_sha256']
  for threads in item['threads']:
   dest=folder/'direct'/item['case']/str(threads);checkpoint=dest/'pass.json'
   if checkpoint.exists():row=read(checkpoint);assert row['binary_sha256']==sha(binary) and row['sha256']==item['expected_sha256']==sha(dest/'distances.txt');rows.append(row);continue
   dest.mkdir(parents=True);q=subprocess.run([str(binary),'--data',str(data),'--out',str(dest)],capture_output=True,text=True,env=dict(env,SPEED_DEMON_THREADS=str(threads)),timeout=90);assert q.returncode==0 and not q.stdout and not q.stderr,(mode,item['case'],threads,q.returncode,q.stderr);assert [p.name for p in dest.iterdir()]==['distances.txt'];assert sha(dest/'distances.txt')==item['expected_sha256'];row={**item,'threads':threads,'sha256':item['expected_sha256'],'binary_sha256':sha(binary),'returncode':0,'stdout':'','stderr':''};checkpoint.write_text(json.dumps(row,indent=2)+'\n');rows.append(row)
  assert {p.name:sha(p) for p in data.iterdir()}==item['inputs_sha256']
 report['direct_runs']+=rows;save();path=r/f'docs/round286-d-{mode}-query-floyd.json';path.write_text(json.dumps({'passed':True,'official_score':False,'scope':'Fresh independent Floyd references, complete all-pairs/duplicate/zero/maximum/full64/wide-ID/band-stale graphs, exact targeted q0/1/2/5/6/7/11/12/13/25 and empty graph for every requested1..12 budget. Each case generated/reference solved once and reused across strict modes. Inputs, ELF and full output hashes checked; no timing/K inference.','source_sha256':pre['source_sha256'],'binary_sha256':sha(binary),'runs':rows},indent=2)+'\n');print('PASS286',mode,'direct query/Floyd',len(rows),flush=True)
# Immutable full public and untrained full inputs execute with the new strict ASAN main; no generation/old model duplication.
compiled=read(out/'asan/compile.json');binary=out/'asan/track-d';screen=read(r/'.build/round285/screen/report.json');full=[]
for item in screen['cases']:
 data=Path(item['data_folder']);assert {p.name:sha(p) for p in data.iterdir()}==item['inputs_sha256']
 for threads in [1,6,12]:
  dest=out/'full-public-and-untrained'/item['case']/str(threads);dest.mkdir(parents=True);q=subprocess.run([str(binary),'--data',str(data),'--out',str(dest)],capture_output=True,text=True,env=dict(env,SPEED_DEMON_THREADS=str(threads)),timeout=180);assert q.returncode==0 and not q.stdout and not q.stderr,(item['case'],threads,q.returncode,q.stderr);assert [p.name for p in dest.iterdir()]==['distances.txt'];assert sha(dest/'distances.txt')==item['reference_sha256'];full.append({**item,'threads':threads,'expected_sha256':item['reference_sha256'],'sha256':item['reference_sha256'],'binary_sha256':sha(binary)})
 for p,h in item['inputs_sha256'].items():assert sha(data/p)==h
report['full_public_untrained_runs']=full
for rel,h in pre['source_sha256'].items():assert sha(s/rel)==h
report.update(passed=True,completed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(r/'docs/round286-d-native-proof.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS286 native strict/race/new query-count/Floyd/public/untrained proof complete',flush=True)
