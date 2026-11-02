from pathlib import Path
import datetime,hashlib,json,shutil,subprocess
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round395';s=w/'source';read=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):Path(p).write_text(json.dumps(x,indent=2)+'\n')
assert not(w/'proof-plan.json').exists();m=read(w/'frozen.json');initial=read(w/'screen/report.json');fresh=read(w/'untrained-confirmation/report.json');assert initial['passed']and fresh['passed']and fresh['paired_median_ratio']<1 and fresh['paired_wins']==13
assert all(sha(w/p)==h for p,h in m['source_sha256'].items());assert all(sha(r/p)==h for p,h in m['root_inputs_sha256'].items())
# Exact inverse substitutions prove that no data address, load/store or protocol changed.
inverse={
 'main.cpp':[('__builtin_prefetch(&degree.values[u], 0, 3); __builtin_prefetch(&reverse_degree.values[v], 0, 3);','__builtin_prefetch(&degree.values[u], 1, 1); __builtin_prefetch(&reverse_degree.values[v], 1, 1);',1)],
 'load_cursors.hpp':[('], 0, Write ? 3 : 1);','], Write ? 1 : 0, 1);',2)],
 'edge_store.hpp':[('], 0, Write ? 3 : 1);','], Write, 1);',2)]}
for name,changes in inverse.items():
 text=(s/'track-d'/name).read_text()
 for a,b,n in changes:assert text.count(a)==n;text=text.replace(a,b)
 assert text==(r/'track-d'/name).read_text(),name
for p in(s/'track-d').iterdir():
 if p.is_file()and(p.suffix in['.cpp','.hpp']or p.name in['Dockerfile','training_generator.py','.speed-demon.toml'])and p.name not in inverse:assert sha(p)==sha(r/'track-d'/p.name)
shutil.copy2(r/'Makefile',s/'Makefile')
# Use only saved fixture/reference bytes, then execute the exact changed code freshly.
base=read(r/'docs/round334-d-linux-image.json');assert base['passed'];rows={};errors={};folders={}
for row in base['runs']:
 p=row['data_folder'];name=row['case']
 selected='round334-'in name or name in ['sample-seed3467','sample-seed3469','sample-seed3481','public-full-seed1','full-seed1823','full-seed2633','full-seed3473']
 if not selected:continue
 h=row['inputs_sha256'];key=(tuple(sorted(h.items())),row['threads']);old=rows.get(key);expected=row.get('expected_sha256')or row['sha256']
 if old:assert old['expected_sha256']==expected
 rows[key]={'case':name,'data_folder':p,'threads':row['threads'],'inputs_sha256':h,'expected_sha256':expected,'reference_source':'docs/round334-d-linux-image.json saved inputs/expected bytes only; no old changed-code pass reused'};folders[p]=h
for row in base['expected_failures']:
 h=row['inputs_sha256'];key=(tuple(sorted(h.items())),row['threads']);errors[key]={'case':row['case'],'data_folder':row['data_folder'],'threads':row['threads'],'inputs_sha256':h,'expected_returncode':1,'reference_source':'docs/round334-d-linux-image.json saved malformed-input bytes only'};folders[row['data_folder']]=h
for p,h in folders.items():assert {q.name:sha(q)for q in(r/p).iterdir()if q.is_file()}==h,p
bank={'scope':'Input-content/thread deduplicated saved independent Floyd all-pairs, query counts/every-budget, actual degree/cursor width/full weight/id/seams/partial batches/cancellation, samples and full public/untrained; no generation/oracle/training repeated. Every current395 main replay is fresh.','valid':list(rows.values()),'errors':list(errors.values()),'folders':folders};dump(w/'proof-bank.json',bank)
model=(r/'.build/round334/joined_cursor_model.cpp').read_text();old_model_sha=sha(r/'.build/round334/joined_cursor_model.cpp')
model=model.replace('#include "source/track-d/load_cursors.hpp"','#include "source/track-d/load_cursors.hpp"\n#include "source/track-d/edge_store.hpp"')
a='''                uint32_t slot=force_wide?cursor.take<true>(node):cursor.take(node);''';b='''                cursor.prefetch<true,true>(node);
                if(!cursor.wide_blocks)cursor.prefetch<false,true>(node);
                uint32_t slot=force_wide?cursor.take<true>(node):cursor.take(node);''';assert model.count(a)==1;model=model.replace(a,b)
pos=model.index('int main(')
extra='''template<bool Compact> static void edge_hints(){
    for(size_t count:{size_t(0),size_t(1),size_t(15),size_t(16),size_t(17),size_t(257)}){
        EdgeStore edges(count,Compact?100U:(1U<<21)+1);
        for(uint32_t i=0;i<count;++i){
            edges.prefetch<Compact,true>(i);
            edges.set<Compact>(i,i*7,Compact?i%2048:i%65536);
        }
        for(uint32_t i=0;i<count;++i){
            edges.prefetch<Compact,false>(i);
            auto value=edges.get<Compact>(i);
            require(value.first==i*7&&value.second==(Compact?i%2048:i%65536));
        }
    }
}
'''
model=model[:pos]+extra+model[pos:];a=model.index('{',model.index('int main('))+1;model=model[:a]+'\n    edge_hints<true>();edge_hints<false>();\n'+model[a:];(w/'loader_hints_model.cpp').write_text(model)
plan={'created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_manifest_sha256':sha(w/'frozen.json'),'candidate_Makefile_sha256':sha(s/'Makefile'),'proof_bank_sha256':sha(w/'proof-bank.json'),'valid_cases':len(rows),'normal_error_cases':len(errors),'model_sha256':sha(w/'loader_hints_model.cpp'),'model_base_sha256':old_model_sha,'model_changes':'Fresh actual395 headers. Existing joined-cursor independent complete-prefix/unique atomic slot coverage/post-unmap narrow/wide/uint32 extremes and1..12 owners now invoke BOTH changed write-prefetch template paths before claims. Added actual compact/wide EdgeStore write/read hint/set/get roundtrips for empty/single/batch-boundary/partial counts. Original algorithm maps/heaps/allocator bodies exact, no new protocol theorem or unexecuted primitive pass invented.','source_inverse_substitutions_verified':True,'scope':'Only existing loader hint operands changed; exact inverse substitutions recover original three files. Whole current main freshly strict/race/GNU/image tested using independently expected saved fixtures, not old source proof. GNU native build and allowedPGO unchanged, true entrypoint defaults required. Native gains remain hypotheses pending one real all-track trial.'};dump(w/'proof-plan.json',plan);shutil.copy2(Path(__file__),w/'prepare_proof.py');print('PREPARED395 fresh proof bank',len(rows),'valid',len(errors),'normalerrors; exact inverse source verified',flush=True)
