#include "csv_model.hpp"
#include <array>
#include <cassert>
#include <iostream>
#include <random>
#include <string>
#include <sys/mman.h>
#include <unistd.h>

uint64_t checks=0;
std::string interior(std::string_view value){
    std::string result;
    for(char byte:value){result.push_back(byte);if(byte=='"')result.push_back(byte);}
    return result;
}
void verify_at(const char* memory,std::string_view value,bool quoted,std::string_view tail){
    std::string raw=quoted?interior(value):std::string(value);
    size_t consumed=raw.size()+(quoted?2:0);
    Csv csv{memory,memory+consumed+tail.size()};auto field=csv.field();
    assert(field.value==raw&&field.bytes==value.size()&&csv.p==memory+consumed);
    if(tail==",")csv.comma();else csv.newline();
    assert(csv.p==csv.end);++checks;
}
void verify(std::string_view value,bool quoted,std::string_view tail){
    std::string raw=quoted?interior(value):std::string(value);
    std::string input=(quoted?"\""+raw+"\"":raw)+std::string(tail);
    verify_at(input.data(),value,quoted,tail);
}
int main(){
    static_assert(sizeof(Field)==sizeof(std::string_view)+sizeof(size_t));
    for(unsigned byte=0;byte<256;++byte)for(size_t n=0;n<=256;++n){
        std::string value(n,char(byte));
        for(std::string_view tail:{std::string_view(),std::string_view(","),std::string_view("\n"),std::string_view("\r\n")}){
            verify(value,true,tail);
            if(byte!='"'&&byte!=','&&byte!='\r'&&byte!='\n')verify(value,false,tail);
        }
    }
    std::mt19937_64 random(0x370f13ULL);
    for(unsigned trial=0;trial<20000;++trial){
        std::string value(size_t(random()%384),' ');
        for(char& byte:value)byte=char(random()%256);
        verify(value,true,trial%2?"\r\n":",");
    }
    for(std::string_view label:{"id","name","note","region_id","amount","country"}){
        for(bool quoted:{false,true}){
            std::string input=(quoted?"\""+interior(label)+"\"":std::string(label))+",";
            Csv csv{input.data(),input.data()+input.size()};assert(csv.field().value==label);csv.comma();assert(csv.p==csv.end);++checks;
        }
        for(size_t at=0;at<=label.size();++at)for(unsigned byte=0;byte<256;++byte){
            std::string decoded(label);decoded.insert(at,1,char(byte));
            std::string input="\""+interior(decoded)+"\",";Csv csv{input.data(),input.data()+input.size()};
            // The expected decoded bytes are known before encoding; no parsing oracle is copied.
            assert((csv.field().value==label)==(decoded==label));csv.comma();assert(csv.p==csv.end);++checks;
        }
    }
    for(std::string_view value:{std::string_view("\xef\xbb\xbf"),std::string_view("a\xef\xbb\xbf\n\"z "),std::string_view("\""),std::string_view("\"\"\""),std::string_view(" ")})verify(value,true,"\r\n");
    for(char byte:{'x','"','\n'})verify(std::string(1048576,byte),true,",");
    size_t page=size_t(sysconf(_SC_PAGESIZE));
    char* pages=static_cast<char*>(mmap(nullptr,page*3,PROT_NONE,MAP_PRIVATE|MAP_ANON,-1,0));
    assert(pages!=MAP_FAILED&&mprotect(pages+page,page,PROT_READ|PROT_WRITE)==0);
    for(size_t n=0;n<=512;++n)for(bool quoted:{false,true}){
        std::string value(n,quoted?'"':'a');std::string raw=quoted?interior(value):value;std::string input=quoted?"\""+raw+"\"":raw;
        for(bool right:{false,true}){
            char* start=right?pages+2*page-input.size():pages+page;
            if(!input.empty())std::memcpy(start,input.data(),input.size());
            verify_at(start,value,quoted,{});
        }
        if(quoted){
            input.pop_back();char* start=pages+2*page-input.size();std::memcpy(start,input.data(),input.size());
            Csv csv{start,start+input.size()};bool threw=false;try{csv.field();}catch(const std::runtime_error&){threw=true;}
            assert(threw);++checks;
            start=pages+page;std::memcpy(start,input.data(),input.size());start[input.size()]='"';
            csv={start,start+input.size()};threw=false;try{csv.field();}catch(const std::runtime_error&){threw=true;}
            assert(threw);++checks;
        }
    }
    assert(munmap(pages,page*3)==0);
    std::cout<<"PASS370 constructed rawcanonical/decodedcount/quote-free-header-equivalence/all-byte/UTF8/BOM/1MiB/logical-and-protected-tail models "<<checks<<" checks\n";
}
