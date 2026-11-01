from pathlib import Path
import datetime,hashlib,json,os,subprocess,sys
r=Path.cwd();w=r/'.build/round294';source=w/'source';out=w/'native-proof';out.mkdir(exist_ok=True);read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();pre=read(w/'preflight.json');report={'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'official_score':False,'selected_in_root':False,'scope':'Fresh exact C294 packed short-length/full-length escape and56-bit membership header. Independent std::set/full-key/index/block/growth/overflow/layout/boundary models and current main strict ASAN/UBSAN/TSAN execute. New country and key-length seams exercised in actual main; parser/queue/quote primitives unchanged by bytes only. Native hypothesis is time/memory tradeoff, no target K/M/ELF/general correctness guarantee.','source_sha256':pre['source_sha256'],'model_files_sha256':pre['model_files_sha256'],'compiles':[],'models':[],'runs':[]}
env=dict(os.environ,ASAN_OPTIONS='halt_on_error=1',UBSAN_OPTIONS='halt_on_error=1:print_stacktrace=1',TSAN_OPTIONS='halt_on_error=1',PYTHONPATH=str(r/'tools'))
def save():(out/'partial.json').write_text(json.dumps(report,indent=2)+'\n')
for rel,h in pre['source_sha256'].items():assert sha(source/rel)==h
for rel,h in pre['model_files_sha256'].items():assert sha(w/rel)==h
def compile(unit,file,binary,flags):
 cmd=['clang++','-std=c++20','-O1','-g','-Wall','-Wextra','-Wpedantic','-Werror','-pthread','-fno-omit-frame-pointer',*flags,str(file),'-o',str(binary)];marker=binary.with_suffix('.compile.json')
 if marker.exists():d=read(marker);assert d['command']==cmd and d['binary_sha256']==sha(binary) and d['returncode']==0
 else:
  q=subprocess.run(cmd,capture_output=True,text=True,timeout=240);d={'unit':unit,'command':cmd,'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr};binary.with_suffix('.compile-attempt.json').write_text(json.dumps(d,indent=2)+'\n');assert q.returncode==0 and not q.stderr and not q.stdout,(unit,q.returncode,q.stderr[-2000:]);d['binary_sha256']=sha(binary);marker.write_text(json.dumps(d,indent=2)+'\n')
 report['compiles'].append(d);save()
def suite(cmd,label,path):
 if path.exists():assert read(path)['passed'];report['runs'].append({'suite':label,'command':cmd,'report':str(path.relative_to(r)),'returncode':0,'reuse':'Terminal passing sub-suite within unchanged candidate; not repeated'});save();return
 print('RUN294',label,flush=True);q=subprocess.run(cmd,capture_output=True,text=True,env=env,timeout=1000);(out/(label+'.stdout')).write_text(q.stdout);(out/(label+'.stderr')).write_text(q.stderr);report['runs'].append({'suite':label,'command':cmd,'report':str(path.relative_to(r)),'returncode':q.returncode});save();assert q.returncode==0,(label,q.returncode,q.stdout[-1800:],q.stderr[-1800:]);assert read(path)['passed']
for mode,flags in [('asan',['-fsanitize=address,undefined','-fno-sanitize-recover=all']),('tsan',['-fsanitize=thread'])]:
 folder=out/mode;folder.mkdir(exist_ok=True);model=folder/'packed-names-model';compile(mode+'-model',w/'packed_names_model.cpp',model,flags);marker=folder/'model.json'
 if marker.exists():d=read(marker);assert d['passed'] and d['binary_sha256']==sha(model)
 else:
  q=subprocess.run([str(model)],capture_output=True,text=True,env=env,timeout=300);d={'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr,'binary_sha256':sha(model),'model_files_sha256':pre['model_files_sha256']};(folder/'model-attempt.json').write_text(json.dumps(d,indent=2)+'\n');assert q.returncode==0 and not q.stderr,(mode,q.returncode,q.stdout[-1500:],q.stderr[-2000:]);d['passed']=True;marker.write_text(json.dumps(d,indent=2)+'\n')
 report['models'].append({'mode':mode,**d});save();print('PASS294',mode,'packed name model',flush=True)
 compile(mode+'-main',source/'track-c/main.cpp',folder/'track-c',flags)
 seed='3241' if mode=='asan' else '3251';path=r/f'docs/round294-c-{mode}-sample.json';suite([sys.executable,'tools/verify.py','--run-id','round294-'+mode+'-sample','--source-root',str(source),'--binary-dir',str(folder),'--tracks','c','--threads','1','6','12','--scale','sample','--seeds',seed,'--report',str(path)],mode+'-sample',path)
 path=r/f'docs/round294-c-{mode}-countries.json';code="import sys;sys.path.insert(0,'tools');import verify;verify.RUN_ID='round294-"+mode+"';import importlib.util;spec=importlib.util.spec_from_file_location('packed_countries','.build/round294/test_country_codes.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);m.main()";suite([sys.executable,'-c',code,'--binary-dir',str(folder),'--report',str(path)],mode+'-countries',path)
 for tool,label in [('test_name_pipeline.py','pipeline'),('test_cooperative_pipeline.py','topology'),('test_name_ring_pressure.py','pressure')]:
  path=r/f'docs/round294-c-{mode}-{label}.json';suite([sys.executable,'tools/'+tool,'--binary-dir',str(folder),'--run-id','round294-'+mode+'-'+label,'--report',str(path)],mode+'-'+label,path)
# Reuse independently solved inputs, never regenerate prior full screen/reference cases.
full=read(r/'.build/round293/confirmation/report.json')['cases'];fresh=read(r/'.build/round293/fresh-confirmation/report.json');assert fresh['passed'];full.append({'case':'full-seed3187','data_folder':str(r/'.data/c/full-seed3187'),'inputs_sha256':fresh['inputs_sha256'],'expected_sha256':fresh['expected_sha256']});binary=out/'asan/track-c';rows=[]
for item in full:
 data=Path(item['data_folder']);assert {p.name:sha(p) for p in data.iterdir() if p.is_file()}==item['inputs_sha256']
 for threads in [1,6,12]:
  dest=out/'full'/item['case']/str(threads);dest.mkdir(parents=True);q=subprocess.run([str(binary),'--data',str(data),'--out',str(dest)],capture_output=True,text=True,env=dict(env,SPEED_DEMON_THREADS=str(threads)),timeout=180);assert q.returncode==0 and not q.stdout and not q.stderr,(item['case'],threads,q.returncode,q.stderr);assert [p.name for p in dest.iterdir()]==['aggregates.txt'] and sha(dest/'aggregates.txt')==item['expected_sha256'];rows.append({**item,'threads':threads,'sha256':item['expected_sha256'],'binary_sha256':sha(binary)})
 assert {p.name:sha(p) for p in data.iterdir() if p.is_file()}==item['inputs_sha256']
report['full_public_untrained_runs']=rows
for rel,h in pre['source_sha256'].items():assert sha(source/rel)==h
for rel,h in pre['model_files_sha256'].items():assert sha(w/rel)==h
report.update(passed=True,completed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(r/'docs/round294-c-native-proof.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS294 native exact packed names/main proof complete',flush=True)
