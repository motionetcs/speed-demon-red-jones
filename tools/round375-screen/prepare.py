from pathlib import Path
import datetime,difflib,hashlib,json,shutil,subprocess
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round375';assert not w.exists();w.mkdir();s=w/'source';s.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prior=json.loads((r/'docs/round371-final-source-match.json').read_text());assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip()==prior['source_commit'];bindings={x['path']:x['sha256']for x in prior['inputs']};bindings['Makefile']=prior['Makefile_sha256']
for p,h in bindings.items():assert sha(r/p)==h,p
shutil.copytree(r/'track-a',s/'track-a');p=s/'track-a/main.cpp';old=p.read_text();new=old
a='''        std::vector<const char*> boundaries(threads + 1);
        boundaries.front() = file.data; boundaries.back() = end;
        for (unsigned i = 1; i < threads; ++i) {
            const char* p = file.data + file.size * i / threads;'''
b='''        constexpr size_t parse_block_bytes = size_t(1) << 20;
        size_t parts = (file.size + parse_block_bytes - 1) / parse_block_bytes;
        std::vector<const char*> boundaries(parts + 1);
        boundaries.front() = file.data; boundaries.back() = end;
        for (size_t i = 1; i < parts; ++i) {
            const char* p = file.data + i * parse_block_bytes;'''
assert a in new;new=new.replace(a,b)
a='''        parallel(threads, [&](unsigned worker) {
            const char* p = boundaries[worker]; const char* limit = boundaries[worker + 1];
            auto& chunk = chunks[worker];
            LocalEndpoints local_names(endpoints);
            size_t reserve_hint = (limit - p) / (72 * 64);
            while (p < limit) {'''
b='''        std::atomic<size_t> next_part{0};
        parallel(threads, [&](unsigned worker) {
            auto& chunk = chunks[worker];
            LocalEndpoints local_names(endpoints);
            size_t reserve_hint = (file.size / threads) / (72 * 64);
            for (;;) {
                size_t part = next_part.fetch_add(1, std::memory_order_relaxed);
                if (part >= parts) break;
                const char* p = boundaries[part]; const char* limit = boundaries[part + 1];
                while (p < limit) {'''
assert a in new;new=new.replace(a,b)
a='''                if (latency >= latency_escape) chunk.wide[hour].push_back(static_cast<uint32_t>(latency));
            }
        });'''
b='''                if (latency >= latency_escape) chunk.wide[hour].push_back(static_cast<uint32_t>(latency));
                }
            }
        });'''
assert a in new;new=new.replace(a,b);p.write_text(new);(w/'main.cpp.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/track-a/main.cpp',tofile='b/track-a/main.cpp')))
p=s/'track-a/README.md';old=p.read_text();new=old+'\n\nParsing uses newline-aligned ranges at1MiB byte intervals. The same requested workers claim range indices from one atomic counter, retaining private hour vectors and endpoint caches across claims. Each range is claimed once; overlapping newline searches produce equal boundaries and harmless empty ranges. No record is skipped or processed twice. This is a shared task counter, not a work-stealing deque or a host scheduling change.\n';p.write_text(new);(w/'README.md.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/track-a/README.md',tofile='b/track-a/README.md')))
scope='A375 replaces12 static parser input ranges with1MiB newline-aligned ranges dynamically claimed by the SAME requested workers through atomic<size_t>::fetch_add(relaxed). One immutable boundary array built before thread launch covers entire actual file; equal boundaries give empty jobs. Private Chunk/hour/wideescape vectors and LocalEndpoints cache retained per worker across jobs; original average per-worker byte estimate (file.size/threads)/(72*64) for initial reserve, not rejected374reserve512. Every fetch index unique/increasing perworker, no wrap under existinguint32 file-size guard; firstline positions stay earliest in each owned hour. Original rows/methods/hours/status/full32latencies/endpoints/quantiles/output/12thread limit/flags/PGO unchanged. Hypothesis reduced end-of-parse imbalance, with possible extra allocations/private-hour fragmentation/atomic overhead. No claimed P/E-core cause, affinity/host/harness/counter change, seed/order/recordcount assumption or cached answers. Need new exact-once partition/empty/equal-boundary/truncation/overflow/guard/privateownership/errorjoin/source-specific main strict/race/independent/adversarial/untrained/GNU/image/default/Make/source/real proof if promising.'
pre={'created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_parent':prior['source_commit'],'official_score':False,'selected_in_root':False,'scope':scope,'source_sha256':{str(p.relative_to(s)):sha(p)for p in(s/'track-a').iterdir()if p.is_file()},'root_selected_bindings':bindings,'control_binary':str(r/'.build/round263/final-make/track-a'),'control_binary_sha256':sha(r/'.build/round263/final-make/track-a'),'duplicate_review':'Own A PERFs and prototype indices searched. Original parallel uses exactlyone contiguous static range/worker;264 two/four independent cursors use fixed ranges perworker for latency hiding;296 fixed recordblocks changes storage;236/241 dynamic hour/output scheduling is downstream. No prior dynamically claimed parser subranges found. No other implementation copied, no old scheduler/model proof transferred.','public_research':{'primary_documentation':'https://eel.is/c++draft/atomics.types.operations','video_metadata_only':'https://gotopia.tech/experts/573/roy-van-rijn','video_metadata_scope':'Organizer lists billion-row file parsing talks. Direct CppCon2017 YouTube fetch failed; no watched-video or transcript claim and no technical result inferred from third-party talk summaries.'}}
(w/'preflight.json').write_text(json.dumps(pre,indent=2)+'\n');shutil.copyfile(Path(__file__),w/'prepare.py');screen=(r/'.build/round374/screen.py').read_text().replace('374','375').replace('initial mapped reserve512','dynamic newline-aligned parser jobs');compile(screen,'screen375.py','exec');(w/'screen.py').write_text(screen)
note=scope+' Isolatedonecompile/90nativefullhashcalls next sharedlock. C372,D373 rejectedclear native losses; A374 reserve512weak/mixed.981225/.991222/1.002044,RSS+0.23–0.36MB, native-only reject beforebroader proof. Exactarchivespending. Rootoriginal371 all30 untouched; no generator/oracle/model/PGO or boardwork active.'
(w/'ACTIVE.json').write_text(json.dumps({'status':'native_screen_prepared','selected_in_root':False,'note':note},indent=2)+'\n');p=r/'docs/STATE.md';p.write_text('# Active isolated A375 dynamic-parser screen; original371 selected\n\n'+note+'\n\n'+p.read_text());print('PREPARED375 dynamic newline jobs; selected runtime unchanged',flush=True)
