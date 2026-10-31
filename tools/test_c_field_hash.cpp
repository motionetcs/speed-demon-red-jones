// Include the exact program parser; the renamed entry function is never called.
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wreturn-type"
#define main unused_program_entry_for_parser_model
#include CSV_SOURCE
#undef main
#pragma GCC diagnostic pop
#include <cassert>
#include <iostream>
#include <random>
#include <unistd.h>

#if defined(REQUIRE_SSE42) && !defined(__SSE4_2__)
#error The target-specific hash path must be enabled in this model.
#endif

void check_value(const std::string& value) {
    bool quoted=value.find_first_of(",\r\n\"")!=std::string::npos;
    std::string raw;
    if(quoted)raw.push_back('"');
    for(char c:value){raw.push_back(c);if(quoted&&c=='"')raw.push_back(c);}
    if(quoted)raw.push_back('"');
    raw.push_back(',');
    for(bool decode:{false,true}){
        Csv fast{raw.data(),raw.data()+raw.size()}, scalar=fast;
        std::string a,b;
        Field actual=fast.data_field(a,decode), reference=scalar.field(b,decode);
        assert(actual.bytes==value.size()&&actual.bytes==reference.bytes);
        assert(actual.value==reference.value&&actual.escaped==reference.escaped);
        if(decode)assert(actual.value==value);
        assert(fast.p==scalar.p&&fast.p==raw.data()+raw.size()-1);
    }
}

int main(){
    std::mt19937_64 random(0x60c25e);
    for(unsigned byte=0;byte<256;++byte)for(unsigned length=0;length<33;++length)
        check_value(std::string(length,char(byte)));
    for(unsigned i=0;i<20000;++i){
        std::string value(random()%513,' ');
        for(char& c:value)c=char(random());
        check_value(value);
    }
    size_t page=size_t(sysconf(_SC_PAGESIZE));
    char* memory=static_cast<char*>(mmap(nullptr,page*2,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANON,-1,0));
    assert(memory!=MAP_FAILED&&mprotect(memory+page,page,PROT_NONE)==0);
    char* end=memory+page;
    for(size_t length=0;length<=512;++length){
        char* start=end-length-1;
        for(size_t i=0;i<length;++i){
            unsigned char c=static_cast<unsigned char>(random());
            if(c==','||c=='"'||c=='\r'||c=='\n')c='-';
            start[i]=char(c);
        }
        end[-1]=',';
        Csv csv{start,end};std::string scratch;
        Field result=csv.data_field(scratch,true);
        assert(result.bytes==length&&result.value==std::string_view(start,length)&&csv.p==end-1);
        start=end-length;
        for(size_t i=0;i<length;++i)start[i]=char(random());
        std::string_view key(start,length);std::string copied(key);
        assert(Names::hash_key(key)==Names::hash_key(copied)&&Names::hash_key(key)>=2);
    }
    munmap(memory,page*2);
    std::string large(1<<20,'x');
    for(char& c:large)c=char(random());
    assert(Names::hash_key(large)==Names::hash_key(std::string(large)));
#ifdef __SSE4_2__
    std::cout<<"PASS exact CSV field/byte/quote/guard-page and active SSE4.2 hash span models\n";
#else
    std::cout<<"PASS exact CSV field/byte/quote/guard-page and portable hash span models\n";
#endif
}
