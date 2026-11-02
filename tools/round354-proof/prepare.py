from pathlib import Path
import datetime,difflib,hashlib,json,shutil,subprocess
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round354';assert not w.exists();w.mkdir();s=w/'source';s.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
proof=json.loads((r/'docs/round353-final-source-match.json').read_text());assert proof['passed']and proof['actual_all_gates_passed'];bindings={x['path']:x['sha256']for x in proof['inputs']};bindings['Makefile']=proof['Makefile_sha256']
for p,h in bindings.items():assert sha(r/p)==h,p
for t in 'acd':shutil.copytree(r/f'track-{t}',s/f'track-{t}')
shutil.copy2(r/'Makefile',s/'Makefile');patches={};p=s/'track-c/names.hpp';old=p.read_text();start=old.index('// One producer and one consumer');new=old[:start]+'''// One owner epoch covers all its input queues; waits cannot miss a publication.
struct alignas(64) NameWake {
    std::atomic<uint64_t> epoch{0};
    void signal(){epoch.fetch_add(1,std::memory_order_release);epoch.notify_one();}
};
// Queue state2 is sticky cancellation. Only0->1 publication and1->0 retirement
// use CAS, so neither can overwrite cancellation or permit premature reuse.
struct NameQueue {
    alignas(64) std::atomic<unsigned> state{0};std::vector<NameEvent> rows;
    void send(std::vector<NameEvent>& batch,const std::atomic<bool>& canceled,NameWake& wake){
        unsigned observed=state.load(std::memory_order_acquire);
        while(observed==1){
            if(canceled.load(std::memory_order_acquire))throw std::runtime_error("name pipeline canceled");
            state.wait(1,std::memory_order_acquire);observed=state.load(std::memory_order_acquire);
        }
        if(observed==2||canceled.load(std::memory_order_acquire))throw std::runtime_error("name pipeline canceled");
        rows.swap(batch);unsigned empty=0;
        if(!state.compare_exchange_strong(empty,1,std::memory_order_acq_rel,std::memory_order_acquire))throw std::runtime_error("name pipeline canceled");
        wake.signal();
    }
    void retire(){unsigned full=1;state.compare_exchange_strong(full,0,std::memory_order_release,std::memory_order_relaxed);state.notify_one();}
    void cancel(){state.store(2,std::memory_order_release);state.notify_all();}
};
''';p.write_text(new);patches['names.hpp']=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/track-c/names.hpp',tofile='b/track-c/names.hpp'))
p=s/'track-c/main.cpp';old=p.read_text();new=old
before='        std::atomic<bool> canceled{false};';after='''        std::atomic<bool> canceled{false};auto wakes=std::make_unique<NameWake[]>(owners);
        auto cancel_pipeline=[&]{
            canceled.store(true,std::memory_order_release);
            for(size_t i=0;i<size_t(readers)*owners;++i)queues[i].cancel();
            for(unsigned i=0;i<owners;++i)wakes[i].signal();
        };''';assert new.count(before)==1;new=new.replace(before,after)
assert new.count('.send(batch,canceled)')==3;new=new.replace('.send(batch,canceled)','.send(batch,canceled,wakes[owner])')
before='''                        while(remaining){
                            if(canceled.load(std::memory_order_relaxed))throw std::runtime_error("name pipeline canceled");''';after='''                        while(remaining){
                            uint64_t stamp=wakes[owner].epoch.load(std::memory_order_acquire);
                            if(canceled.load(std::memory_order_acquire))throw std::runtime_error("name pipeline canceled");''';assert new.count(before)==1;new=new.replace(before,after)
before='''                                if(finished[reader])continue;auto& queue=queues[size_t(reader)*owners+owner];
                                if(!queue.ready.load(std::memory_order_acquire))continue;progress=true;''';after='''                                if(finished[reader])continue;
                                auto& queue=queues[size_t(reader)*owners+owner];
                                unsigned state=queue.state.load(std::memory_order_acquire);
                                if(state==2)throw std::runtime_error("name pipeline canceled");
                                if(state!=1)continue;
                                progress=true;''';assert new.count(before)==1;new=new.replace(before,after)
