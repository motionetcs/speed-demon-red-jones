from pathlib import Path
import datetime,hashlib,json,os,shutil,statistics,subprocess,time,difflib
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round380-profile';assert not w.exists();w.mkdir();source=w/'source';source.mkdir();sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();read=lambda p:json.loads(Path(p).read_text());selected=read(r/'docs/round377-final-source-match.json');bindings={x['path']:x['sha256']for x in selected['inputs']};bindings['Makefile']=selected['Makefile_sha256']
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip()==selected['source_commit']
for p,h in bindings.items():assert sha(r/p)==h,p
shutil.copytree(r/'track-d',source/'track-d');p=source/'track-d/main.cpp';old=p.read_text();new=old.replace('#include <memory>','#include <memory>\n#include <chrono>')
labels=['startup_and_boundary_degree_allocation','degree_decode_and_atomic_counts','prefix_cursor_edge_allocation','scatter_decode_and_atomic_writes','prefix_release_escape_merge_queries','bidirectional_queries','output']
a='int main(int argc, char** argv) {\n    try {';b='''int main(int argc, char** argv) {
    auto phase_start = std::chrono::steady_clock::now();
    std::array<double,7> phase_seconds{}; size_t phase_index=0;
    auto phase=[&]{ auto now=std::chrono::steady_clock::now(); phase_seconds.at(phase_index++)=std::chrono::duration<double>(now-phase_start).count(); phase_start=now; };
    try {''';assert new.count(a)==1;new=new.replace(a,b)
reps=[('        DegreeBytes degree(n), reverse_degree(n);','        DegreeBytes degree(n), reverse_degree(n);\n        phase();'),('        size_t edge_count = 0;','        phase();\n        size_t edge_count = 0;'),('        auto scatter = [&]<bool Compact, bool WideCursors>() {','        phase();\n        auto scatter = [&]<bool Compact, bool WideCursors>() {'),('        Prefix().swap(offsets);Prefix().swap(reverse_offsets);','        phase();\n        Prefix().swap(offsets);Prefix().swap(reverse_offsets);'),('        auto worker = [&]<bool Compact,bool HasWide>() {','        phase();\n        auto worker = [&]<bool Compact,bool HasWide>() {'),('        Output output;','        phase();\n        Output output;'),('        output.save(paths.out / "distances.txt");','''        output.save(paths.out / "distances.txt");
        phase();
        std::fprintf(stderr,"[");
        for(size_t i=0;i<phase_seconds.size();++i)std::fprintf(stderr,i?",%.9f":"%.9f",phase_seconds[i]);
        std::fprintf(stderr,"]\\n");''')]
for a,b in reps:assert new.count(a)==1,a;new=new.replace(a,b)
p.write_text(new);(w/'main.cpp.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/track-d/main.cpp',tofile='b/track-d/main.cpp')));shutil.copy2(Path(__file__),w/'profile.py');manifest={str(p.relative_to(w)):sha(p)for p in(source/'track-d').iterdir()if p.is_file()};report={'started_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_commit':selected['source_commit'],'scope':'UNSCORED current D334 native-only phase diagnostic copy. Seven ordinary steady-clock phase boundaries, one stderr JSON emitted after output. Selected runtime unchanged; timings do not compare equal binaries or establish Intel/board, dynamic cache/call frequency, causal improvement or correctness outside exact replayed data. No new runtime algorithm, compiler/training image, generator or reference. Native copied source compiled once. Reuses only independently expected full data/reference bytes.','labels':labels,'root_inputs_sha256':bindings,'profile_source_sha256':manifest,'runs':[]}
def save():(w/'partial.json').write_text(json.dumps(report,indent=2)+'\n')
(w/'frozen.json').write_text(json.dumps(report,indent=2)+'\n');binary=w/'track-d-profile';cmd=['clang++','-std=c++20','-O3','-DNDEBUG','-Wall','-Wextra','-Wpedantic','-pthread',str(p),'-o',str(binary)];q=subprocess.run(cmd,capture_output=True,text=True,timeout=180);report['compile']={'argv':cmd,'returncode':q.returncode,'stdout':q.stdout,'stderr':q.stderr};save();assert q.returncode==0 and not q.stdout and not q.stderr,q.stderr;report['binary_sha256']=sha(binary)
cases=read(r/'.build/round378/screen/report.json')['cases'];report['cases']=cases
for case in cases:
 assert {p.name:sha(p)for p in Path(case['data_folder']).iterdir()if p.is_file()}==case['inputs_sha256']
for rep in range(3):
 for offset in range(3):
  case=cases[(rep+offset)%3]
  for threads in ([1,6,12]if(rep+offset)%2==0 else[12,6,1]):
   dest=w/'outputs'/f"{case['case']}-{threads}-{rep}";dest.mkdir(parents=True);env=dict(os.environ,SPEED_DEMON_THREADS=str(threads));start=time.perf_counter();q=subprocess.run([str(binary),'--data',case['data_folder'],'--out',str(dest)],env=env,capture_output=True,text=True,timeout=180);elapsed=time.perf_counter()-start;assert q.returncode==0 and not q.stdout,q.stderr;phases=json.loads(q.stderr);assert len(phases)==len(labels) and all(x>=0 for x in phases);assert sorted(p.name for p in dest.iterdir())==['distances.txt']and sha(dest/'distances.txt')==case['reference_sha256'];report['runs'].append({'case':case['case'],'threads':threads,'round':rep,'elapsed_including_launch_seconds':elapsed,'phases_seconds':dict(zip(labels,phases)),'output_sha256':sha(dest/'distances.txt')});save()
for case in cases:assert {p.name:sha(p)for p in Path(case['data_folder']).iterdir()if p.is_file()}==case['inputs_sha256']
for p,h in manifest.items():assert sha(w/p)==h,p
for p,h in bindings.items():assert sha(r/p)==h,p
assert sha(binary)==report['binary_sha256']
report['summary']={case['case']:{str(t):{label:statistics.median(row['phases_seconds'][label]for row in report['runs']if row['case']==case['case']and row['threads']==t)for label in labels}for t in[1,6,12]}for case in cases};report.update(passed=True,completed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());(w/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS380 phase-only diagnostics27fullhashes',json.dumps(report['summary']),flush=True)
