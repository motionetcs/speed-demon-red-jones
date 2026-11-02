from pathlib import Path
import datetime,difflib,hashlib,json,shutil,subprocess,tempfile
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round391';s=w/'source';a=r/'tools/round391-proof';sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();read=lambda p:json.loads(Path(p).read_text());dump=lambda p,x:Path(p).write_text(json.dumps(x,indent=2)+'\n');pre=read(w/'preflight.json');proof=read(r/'docs/round391-candidate-source-match.json');assert proof['passed']and proof['source_parent']==subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip();assert not(w/'final-source.json').exists()
for p,h in pre['unchanged_A_cpp_sha256'].items():assert sha(r/p)==sha(s/p)==h
p=s/'track-a/README.md';old=p.read_text();oldhash=sha(p);assert oldhash==pre['source_sha256']['track-a/README.md']==sha(r/'track-a/README.md')==sha(w/'submitted-source/track-a/README.md');new=old.replace('The retained163 design keeps all twelve aggregation workers.','The retained163 aggregation algorithm supports the requested worker count; current container defaults are stated below.').replace('Candidate178 changes only the first build-time PGO workload','The retained178 build changed only the first build-time PGO workload').replace('This is an unconfirmed compiler-profile experiment.','Recorded board comparisons and retained source identities are in PERF.md.');assert new!=old;shutil.copy2(p,a/'README.initial-tested.md');shutil.copy2(w/'README.md.patch',a/'initial-README.md.patch');p.write_text(new)
for target in[r/'track-a/README.md',w/'submitted-source/track-a/README.md']:target.write_text(new)
change={'path':'track-a/README.md','old_sha256':oldhash,'new_sha256':sha(p),'reason':'Correct stale historical twelve-worker/unconfirmed178 captions while documenting the proposed final-image default8. NO C++/header/Dockerfile/compiler/training/input/image change; README is not copied by the build or read by the executable. No validation reexecuted or relabeled.'};final=dict(pre);final['source_sha256']=dict(pre['source_sha256']);final['source_sha256']['track-a/README.md']=sha(p);final['tested_preflight_sha256']=sha(w/'preflight.json');final['post_validation_metadata_revision']=change;dump(w/'final-source.json',final);dump(a/'final-source.json',final);shutil.copy2(Path(__file__),w/'revise_readme.py');shutil.copy2(Path(__file__),a/'revise_readme.py')
base_text=subprocess.check_output(['git','show',pre['source_parent']+':track-a/README.md'],cwd=r).decode();patch=''.join(difflib.unified_diff(base_text.splitlines(True),new.splitlines(True),fromfile='a/track-a/README.md',tofile='b/track-a/README.md'));dest=r/'docs/prototype-patches/round391-a-runtime8-README.md.patch';dest.write_text(patch)
for row in proof['inputs']:
 if row['path']=='track-a/README.md':row['sha256']=sha(p)
proof['README_sha256']['a']=sha(p);proof['post_validation_metadata_revision']=change;proof['scope']+=' Historical README captions were corrected after validation; final-source.json binds doc-only revision, all compiled/image inputs and tests unchanged.';dump(r/'docs/round391-candidate-source-match.json',proof)
pa=read(r/'docs/round391-proof-archive.json');
for row in pa['patches']:
 if row['path']==str(dest.relative_to(r)):row['sha256']=sha(dest)
with tempfile.TemporaryDirectory(prefix='round391-final-metadata-reconstruct-')as tmp:
 base=Path(tmp)
 for path,h in final['source_sha256'].items():
  target=base/path;target.parent.mkdir(parents=True,exist_ok=True)
  if target.name=='PERF.md':shutil.copy2(a/'base-a-PERF.md',target)
  else:target.write_bytes(subprocess.check_output(['git','show',pre['source_parent']+':'+path],cwd=r))
 for row in pa['patches']:
  q=subprocess.run(['git','apply',str(r/row['path'])],cwd=base,capture_output=True,text=True);assert q.returncode==0,q.stderr
 for path,h in final['source_sha256'].items():assert sha(base/path)==h==sha(s/path)
rec=read(r/'docs/round391-archive-reconstruction.json');rec['post_validation_metadata_revision']=change;rec['scope']='Exact parent plus2 final ENV8/README patches and frozen excluded PERF reconstruct all final context files; doc-only README correction disclosed, every compiled/build/image input unchanged.';dump(r/'docs/round391-archive-reconstruction.json',rec);pa['reconstruction']=rec;pa['post_validation_metadata_revision']=change;pa['executed_drivers']={str(p.relative_to(r)):sha(p)for p in a.iterdir()if p.is_file()};dump(r/'docs/round391-proof-archive.json',pa)
for row in proof['inputs']:assert sha(r/row['path'])==row['sha256']==sha(w/'submitted-source'/row['path'])
print('REVISED391 stale README captions; exact final context reconstruction/source30 PASS; compiled source/ELF/tests unchanged')
