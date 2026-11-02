from pathlib import Path
import datetime, hashlib, json, shutil, subprocess, tempfile
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round393';read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
pre=read(w/'preflight.json');rep=read(w/'confirmation/report.json');parent=pre['source_parent']
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip()==parent
assert rep['passed']and len(rep['runs'])==118
assert all(sha(r/p)==h for p,h in pre['root_selected_bindings'].items())
assert all(sha(w/'source'/p)==h for p,h in pre['source_sha256'].items())
a=r/'tools/round393-screen';assert not a.exists();a.mkdir()
for name,src in [('prepare.py',w/'prepare.py'),('screen.py',w/'screen.py'),('close.py',Path(__file__)),('preflight.json',w/'preflight.json'),('report.json',w/'confirmation/report.json'),('compile.json',w/'compile.json'),('base-c-PERF.md',w/'source/track-c/PERF.md')]:shutil.copy2(src,a/name)
patches=[]
for p in sorted(w.glob('*.patch')):
 dest=r/('docs/prototype-patches/round393-c-deferred-'+p.name);shutil.copy2(p,dest);patches.append({'path':str(dest.relative_to(r)),'sha256':sha(dest)})
with tempfile.TemporaryDirectory(prefix='round393-reconstruct-')as tmp:
 base=Path(tmp)
 for p in pre['source_sha256']:
  dest=base/p;dest.parent.mkdir(parents=True,exist_ok=True)
  if dest.name=='PERF.md':shutil.copy2(a/'base-c-PERF.md',dest)
  else:dest.write_bytes(subprocess.check_output(['git','show',parent+':'+p],cwd=r))
 for row in patches:
  q=subprocess.run(['git','apply',str(r/row['path'])],cwd=base,capture_output=True,text=True);assert q.returncode==0,q.stderr
 assert all(sha(base/p)==h for p,h in pre['source_sha256'].items())
