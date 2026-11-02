from pathlib import Path
import datetime,difflib,hashlib,json,shutil,subprocess
r=Path('/Volumes/Vault/Documents/codex/rough/speed-demon-fresh');w=r/'.build/round370';assert not w.exists();w.mkdir();s=w/'source';s.mkdir()
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();proof=json.loads((r/'docs/round363-final-source-match.json').read_text());bindings={x['path']:x['sha256']for x in proof['inputs']};bindings['Makefile']=proof['Makefile_sha256'];assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=r,text=True).strip()==proof['source_commit']
for p,h in bindings.items():assert sha(r/p)==h,p
shutil.copytree(r/'track-c',s/'track-c');(w/'original-retained').mkdir();shutil.copytree(r/'track-c',w/'original-retained/track-c');p=s/'track-c/main.cpp';old=p.read_text();start=old.index('struct Field {');end=old.index('    void comma()')
replacement='''struct Field { std::string_view value; size_t bytes; };
struct Csv {
    const char* p;
    const char* end;
    void bom() {
        if (end - p >= 3 && std::memcmp(p, "\\xef\\xbb\\xbf", 3) == 0) p += 3;
    }
    Field field() {
        const char* start = p;
        if (p == end || *p != '"') {
            while (p < end && *p != ',' && *p != '\\r' && *p != '\\n') ++p;
            return {{start, static_cast<size_t>(p - start)}, static_cast<size_t>(p - start)};
        }
        const char* segment = ++p;
        start = segment;
        size_t bytes = 0;
        while (p < end) {
            const char* quote = find_quote(p, end);
            if (!quote) throw std::runtime_error("unterminated quoted field");
            bytes += static_cast<size_t>(quote - segment);
            if (quote + 1 < end && quote[1] == '"') {
                ++bytes;
                segment = p = quote + 2;
            } else {
                p = quote + 1;
                return {{start, static_cast<size_t>(quote - start)}, bytes};
            }
        }
        throw std::runtime_error("unterminated quoted field");
    }
'''
new=old[:start]+replacement+old[end:]
for a,b in [('Csv tail{quote+2,end};std::string unused;','Csv tail{quote+2,end};'),('tail.field(unused,false)','tail.field()'),('        std::string scratch;\n',''),('region_csv.field(scratch, false)','region_csv.field()'),('header.field(scratch, true)','header.field()'),('};std::string name_scratch,unused;','};'),('csv.field(name_scratch,false)','csv.field()'),('csv.field(unused,false)','csv.field()'),('if(finished[reader])continue;auto& queue=queues[size_t(reader)*owners+owner];','if(finished[reader])continue;\n                                auto& queue=queues[size_t(reader)*owners+owner];'),('if(!queue.ready.load(std::memory_order_acquire))continue;progress=true;','if(!queue.ready.load(std::memory_order_acquire))continue;\n                                progress=true;')]:
 assert a in new,a;new=new.replace(a,b)
assert 'scratch'not in new and 'bool escaped'not in new and 'bool decode'not in new;p.write_text(new);(w/'main.cpp.patch').write_text(''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),fromfile='a/track-c/main.cpp',tofile='b/track-c/main.cpp')))
p=s/'track-c/README.md';old_readme=p.read_text();p.write_text(old_readme+'\n\nThe field lexer returns the exact raw canonical interior and unescaped byte count. Every expected header label has no literal quote, so comparing its canonical interior to that label also accepts the same quoted headers without needing a decoded scratch string. Record grammar, byte equality, lengths and all worker/owner protocols are preserved.\n');(w/'README.md.patch').write_text(''.join(difflib.unified_diff(old_readme.splitlines(True),p.read_text().splitlines(True),fromfile='a/track-c/README.md',tofile='b/track-c/README.md')))
pre={'created_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'source_parent':proof['source_commit'],'official_score':False,'selected_in_root':False,'scope':'C370 rawcanonical+decodedcount-only field API: removeunusedField.escaped and scratch/decode machinery; allproductioncallers field(). Record/boundary/regionheader callers alreadydecode=false. Recordsheader wasonlydecode=true but everyexpectedlabel hasno literalquote: canonical raw==expected iffdecoded==expected, including quotedheaderextensions, so no literalheader narrowing. CSVsegmentedquoted/doubledquote/UTF8/BOM/CRLF/LF/EOF/bytecount/invaliddelimiter logic remainsoriginalrawpath. Numeric/comma/newline/BOM, Names/fullkeys/countrywidths/queues/readers8owners4/512/default12/PGO/flags unchanged. Twooldqueue statementlinebreaks forstrictGCC included beforefirstcompile. Simpler source and24BField vs32B mayhelp totalK; originaldefaultnarrowfieldalreadyinlined (308/349), so no hiddenABI/hotdecode-saving assumption. Need semanticheader-equivalence/rawcount/allbytes/long/guard/independent/adversarial/untrained/strict/race/GNU/image/default/Make/sourceproof before any integration/privatepush/realtrial. No artificialminification, exemptions, seed/catalogue/answers/harness/host/worker/counter/default/ISA changes. A178/D334 untouched.','source_sha256':{str(p.relative_to(s)):sha(p)for p in(s/'track-c').iterdir()if p.is_file()},'root_selected_bindings':bindings,'control_binary':str(r/'.build/round263/final-make/track-c'),'control_binary_sha256':sha(r/'.build/round263/final-make/track-c'),'unchanged_C_headers_sha256':{str(p.relative_to(s)):sha(p)for p in(s/'track-c').glob('*.hpp')},'duplicate_check':'237/241 compile-time note specialization retained genericdecoder,300 payload rawalgebra retainedheader/genericparser,349 stringview/optionalcount ABI retainedgenericdecode andnot source removal.370 removesgloballyunneededdecoder/escapedresult andproves observableheadercompare equivalence; rawsegmentedalgorithm unchanged, not300rawlength-minuspair state. No oldstrictproof relabeled.','frozen_spec':{'path':'tools/official/specs/c-join.md','sha256':sha(r/'tools/official/specs/c-join.md'),'scope':'2.1 headerlabels/CSVbytegrammar and2.2generatorconstraints read; no generatedheader-onlyshortcutused. Quotedheaderextensionpreserved bycanonical comparison.'}}
(w/'preflight.json').write_text(json.dumps(pre,indent=2)+'\n');shutil.copyfile(Path(__file__),w/'prepare.py');screen=(r/'.build/round357/screen.py').read_text().replace('357','370').replace('direct-word owner epochs screen','rawcanonical/count-only field API screen');compile(screen,'screen370.py','exec');(w/'screen.py').write_text(screen);print('PREPARED370 isolated rawfield/header-equivalence refactor; rootunchanged',flush=True)
