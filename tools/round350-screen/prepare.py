from pathlib import Path
import datetime,difflib,hashlib,json,shutil,subprocess
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round350';assert not w.exists();w.mkdir();s=w/'source';s.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
proof=json.loads((r/'docs/round344-final-source-match.json').read_text());assert proof['passed'] and proof['actual_all_gates_passed'];bindings={x['path']:x['sha256'] for x in proof['inputs']};bindings['Makefile']=proof['Makefile_sha256']
for p,h in bindings.items():assert sha(r/p)==h,p
for t in 'acd':shutil.copytree(r/f'track-{t}',s/f'track-{t}')
shutil.copy2(r/'Makefile',s/'Makefile');p=s/'track-a/main.cpp';old=p.read_text();helper='''template<size_t Width,size_t Span=2,size_t Gap=1>
void small_network_layer(std::array<uint32_t,Width>& values){
    for(size_t i=0;i<Width;++i){
        size_t other=i^Gap;if(other<=i)continue;
        uint32_t a=values[i],b=values[other],low=std::min(a,b),high=std::max(a,b);
        if(i&Span){values[i]=high;values[other]=low;}else{values[i]=low;values[other]=high;}
    }
    if constexpr(Gap>1)small_network_layer<Width,Span,Gap/2>(values);
    else if constexpr(Span<Width)small_network_layer<Width,Span*2,Span>(values);
}
template<size_t Width> void small_network(uint32_t* first,size_t count){
    std::array<uint32_t,Width> values;values.fill(UINT32_MAX);std::copy_n(first,count,values.begin());
    small_network_layer(values);std::copy_n(values.begin(),count,first);
}

''';assert old.count('int main(int argc, char** argv) {')==1;new=old.replace('int main(int argc, char** argv) {',helper+'int main(int argc, char** argv) {');before='                    if (n < 32) std::sort(first, first + n);';after='''                    if(n<5)std::sort(first,first+n);
                    else if(n<=8)small_network<8>(&*first,n);
                    else if(n<=16)small_network<16>(&*first,n);
                    else if(n<32)small_network<32>(&*first,n);''';assert before in new;new=new.replace(before,after);p.write_text(new);(w/'main.cpp.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/track-a/main.cpp',tofile='b/track-a/main.cpp')))
pre={'created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_parent':subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip(),'official_score':False,'selected_in_root':False,'scope':'A350 only n5..31smallgroup ordering uses an independentlywritten generic recursive fixed-stage bitonic compare-exchange network of width8/16/32, fullunsigned32 min/max, localstack sentinelUINT32MAXpadding and exactlycount copyin/copyout. Equal realMAX values remain indistinguishable and correct, no rounded/droppedlatencies or percentilechange. n0..4and>=32originalsort/nth remain, actualnneverzero athelper. Entireparse/cache/records/escape/countryhour/count/error/output/threads/PGO/flags unchanged; no SIMDtarget/host/harness/counter/domain/catalogue/seed/outputcache/exemption changes. Branch/locality/source tradeoff hypothesis only; fresh independent fullsort/multiset/allranks/n=0..32/dense binary duplicate/uint32MAX/guard/count/precondition/strict/race/currentmain/adversarial/untrained/pinnedGCC/image/default/Make proof needed before promotion.','source_sha256':{str(q.relative_to(s)):sha(q) for q in sorted((s/'track-a').iterdir()) if q.is_file()},'control_binary':str(r/'.build/round263/final-make/track-a'),'control_binary_sha256':sha(r/'.build/round263/final-make/track-a'),'root_selected_bindings':bindings,'duplicate_check':'278smallgroupmedian+top2 changed rankselection but no sortingnetwork;191radixselect>=512/1024/4096;339nintherthreeway>=128. OwnPERF/patchgrep has no bitonic/networksmallgroups, no importedexternalimplementation.349C keptisolated andnotcombined.','primary_sources':[{'url':'https://15721.courses.cs.cmu.edu/spring2016/slides/12.pdf','scope':'Primarylecture slides on fixed bitonicmerge network compare-exchange concept, no implementationcopied and no playedvideo/performance theorem transferred.'},{'url':'https://dl.acm.org/doi/10.1145/1468075.1468121','scope':'Batcher1968 citation metadata only; publisheropenreturned403, no access workaround or paper-contentclaim.'}]}
(w/'preflight.json').write_text(json.dumps(pre,indent=2)+'\n');driver=(r/'tools/round348-screen/screen.py').read_text().replace('round348','round350').replace('A348 complete standard hash cache reuse','A350 small-group bitonic networks');(w/'screen.py').write_text(driver);shutil.copy2('/private/tmp/speed-demon-prepare350.py',w/'prepare.py');print(json.dumps({'prepared':350,'main_sha256':sha(p),'helper_lines':len(helper.splitlines()),'root_unchanged':True}))