summary={n:{'paired_median_ratio':x['paired_median_ratio'],'paired_wins':x['paired_wins'],'native_rss_delta_bytes':x['variants']['candidate']['median_native_rss_bytes']-x['variants']['control']['median_native_rss_bytes']}for n,x in rep['summary'].items()}
limits='Post-EOF owner-private reduction is slower/flat on all four full inputs:1.013720/1.034520/1.000917/1.031445 (5/0/5/2wins). Small native RSS reductions do not establish chargedM/Intel/totalK. REJECT before new padding-zero/last-word/collision/empty/grow/index/stdset/allwidth/guard/countconservation/privateowner/lifetime models, strict/race/untrained/GNU/image/default/actual proof. Unchanged Names::first/queue/parser provenance is not a correctness certificate for new reduction. No seed/domain-bound or target cause is inferred.'
(a/'README.md').write_text('# C393: rejected after native screening\n\n'+pre['scope']+'\n\n'+limits+'\n\n'+pre['duplicate_review']+'\n\nPrimary conceptual standard: https://timsong-cpp.github.io/cppwp/n4861/bit.count ; frozen official spec hash in preflight. No competitor or library implementation imported.\n')
result={'observed_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'decision':'REJECT_NATIVE_ONLY','scope':pre['scope'],'source_parent':parent,'selected_in_root':False,'official_score':False,'summary':summary,'runs':len(rep['runs']),'limitations':limits,'duplicate_review':pre['duplicate_review'],'patches':patches,'frozen_source_sha256':pre['source_sha256'],'reconstruction_passed':True,'reconstructed_file_count':len(pre['source_sha256']),'files':{str(p.relative_to(r)):sha(p)for p in a.iterdir()if p.is_file()}}
dump(r/'docs/round393-c-deferred-counts-screen.json',result);dump(w/'ACTIVE.json',{'status':'rejected_native_only','no_active_work':True,'summary':summary,'limitations':limits})
p=r/'track-c/PERF.md';p.write_text(p.read_text()+'\n\nC393 owner-private post-EOF membership materialization: REJECT_NATIVE_ONLY. '+json.dumps(summary,sort_keys=True)+'. '+limits+' Onecompile118calls, fullpublic1/6/12 and13rotating4fulls, all before/after source/ELF/input/output hashesPASS. Explicit materially new layout retest of historical shared/private-membership2 concept; stopped exact conditional per-row counter338 duplicate before new code/compile. No selected runtime or board action. Exact docs/round393-c-deferred-counts-screen.json/tools/round393-screen.\n')
p=r/'docs/STATE.md';state=p.read_text();i=state.index('# Original392 real-confirmed; no active jobs');state=state[i:];state=state.replace('Next fresh round393 only if materially novel idea and enough time;','Next fresh round394 only if materially novel idea and enough time;');state=state.replace('through392 terminal;','through393 terminal;');state=state.replace('C384 prior four-word specialization', '393 C deferred owner-private counts REJECT_NATIVE_ONLY .1.013720/1.034520/1.000917/1.031445 with5/0/5/2wins; modest nativeRSS reductions, no target/generic correctness claim, no further proof or actual trial. Fullpublic1/6/12+fourfull13pairs/118calls all hashesPASS. Archive/source reconstruction all10 filesPASS. Duplicate338 conditional counter idea stopped before implementation; historical2 shared/private-membership reduction differs materially and was disclosed as a retest, no old proof reused. Exact docs/round393-c-deferred-counts-screen.json/tools/round393-screen.\n\nC384 prior four-word specialization');state=state.replace('counts REJECT_NATIVE_ONLY .1.013720','counts REJECT_NATIVE_ONLY 1.013720');p.write_text(state)
p=r/'docs/RESULTS.md';p.write_text(p.read_text()+'\nC393 owner-private post-EOF distinct-count materialization was rejected after native full-reference screening: ratios1.013720/1.034520/1.000917/1.031445 with5/0/5/2wins. Smaller native RSS did not establish a target gain. No selected source/image/board change or broad strict/general correctness proof is claimed. Exact source/reconstruction/drivers: round393-c-deferred-counts-screen.json and tools/round393-screen.\n')
# Replace outdated round281 executive tables, preserving the exact old captions.
proof=read(r/'docs/round392-final-source-match.json');actual=read(r/'docs/board-round392-original-restored.json');old_summaries={}
descriptions={
 'a':'One-pass request parsing produces exact four-byte endpoint/error/latency records with full32-bit latency escapes. Hour owners count/scatter and select exact nearest-rank percentiles. Full endpoint bytes resolve hash collisions. Mapped record/output buffers release completed-hour storage; ordered output and the bounded decimal decoder are retained. Twelve-worker production default is restored; rejected391 final ENV8 is absent.',
 'c':'Quote-aware CSV readers compute exact integer-cent country aggregates and route canonical name bytes through bounded512-event SPSC vectors to private hash owners. Every full key decides equality; exact dynamic country bitmaps record distinct membership. Offset arenas keep complete keys stable. Default topology is eight readers/four owners; one worker uses the exact serial path. Rejected384 four-word specialization and393 deferred counters are absent.',
 'd':'Two directed CSR graphs retain every node, edge and full weight through exact inline/escape storage. Query-owned bidirectional64-bit search uses full-ID packed labels with exact wide fallback and conservative whole-batch bounds. Retained334 unmapped temporary prefixes and reused exact final joined cursors as read-only CSR ends. Band64/batch32/default12 remain. Rejected filters, smaller map capacity and degree-two bypass are absent.'}
for t in 'acd':
 p=r/('track-'+t)/'PERF.md';text=p.read_text();marker='## Historical experiments';assert marker in text;index=text.index(marker);old_summaries[t]=text[:index];best=proof['best_records'][t];latest=actual['tracks'][t]
 title='# Track '+t.upper()+' optimization log\n\n## Selected implementation and measured records\n\n'+descriptions[t]+'\n\n'
 title+='Selected passing source: `'+parent+'` (**A178/C175/D334**). Exact runtime/build/input and replay-image bindings: [round392-final-source-match.json](../docs/round392-final-source-match.json). Local images identify our replays, not organizer executables.\n\n'
 title+='| Record | Run ID | T seconds | Charged memory bytes | S | K | Machine points |\n| --- | --- | ---: | ---: | ---: | ---: | ---: |\n'
 for label,x in [('Historical best',best),('Latest passing392',latest)]:title+=f"| {label} | {x['run_id']} | {x['T_s']} | {x['M_bytes']} | {x['S']} | {x['K']} | {x['points']} |\n"
 title+='\nEvery check/build/correctness/timeout/sandbox gate passed for these records. Historical best and unchanged-source repeat variation stay separate. Native Apple timing/process RSS and emulated Linux correctness do not establish Intel timing or charged memory. No final holdout, judging, eligibility, personal understanding, prize or victory guarantee is made. [Current combined results and leader comparison](../docs/RESULTS.md), [real latest records](../docs/board-round392-original-restored.json).\n\n'
 title+='The chronological log below preserves successful and rejected experiments as recorded, including historical defaults and provisional decisions that later entries supersede. Its earlier statements are dated experiment context. The previous round281 executive captions are preserved verbatim in tools/round393-screen/prior-executive-summaries.json; the current records above replace those stale captions.\n\n'
 p.write_text(title+text[index:])
dump(a/'prior-executive-summaries.json',old_summaries)
result['files']={str(p.relative_to(r)):sha(p)for p in a.iterdir()if p.is_file()};result['report_cleanup']='Replaced stale round281 executive best/latest tables in all3 PERF logs using verified392 and historical-best records; exact previous captions archived. Chronological measurements and executed proof remain unchanged. This is report metadata only; all30 runtime/build inputs/Make/trackREADME/fullsets remain exact392.';dump(r/'docs/round393-c-deferred-counts-screen.json',result)
assert all(sha(r/p)==h for p,h in pre['root_selected_bindings'].items())
assert subprocess.run(['git','diff','--check'],cwd=r,capture_output=True,text=True).returncode==0
print('C393 REJECTED and fully archived; all30 passing392 runtime/Make unchanged; stale PERF executive tables corrected from verified records',flush=True)
