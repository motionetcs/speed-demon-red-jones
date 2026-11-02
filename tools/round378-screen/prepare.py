from pathlib import Path
import datetime,difflib,hashlib,json,shutil,subprocess
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round378';assert not w.exists();w.mkdir();s=w/'source';s.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();prior=json.loads((r/'docs/round377-final-source-match.json').read_text());bindings={x['path']:x['sha256']for x in prior['inputs']};bindings['Makefile']=prior['Makefile_sha256']
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip()==prior['source_commit']
for p,h in bindings.items():assert sha(r/p)==h,p
shutil.copytree(r/'track-d',s/'track-d');p=s/'track-d/main.cpp';old=p.read_text();new=old
a='''        std::vector<const char*> boundaries(loaders + 1);
        boundaries.front() = edge_start; boundaries.back() = graph.data + graph.size;
        for (unsigned i = 1; i < loaders; ++i) {
            const char* p = edge_start + (graph.data + graph.size - edge_start) * i / loaders;'''
b='''        constexpr size_t parse_block_bytes = size_t(1) << 21;
        size_t edge_bytes = static_cast<size_t>(graph.data + graph.size - edge_start);
        size_t parts = edge_bytes / parse_block_bytes + (edge_bytes % parse_block_bytes != 0);
        std::vector<const char*> boundaries(parts + 1);
        boundaries.front() = edge_start; boundaries.back() = graph.data + graph.size;
        for (size_t i = 1; i < parts; ++i) {
            const char* p = edge_start + i * parse_block_bytes;'''
assert a in new;new=new.replace(a,b)
a='''        DegreeBytes degree(n), reverse_degree(n);
        parallel(loaders, [&](unsigned worker) {
            auto& local = locals[worker];
            Scanner input{boundaries[worker], boundaries[worker + 1]};
            std::array<std::pair<uint32_t,uint32_t>, 16> batch;
            while (input.more()) {'''
b='''        DegreeBytes degree(n), reverse_degree(n);
        std::atomic<size_t> next_part{0};
        parallel(loaders, [&](unsigned worker) {
            auto& local = locals[worker];
            std::array<std::pair<uint32_t,uint32_t>, 16> batch;
            for (;;) {
                size_t part = next_part.fetch_add(1, std::memory_order_relaxed);
                if (part >= parts) break;
                Scanner input{boundaries[part], boundaries[part + 1]};
                while (input.more()) {'''
assert a in new;new=new.replace(a,b)
a='''                for (size_t i=0;i<count;++i) { auto [u,v]=batch[i]; degree.add(u, local.out_spills); reverse_degree.add(v, local.in_spills); }
            }
        });'''
b='''                for (size_t i=0;i<count;++i) { auto [u,v]=batch[i]; degree.add(u, local.out_spills); reverse_degree.add(v, local.in_spills); }
                }
            }
        });'''
assert a in new;new=new.replace(a,b)
a='''        auto scatter = [&]<bool Compact, bool WideCursors>() {
            parallel(loaders, [&](unsigned worker) {
            auto& local = locals[worker];
            Scanner input{boundaries[worker], boundaries[worker + 1]};
            struct Row { uint32_t u, v, value, out, in; };
            std::array<Row, 16> batch;
            while (input.more()) {'''
b='''        auto scatter = [&]<bool Compact, bool WideCursors>() {
            next_part.store(0, std::memory_order_relaxed);
            parallel(loaders, [&](unsigned worker) {
            auto& local = locals[worker];
            struct Row { uint32_t u, v, value, out, in; };
            std::array<Row, 16> batch;
            for (;;) {
                size_t part = next_part.fetch_add(1, std::memory_order_relaxed);
                if (part >= parts) break;
                Scanner input{boundaries[part], boundaries[part + 1]};
                while (input.more()) {'''
assert a in new;new=new.replace(a,b)
a='''                    if(row.value >= (Compact ? EdgeStore::small_limit : uint32_t(UINT16_MAX))) { local.wide.emplace_back(row.out*2,row.value); local.wide.emplace_back(row.in*2+1,row.value); }
                }
            }
        });'''
