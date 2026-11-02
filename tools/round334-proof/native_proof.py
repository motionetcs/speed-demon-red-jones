from pathlib import Path
import datetime,hashlib,json,os,random,subprocess,sys
r=Path.cwd();w=r/'.build/round334';s=w/'source';out=w/'native-proof';out.mkdir(exist_ok=True);read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();pre=read(w/'frozen.json');plan=read(w/'model-plan.json');fresh=read(w/'fresh/report.json');assert fresh['passed'];assert not (out/'report.json').exists(),'Completed proof must not be repeated'
report={'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'official_score':False,'selected_in_root':False,'scope':'Fresh exact334 joined final cursor ranges after actual mapped temporary prefix release; component against independent prefix/slot coverage, unchanged mapped allocator model freshly bound to copied D header; strict current main ASAN/UBSAN(no recovery) and TSAN on fresh samples, independent Floyd/block/query-budget/normal errors and all public/untrained full references. Header/search primitives unchanged retain source-bound original317 proof, no old changed end-range proof transferred. Native RSS/time not organizer M/K.','source_sha256':pre['source_sha256'],'candidate_Makefile_sha256':pre['candidate_Makefile_sha256'],'model_plan_sha256':sha(w/'model-plan.json'),'compiles':[],'models':[],'runs':[],'direct_runs':[]}
def save():(out/'partial.json').write_text(json.dumps(report,indent=2)+'\n')
for p,h in pre['source_sha256'].items():assert sha(w/p)==h
assert sha(s/'Makefile')==pre['candidate_Makefile_sha256'];assert sha(w/'joined_cursor_model.cpp')==plan['new_model_sha256'];assert sha(r/'tools/test_mapped_allocator.cpp')==plan['mapped_allocator_model_sha256'];save()
# One fresh reference bank, generated/solved once before either strict mode.
refbank=out/'reference-cases.json'
if refbank.exists():bank=read(refbank)
else:
 bank=[];rng=random.Random(0x334053)
 def add(label,n,edges,pairs,kind,threads):
  ids=sorted(set([u for u,v,a in edges]+[v for u,v,a in edges]+[u for u,v in pairs]+[v for u,v in pairs]));index={x:i for i,x in enumerate(ids)};inf=10**40;distance=[[0 if i==j else inf for j in range(len(ids))] for i in range(len(ids))]
  for u,v,weight in edges:distance[index[u]][index[v]]=min(distance[index[u]][index[v]],weight)
  for k in range(len(ids)):
   for i in range(len(ids)):
    for j in range(len(ids)):distance[i][j]=min(distance[i][j],distance[i][k]+distance[k][j])
  expected=''.join(str(-1 if distance[index[u]][index[v]]==inf else distance[index[u]][index[v]])+'\n' for u,v in pairs).encode();folder=r/'.data/cases'/('round334-'+label);assert not folder.exists();folder.mkdir();(folder/'graph.txt').write_text(f'{n} {len(edges)}\n'+''.join(f'{u} {v} {a}\n' for u,v,a in edges));(folder/'queries.txt').write_text(''.join(f'{u} {v}\n' for u,v in pairs));reference=out/'reference-outputs'/(label+'.txt');reference.parent.mkdir(exist_ok=True);reference.write_bytes(expected);bank.append({'case':folder.name,'kind':kind,'data_folder':str(folder.relative_to(r)),'inputs_sha256':{p.name:sha(p) for p in folder.iterdir()},'expected_sha256':hashlib.sha256(expected).hexdigest(),'reference_file':str(reference.relative_to(r)),'queries':len(pairs),'threads':threads})
 ids=[0,1,4095,4096,4097,8191,8192,8193,65535,65536,17,42];weights=[0,1,31,32,63,64,65,127,128,129,2046,2047,65534,65535,65536,4294967295]
 for number in range(128):
  count=rng.randrange(12,25);nodes=65537;used=ids.copy()
  while len(used)<count:
   x=rng.randrange(65536)
   if x not in used:used.append(x)
  if number%32==0:used[-1]=(1<<21)+1;nodes=(1<<21)+2
  raw=[(0,1,50),(0,2,1),(2,1,1),(1,3,1)]+[(rng.randrange(count),rng.randrange(count),rng.choice(weights)) for _ in range(rng.randrange(count,count*count//2+1))];rng.shuffle(raw);edges=[(used[u],used[v],a) for u,v,a in raw];pairs=[(u,v) for u in used for v in used];pairs+=pairs[:10];add('fresh-floyd-'+str(number),nodes,edges,pairs,'fresh-floyd',[number%12+1])
 edges=[(0,1,0),(1,4095,4294967295),(4095,4096,1),(4096,8193,63),(8193,0,64),(8192,8192,0)];pairs=[(u,v) for u in [0,1,4095,4096,8192,8193] for v in [0,1,4095,4096,8192,8193]]
 for count in [0,1,2,5,6,7,11,12,13,25]:add('query-budget-'+str(count),8194,edges,pairs[:count],'query-count-budget',list(range(1,13)))
 add('empty-graph',0,[],[],'query-count-budget',list(range(1,13)));refbank.write_text(json.dumps(bank,indent=2)+'\n')
report['reference_bank_sha256']=sha(refbank);report['reference_cases']=len(bank);save();env=dict(os.environ,ASAN_OPTIONS='halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1',TSAN_OPTIONS='halt_on_error=1',PYTHONPATH=str(r/'tools'))
def compile_one(cmd,binary,marker):
 if marker.exists():row=read(marker);assert row['command']==cmd and row['returncode']==0 and sha(binary)==row['binary_sha256'];return row
 assert not binary.exists(),'Inspect successful uncheckpointed binary instead of recompiling';q=subprocess.run(cmd,capture_output=True,text=True,timeout=240);row={'command':cmd,'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr};(marker.with_name(marker.stem+'-attempt.json')).write_text(json.dumps(row,indent=2)+'\n');assert q.returncode==0 and not q.stdout and not q.stderr,(q.returncode,q.stderr);row['binary_sha256']=sha(binary);marker.write_text(json.dumps(row,indent=2)+'\n');return row
def suite(cmd,label,path):
 if path.exists():assert read(path)['passed'];report['runs'].append({'suite':label,'command':cmd,'report':str(path.relative_to(r)),'returncode':0,'reuse':'Terminal passing sub-suite of same exact334 source, no repeat'});save();return
 print('RUN334',label,flush=True);q=subprocess.run(cmd,capture_output=True,text=True,env=env,timeout=1200);(out/(label+'.stdout')).write_text(q.stdout);(out/(label+'.stderr')).write_text(q.stderr);report['runs'].append({'suite':label,'command':cmd,'report':str(path.relative_to(r)),'returncode':q.returncode});save();assert q.returncode==0,(label,q.returncode,q.stdout[-1500:],q.stderr[-1500:]);assert read(path)['passed']
for mode,flags in [('asan',['-fsanitize=address,undefined','-fno-sanitize-recover=all']),('tsan',['-fsanitize=thread'])]:
 folder=out/mode;folder.mkdir(exist_ok=True);common=['clang++','-std=c++20','-O1','-g','-Wall','-Wextra','-Wpedantic','-Werror','-pthread','-fno-omit-frame-pointer',*flags]
 for name,source,defines in [('joined_cursor',w/'joined_cursor_model.cpp',[]),('mapped_allocator',r/'tools/test_mapped_allocator.cpp',['-DMAPPED_ALLOCATOR_HEADER="'+str(s/'track-d/mapped_allocator.hpp')+'"'])]:
  binary=folder/(name+'-model');compiled=compile_one([*common,*defines,str(source),'-o',str(binary)],binary,folder/(name+'-compile.json'));marker=folder/(name+'-model.json')
  if marker.exists():row=read(marker);assert row['passed'] and row['binary_sha256']==sha(binary)
  else:
   q=subprocess.run([str(binary)],capture_output=True,text=True,env=env,timeout=300);row={'compile':compiled,'binary_sha256':sha(binary),'source_sha256':sha(source),'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr};(folder/(name+'-run-attempt.json')).write_text(json.dumps(row,indent=2)+'\n');assert q.returncode==0 and not q.stderr,(mode,name,q.returncode,q.stdout[-1000:],q.stderr[-2000:]);row['passed']=True;marker.write_text(json.dumps(row,indent=2)+'\n')
  report['models'].append({'mode':mode,'name':name,**row});save();print('PASS334',mode,name,flush=True)
 binary=folder/'track-d';compiled=compile_one([*common,str(s/'track-d/main.cpp'),'-o',str(binary)],binary,folder/'compile.json');report['compiles'].append({'mode':mode,**compiled});save();seeds=['3467','3469'] if mode=='asan' else ['3481'];path=r/f'docs/round334-d-{mode}-sample.json';suite(['python3','tools/verify.py','--run-id','round334-'+mode+'-sample','--source-root',str(s),'--binary-dir',str(folder),'--tracks','d','--threads','1','6','12','--scale','sample','--seeds',*seeds,'--report',str(path)],mode+'-sample',path);path=r/f'docs/round334-d-{mode}-pipeline.json';suite(['python3','tools/test_graph_pipeline.py','--binary-dir',str(folder),'--run-id','round334-'+mode+'-pipeline','--report',str(path)],mode+'-pipeline',path)
 chosen=[x for x in bank if x['kind']!='fresh-floyd' or int(x['case'].rsplit('-',1)[1])<(128 if mode=='asan' else 32)];rows=[]
 for item in chosen:
  data=r/item['data_folder'];assert {p.name:sha(p) for p in data.iterdir()}==item['inputs_sha256'];assert sha(r/item['reference_file'])==item['expected_sha256']
  for threads in item['threads']:
   dest=folder/'direct'/item['case']/str(threads);marker=dest/'pass.json'
   if marker.exists():row=read(marker);assert row['binary_sha256']==sha(binary) and row['sha256']==item['expected_sha256']==sha(dest/'distances.txt');rows.append(row);continue
   dest.mkdir(parents=True);q=subprocess.run([str(binary),'--data',str(data),'--out',str(dest)],capture_output=True,text=True,env=dict(env,SPEED_DEMON_THREADS=str(threads)),timeout=90);assert q.returncode==0 and not q.stdout and not q.stderr,(mode,item['case'],threads,q.returncode,q.stderr);assert [p.name for p in dest.iterdir()]==['distances.txt'];assert sha(dest/'distances.txt')==item['expected_sha256'];row={**item,'threads':threads,'sha256':item['expected_sha256'],'binary_sha256':sha(binary),'returncode':0};marker.write_text(json.dumps(row,indent=2)+'\n');rows.append(row)
 report['direct_runs']+=rows;save();path=r/f'docs/round334-d-{mode}-query-floyd.json';path.write_text(json.dumps({'passed':True,'official_score':False,'scope':'Fresh independent Floyd all-pairs/duplicates/block-seam/full-width weights/wide IDs and every-budget query counts; generated/reference solved once and reused across strict modes.','source_sha256':pre['source_sha256'],'binary_sha256':sha(binary),'runs':rows},indent=2)+'\n');print('PASS334',mode,'direct/Floyd',len(rows),flush=True)
# Strict main replays of complete public and four independent full references; no generator/oracle repeat.
binary=out/'asan/track-d';screen=read(w/'screen/report.json');cases=list(screen['cases']);cases.append({'case':'full-seed3473','data_folder':fresh['data_folder'],'inputs_sha256':fresh['inputs_sha256'],'reference_sha256':fresh['expected_sha256']});full=[]
for item in cases:
 data=Path(item['data_folder']);assert {p.name:sha(p) for p in data.iterdir()}==item['inputs_sha256']
 for threads in [1,6,12]:
  dest=out/'full-public-and-untrained'/item['case']/str(threads);marker=dest/'pass.json'
  if marker.exists():row=read(marker);assert row['binary_sha256']==sha(binary) and row['sha256']==item['reference_sha256']==sha(dest/'distances.txt');full.append(row);continue
  dest.mkdir(parents=True);q=subprocess.run([str(binary),'--data',str(data),'--out',str(dest)],capture_output=True,text=True,env=dict(env,SPEED_DEMON_THREADS=str(threads)),timeout=180);assert q.returncode==0 and not q.stdout and not q.stderr,(item['case'],threads,q.returncode,q.stderr);assert [p.name for p in dest.iterdir()]==['distances.txt'];assert sha(dest/'distances.txt')==item['reference_sha256'];row={**item,'threads':threads,'expected_sha256':item['reference_sha256'],'sha256':item['reference_sha256'],'binary_sha256':sha(binary)};marker.write_text(json.dumps(row,indent=2)+'\n');full.append(row)
report['full_public_untrained_runs']=full
for p,h in pre['source_sha256'].items():assert sha(w/p)==h
assert sha(s/'Makefile')==pre['candidate_Makefile_sha256'];report.update(passed=True,completed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(r/'docs/round334-d-native-proof.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS334 native source-bound joined-cursor/allocator strict/race/main/Floyd/full proof complete',flush=True)
