from pathlib import Path
import datetime,difflib,hashlib,json,shutil,subprocess
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round339';assert not w.exists();w.mkdir();s=w/'source';s.mkdir()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
root=json.loads((r/'docs/round334-final-source-match.json').read_text());bindings={row['path']:row['sha256'] for row in root['inputs']};bindings['Makefile']=root['Makefile_sha256'];assert root['passed'] and root['actual_all_gates_passed']
for p,h in bindings.items():assert sha(r/p)==h,p
for track in 'acd':shutil.copytree(r/f'track-{track}',s/f'track-{track}')
shutil.copy2(r/'Makefile',s/'Makefile');p=s/'track-a/main.cpp';old=p.read_text()
helper='''// Partition only intervals containing an exact requested rank; equal values settle together.
static uint32_t median_three(uint32_t a,uint32_t b,uint32_t c) {
    if(a>b)std::swap(a,b);
    if(b>c)std::swap(b,c);
    return std::max(a,b);
}
static void select_quantiles(uint32_t* data,size_t size) {
    if(!size)return;
    std::array<size_t,3> ranks{(uint64_t(size)*50+99)/100-1,(uint64_t(size)*95+99)/100-1,(uint64_t(size)*99+99)/100-1};
    auto split=[&](auto&& self,size_t low,size_t high,unsigned first,unsigned last,unsigned depth)->void {
        while(first<last){
            if(high-low<128||!depth){
                size_t next=low;
                for(unsigned k=first;k<last;++k)if(ranks[k]>=next){
                    std::nth_element(data+next,data+ranks[k],data+high);next=ranks[k]+1;
                }
                return;
            }
            size_t step=(high-low-1)/8;
            uint32_t pivot=median_three(median_three(data[low],data[low+step],data[low+2*step]),
                median_three(data[low+3*step],data[low+4*step],data[low+5*step]),
                median_three(data[low+6*step],data[low+7*step],data[high-1]));
            size_t less=low,read=low,greater=high;
            while(read<greater){
                if(data[read]<pivot){std::swap(data[less],data[read]);++less;++read;}
                else if(data[read]>pivot){--greater;std::swap(data[read],data[greater]);}
                else ++read;
            }
            unsigned middle=first;while(middle<last&&ranks[middle]<less)++middle;
            unsigned right=middle;while(right<last&&ranks[right]<greater)++right;
            if(first<middle)self(self,low,less,first,middle,depth-1);
            low=greater;first=right;--depth;
        }
    };
    split(split,0,size,0,3,2*std::bit_width(size));
}

'''
new=old.replace('#include <numeric>','#include <numeric>\n#include <bit>').replace('int main(int argc, char** argv) {',helper+'int main(int argc, char** argv) {').replace('if (n < 32) std::sort(first, first + n);\n                    else {','if (n < 32) std::sort(first, first + n);\n                    else if(n>=128)select_quantiles(&*first,static_cast<size_t>(n));\n                    else {');assert new.count('static void select_quantiles')==1 and new.count('else if(n>=128)')==1;p.write_text(new)
patch=''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/track-a/main.cpp',tofile='b/track-a/main.cpp'));(w/'main.cpp.patch').write_text(patch)
pre={'created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_parent':subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip(),'official_score':False,'selected_in_root':False,'scope':'A339 exact in-place comparison multiselection for groups>=128: bounded median-of-three-of-three pivot, full uint32 three-way partition, skip equality-settled requested nearest50/95/99 ranks, recurse only requested intervals with depth2*bit_width then original progressively restricted nth_element fallback. Groups<32 sort and32..127 original nth sequence unchanged. No copied algorithm implementation, approximate percentile, input/seed/catalogue/cached answer, narrowed values, new buffer, host/harness/timer/counter/exemption change. Original parser/endpoint/4byte+full32 escapes/output/flags/defaults/PGO remain. Native current233 diagnostic motivates aggregate phase only; no causal phase gain presumed. Fresh rank/full-sort/multiset/duplicates/extreme/guard/depth-fallback/currentmain strict/race/untrained/GCC/image/default/Make proof required if screen supports.','source_sha256':{str(q.relative_to(s)):sha(q) for q in sorted((s/'track-a').iterdir()) if q.is_file()},'control_binary':str(r/'.build/round263/final-make/track-a'),'control_binary_sha256':sha(r/'.build/round263/final-make/track-a'),'original_main_sha256':sha(r/'track-a/main.cpp'),'original_header_sha256':sha(r/'track-a/endpoint_table.hpp'),'root_selected_bindings':bindings,'duplicate_check':'191 uses radix histograms/shared byte-prefix refinement at512/1024/4096 and was flat;278 specializes n4..31 with median/top-two and was flat.339 new full-width comparison partition/equal intervals/ninther/depth fallback at>=128, no histogram or small-group change. No prior same comparison multi-rank candidate found in own PERF.','primary_concepts':['https://ocw.mit.edu/courses/6-046j-introduction-to-algorithms-sma-5503-fall-2005/c0fb16b38fa759cef295c7b3da11cb4f_mR_RUjsJnV8.pdf'],'primary_scope':'Primary MIT lecture6 video transcript text inspected on order-statistic partition/rank recursion and duplicate caveat, not played-video claim.339 independently written deterministic sampled pivot/multiple-rank/equal/depth variant, no lecture expected/worst-case linear theorem transferred. First attempted 2015 lecture5 URL unavailable; actual 2005 transcript used.'}
(w/'preflight.json').write_text(json.dumps(pre,indent=2)+'\n');driver=(r/'tools/round336-screen/screen.py').read_text().replace('round336','round339').replace('A336 direct-slot second-chance admission','A339 comparison multiselection');(w/'screen.py').write_text(driver);shutil.copy2('/private/tmp/speed-demon-prepare339.py',w/'prepare.py');print(json.dumps({'prepared':str(w),'root_unchanged':True,'candidate_main_sha256':sha(p),'helper_lines':len(helper.splitlines())}))