b='''                    if(row.value >= (Compact ? EdgeStore::small_limit : uint32_t(UINT16_MAX))) { local.wide.emplace_back(row.out*2,row.value); local.wide.emplace_back(row.in*2+1,row.value); }
                }
                }
            }
        });'''
assert a in new;new=new.replace(a,b);p.write_text(new);(w/'main.cpp.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/track-d/main.cpp',tofile='b/track-d/main.cpp')))
p=s/'track-d/README.md';old=p.read_text();new=old+'\n\nEach loading pass uses the same immutable newline-aligned2MiB edge ranges. The requested loaders claim range indices from an atomic counter; that counter resets only after the first pass has joined and before the second pass launches. Degree-spill and wide-weight vectors remain private to each loader, and the original shared atomic cursor assigns every CSR slot. Query scheduling and all exact graph semantics remain unchanged.\n';p.write_text(new);(w/'README.md.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/track-d/README.md',tofile='b/track-d/README.md')))
scope='D378 dynamic2MiB newline-aligned edge jobs for BOTH existing degree and scatter passes, same requested<=12 loaders. Single immutable edge-start..EOF boundary array, one relaxed atomic counter reset between joined firstpass and secondpass launch. Per-loader count/overflowSpills/wideweight vectors persist privately across claims; original16-row scratch/atomics/CSR334/cursorfullwidth/PGO/nativeISA/default12/band64/querybatch32/full64 search unchanged. No new graph preprocessing/filter, ID/weight/seed/order shortcut, answercache or host scheduling change. Hypothesis less loader tail imbalance, not a P/E or target speed claim; new counter/job overhead may lose. If promising, require new exact coverage/passreset/partialbatch/private-spill/wrap/slotownership/weight-sidecar/largeIDs/independentFloyd/currentmain strict/race/untrained/GNU/image/default/Make/source/real proof. No A376 scheduler proof is transferred to this different parser and2pass protocol.'
pre={'created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_parent':prior['source_commit'],'official_score':False,'selected_in_root':False,'scope':scope,'source_sha256':{str(p.relative_to(w)):sha(p)for p in(s/'track-d').iterdir()if p.is_file()},'root_inputs_sha256':bindings,'control_binary':str(r/'.build/round334/final-make/track-d'),'control_binary_sha256':sha(r/'.build/round334/final-make/track-d'),'duplicate_review':'Own D PERFs/prototype indices searched.98/107 block-owned loading uses routed owner queues;152/155 private counters changesdegree representation;209 sorts decoded edges;current334 gives one static input range perloader. No dynamically claimed text subranges found. A375/376 was a distinct fused hour-record parser and lost officialK; its tests/gain hypotheses are not D proof.337 byte-relative cursors proposal matched an existing rejected trial and was stopped read-only before any new code.'}
(w/'frozen.json').write_text(json.dumps(pre,indent=2)+'\n');shutil.copy2(Path(__file__),w/'prepare.py');screen=(r/'.build/round373/screen.py').read_text().replace('373','378').replace('retained-storage logical bucket reset','dynamic edge-loading jobs');compile(screen,'screen378.py','exec');(w/'screen.py').write_text(screen)
note=scope+' Isolated one native compile/public1/6/12/3full13pair screen active next under shared inherited lock; CURRENTD334 cf0ab08...control, notold263. Root377 all30 unchanged. No new generator/oracle/model/training/image/board request. Prior376 fully restored, all previous watchers terminal. No other work active.'
(w/'ACTIVE.json').write_text(json.dumps({'status':'native_screen_prepared','selected_in_root':False,'note':note},indent=2)+'\n');p=r/'docs/STATE.md';p.write_text('# Active isolated D378 loader screen; selected377 unchanged\n\n'+note+'\n\n'+p.read_text());print('PREPARED378 dynamic two-pass loader jobs; selected source30 unchanged',flush=True)
