from pathlib import Path
import datetime,hashlib,json,shutil
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round376';s=w/'source';pre=json.loads((w/'preflight.json').read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert json.loads((w/'fresh-confirmation/report.json').read_text())['passed'];assert not(w/'partitions_extracted.hpp').exists()
main=(s/'track-a/main.cpp').read_text();a=main.index('        constexpr size_t parse_block_bytes');b=main.index('        Endpoints endpoints;',a);partition=main[a:b];needle='size_t(1) << 22';assert partition.count(needle)==1;adapted=partition.replace(needle,'Block')
begin=main.index('            for (;;) {',main.index('std::atomic<size_t> next_part'));end=main.index('                while (p < limit) {',begin);claim=main[begin:end]
header='''#pragma once
#include <atomic>
#include <cstddef>
#include <cstring>
#include <vector>
struct SplitResult {size_t parts;std::vector<const char*> boundaries;};
template<size_t Block> SplitResult split_actual(const char* data,size_t size){
    static_assert(Block>0);
    struct FileView {const char* data;size_t size;};FileView file{data,size};
    const char* end=data+size;
'''+adapted+'''    return {parts,std::move(boundaries)};
}
template<class Callback> void claims_actual(const std::vector<const char*>& boundaries,size_t parts,std::atomic<size_t>& next_part,Callback callback){
'''+claim+'''                callback(part,p,limit);
            }
}
'''
(w/'partitions_extracted.hpp').write_text(header);shutil.copyfile('/private/tmp/speed-demon-model376.cpp',w/'partitions_model.cpp');shutil.copyfile(Path(__file__),w/'prepare_proof.py')
manifest={'created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_sha256':pre['source_sha256'],'actual_main_sha256':sha(s/'track-a/main.cpp'),'extracted_partition_text_sha256':hashlib.sha256(partition.encode()).hexdigest(),'extracted_claim_text_sha256':hashlib.sha256(claim.encode()).hexdigest(),'test_adapter':'Exact partition and claim statement text from frozen main, file replaced by matching read-only FileView; block constant expression lifted to template Block. Production4MiB and smaller seam-stress constants instantiated. Claim callback replaces only unchanged record parser body; serialized-line-end oracle and exact-once membership expectations are independent. No parser, allocator, queue or file contents hidden in runtime.','model_files':{n:sha(w/n)for n in ['partitions_extracted.hpp','partitions_model.cpp']},'preparation_provenance':'Original376 preparation was one successful logged inline Python invocation, before source freeze/native compile. No saved pre-execution prepare.py exists; exact context is reproducible from371+two disclosed patches+frozen excluded PERF. This manifest was prepared after native/fresh screening; no completed work rerun.'}
(w/'partition-model-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('PREPARED376 exact extracted partition/claim model; no compiler/model execution')
