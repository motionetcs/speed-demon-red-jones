from pathlib import Path
import datetime,difflib,hashlib,json,shutil,subprocess
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round373';assert not w.exists();w.mkdir();s=w/'source';s.mkdir();sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
prior=json.loads((r/'docs/round371-final-source-match.json').read_text());assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip()==prior['source_commit'];bindings={x['path']:x['sha256']for x in prior['inputs']};bindings['Makefile']=prior['Makefile_sha256']
for p,h in bindings.items():assert sha(r/p)==h,p
shutil.copytree(r/'track-d',s/'track-d');p=s/'track-d/distance_map.hpp';old=p.read_text();new=old
a='''        unsigned old_bits=bits,old_shift=11+bits;uint32_t old_mask=distance_mask();
        auto previous=std::move(labels);++bits;labels.assign(previous.size()*2,0);'''
b='''        unsigned old_bits=bits,old_shift=11+bits;uint32_t old_mask=distance_mask();
        size_t old_size=size_t(8)<<old_bits;
        std::vector<uint32_t> previous;
        if(labels.size()==old_size)previous=std::move(labels);
        else previous.assign(labels.begin(),labels.begin()+old_size);
        ++bits;
        if(labels.empty())labels.assign(old_size*2,0);
        else std::fill_n(labels.begin(),old_size*2,uint32_t(0));'''
assert a in new;new=new.replace(a,b)
a='void reset(){for(uint32_t index:touched)labels[index]=0;touched.clear();wide.reset();}'
b='''void reset(){
        for(uint32_t index:touched)labels[index]=0;
        touched.clear();wide.reset();bits=PACKED_BITS;
    }'''
assert a in new;new=new.replace(a,b);a='if(touched.size()*2>=labels.size()&&bits<20)grow();';b='if(touched.size()*2>=(size_t(8)<<bits)&&bits<20)grow();';assert a in new;new=new.replace(a,b);assert new!=old;p.write_text(new);(w/'distance_map.hpp.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/track-d/distance_map.hpp',tofile='b/track-d/distance_map.hpp')))
p=s/'track-d/README.md';old=p.read_text();new=old+'\n\nA query clears its touched labels and starts with the original logical bucket span while retaining allocated backing storage. Growth reuses that storage when it is large enough, copies only the active prefix for exact rehashing, and moves the old array when more backing storage is required. This changes lookup locality, not node identity, distance width or the full-width fallback.\n';p.write_text(new);(w/'README.md.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/track-d/README.md',tofile='b/track-d/README.md')))
scope='D373 logical packed-label bucket reset with retained backing storage: after exact touched clear, bits returns to original PACKED_BITS; slot/get/improve use that active prefix, load threshold uses8<<bits rather than physical labels.size. grow moves old storage only when physical==active (same old peak shape), otherwise snapshots active prefix then clears/reuses first2*active of larger backing array. Rehash reconstructs all original full node bits/distances and rewrites touched indices; physical size remains power-of-two>=active, enough forreuse2*active whenever physical>active. Original scalar/SSE/NEONslot, full64fallback, original epochmap, graph334/main/queue/band64/batch32/default12/PGO/ISA unchanged. No source/seed/range/answer assumptions. Need new prefix-capacity/grow/reset/overflow/fullbucket/wide/fallback/guard/stdmap/Floyd/strict/race/GNU/image/default/exact-source/real proof if native promising.'
frozen={'created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_parent':prior['source_commit'],'official_score':False,'selected_in_root':False,'scope':scope,'source_sha256':{str(p.relative_to(w)):sha(p)for p in(s/'track-d').iterdir()if p.is_file()},'root_inputs_sha256':bindings,'control_binary':str(r/'.build/round334/final-make/track-d'),'control_binary_sha256':sha(r/'.build/round334/final-make/track-d'),'duplicate_review':'68/70 shrink old full-width logical tables plus hashfold, predating packed75;83 reset-base/cap11/quarter/step always allocated a fresh smaller vector and discarded backing each shrink.373 retains current packed backing allocation and resets only active bucket bits, with explicit active-prefix rehash onregrowth. No previous retained-storage variant found in own PERF/patch indices. No old proofs transferred.'}
(w/'frozen.json').write_text(json.dumps(frozen,indent=2)+'\n');shutil.copyfile(Path(__file__),w/'prepare.py');screen=(r/'.build/round366/screen.py').read_text().replace('366','373').replace('currentbatch32/band32','retained-storage logical bucket reset');compile(screen,'screen373.py','exec');(w/'screen.py').write_text(screen)
note=scope+' Isolated one native compile/90fullhash calls screen next under shared exclusive lock; source334 control(cf0ab08...) reused, never old263D. Selected371 all30 untouched. C372 terminal native-only loser1.041927/1.068899/1.023988/1.062794, no broader proof/board; archive pending. No active duplicate work.'
(w/'ACTIVE.json').write_text(json.dumps({'status':'native_screen_prepared','selected_in_root':False,'note':note},indent=2)+'\n');p=r/'docs/STATE.md';p.write_text('# Active isolated D373 locality screen; selected371 unchanged\n\n'+note+'\n\n'+p.read_text());print('PREPARED373 logical-bucket reset retains backing; root runtime unchanged',flush=True)