assert new.count('queue.rows.clear();queue.ready.store(false,std::memory_order_release);')==1;new=new.replace('queue.rows.clear();queue.ready.store(false,std::memory_order_release);','queue.rows.clear();queue.retire();')
assert new.count('if(!progress)std::this_thread::yield();')==1;new=new.replace('if(!progress)std::this_thread::yield();','if(!progress&&remaining)wakes[owner].epoch.wait(stamp,std::memory_order_acquire);')
assert new.count('}catch(...){canceled.store(true,std::memory_order_relaxed);throw;}')==1;new=new.replace('}catch(...){canceled.store(true,std::memory_order_relaxed);throw;}','}catch(...){cancel_pipeline();throw;}');assert 'queue.ready'not in new and 'fno-unroll'not in(s/'track-c/Dockerfile').read_text();p.write_text(new);patches['main.cpp']=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/track-c/main.cpp',tofile='b/track-c/main.cpp'))
for name,patch in patches.items():(w/(name+'.patch')).write_text(patch)
pre={'created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_parent':subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip(),'official_score':False,'selected_in_root':False,'scope':'C354 standardC++20 wait/notify ONLY at boundedSPSC batch boundaries. Producers wait on fullstate1; owners captureperowneruint64epoch BEFORE cancellationcheck/queue scans and waitonunchangedepoch onlyafterallchannelsidle. Publishsignalsowner; retirementnotifiesproducer. Queue states0empty/1full/2STICKYcancel, publicationCAS0->1 andretireCAS1->0 canNEVERoverwrite2. Cancelrelease setsglobaltrue, cancelsALLqueues withvaluechange+notifyall, then incrementsALLownerepochs; no reset-to-empty cancellation race/lostwake. Onlyoneproducer/consumer ofeachvector; no produceraccess afterobserving2, currentconsumer mayfinishbatchbeforejoining. ExistingexactNames/512batch/EOF/order/readers8+owners4/default12/serial1/parser/country/fullwidth/PGO/flags stay. Runtimewakeepochs are ordinarysyncstate, not board/harnesscounters. Hypothesis reduceOSyieldpolling/SMTresourcecontention atpossibleblocking/extraCAS/notifycost; nativeApple stdlib differsfromLinux, no targetgainclaim. Fullfreshmodel requiredforpostcheck/prepublish/prewait/activeconsume/cancel/EOF/failures/everytopology/epochwrap/ordering/ownership/race/failfaststrict/untrained/pinnedGCC/exactimage/default/Make beforepromotion. No seed/catalogue/outputcache/harness/host/affinity/counter/tunable/defaultbudget/exemption changes.','source_sha256':{str(q.relative_to(s)):sha(q)for q in sorted((s/'track-c').iterdir())if q.is_file()},'control_binary':str(r/'.build/round263/final-make/track-c'),'control_binary_sha256':sha(r/'.build/round263/final-make/track-c'),'root_selected_bindings':bindings,'duplicate_check':'95boundedPAUSE/spin128 stillpolls/yields andactualfailed;151boundedringcapacity/155pooledMPSC/133cooperativeowner work differ andfailed. Old45atomicwait belongsAextraorderedwriter, notCboundedproducer/owneridle. OwnCPERF/patchsearchhasnoCatomicwait/notify/stickycancel/owner-epoch trial. Do nottransferoriginalbool-readyqueue models or old45/95proof. 352compilerflagsfullyrestored, no newcompilerflag in354.','primary_sources':[{'url':'https://eel.is/c++draft/atomics.wait','scope':'Primary standard waiting/notifying semantics and transientvalueABA caveat. No copiedimplementation or guaranteed speed. Stickycancelpreventsunobservedterminalcondition overwrite; perowner counter snapshot andsignalafterpublish requirefreshactualmodels.'},{'url':'https://15721.courses.cs.cmu.edu/spring2024/slides/09-hashjoins.pdf','scope':'Primarylecture synchronization/cachetradeoffs only, no copiedqueuealgorithm/performance claim.'}]}
(w/'preflight.json').write_text(json.dumps(pre,indent=2)+'\n');driver=(r/'tools/round349-screen/screen.py').read_text().replace('round349','round354').replace('C349 register-sized field return','C354 atomic batch waits');(w/'screen.py').write_text(driver);shutil.copy2('/private/tmp/speed-demon-prepare354.py',w/'prepare.py');print(json.dumps({'prepared':354,'main_sha256':sha(s/'track-c/main.cpp'),'header_sha256':sha(s/'track-c/names.hpp'),'root_unchanged':True}))
