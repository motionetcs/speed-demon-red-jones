// The exact program parser is included; its renamed entry function is not called.
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wreturn-type"
#define main unused_program_entry_for_split_model
#include CSV_SOURCE
#undef main
#pragma GCC diagnostic pop
#include <cassert>
#include <iostream>
#include <random>
#include <set>
#include <unistd.h>

std::string encoded(const std::string& value,bool force){
    bool quote=force||value.find_first_of(",\r\n\"")!=std::string::npos;
    if(!quote)return value;
    std::string out="\"";
    for(char c:value){out.push_back(c);if(c=='"')out.push_back('"');}
    out.push_back('"');return out;
}
void check_span(const char* begin,size_t bytes,const std::vector<size_t>& ends){
    const char* end=begin+bytes;
    for(unsigned threads=1;threads<=12;++threads){
        auto split=record_boundaries(begin,end,threads);
        assert(split.size()==threads+1&&split.front()==begin&&split.back()==end);
        for(size_t i=0;i<split.size();++i){
            assert(split[i]>=begin&&split[i]<=end);
            assert(std::binary_search(ends.begin(),ends.end(),size_t(split[i]-begin)));
            if(i)assert(split[i]>=split[i-1]);
        }
    }
}
void check(const std::string& body,const std::vector<size_t>& ends){
    check_span(body.data(),body.size(),ends);
    size_t page=size_t(sysconf(_SC_PAGESIZE));
    if(body.size()>page)return;
    char* guard=static_cast<char*>(mmap(nullptr,page*2,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANON,-1,0));
    assert(guard!=MAP_FAILED&&mprotect(guard+page,page,PROT_NONE)==0);
    char* begin=guard+page-body.size();if(!body.empty())std::memcpy(begin,body.data(),body.size());
    check_span(begin,body.size(),ends);munmap(guard,page*2);
}
int main(){
    const std::string bom="\xef\xbb\xbf";
    std::vector<std::string> values={"","a","a ","a,b","\"","\"\"","a\"b","\",1,0.00\n9999,\"x","line\nnext","line\r\nnext",bom+"x","x"+bom,"\xc3\xa9"};
    for(unsigned n=1;n<=8;++n)values.emplace_back(n,'"');
    check("",{0});
    for(unsigned padding=0;padding<65;++padding)for(unsigned mode=0;mode<4;++mode){
        std::string body;std::vector<size_t> ends{0};
        for(size_t i=0;i<values.size();++i){
            if(i%3==0)body+=bom;
            body+=std::to_string(i+1)+","+encoded(i?values[i]:std::string(padding,'p'),mode&1)+","+encoded(values[values.size()-i-1],mode&2)+",1,-0.05";
            if(i+1<values.size()||padding%2)body+=i%2?"\n":"\r\n";
            ends.push_back(body.size());
        }
        check(body,ends);
    }
    std::mt19937 random(0xc62b0a);
    for(unsigned trial=0;trial<400;++trial){
        std::string body;std::vector<size_t> ends{0};
        for(unsigned i=0;i<1+random()%80;++i){
            if(i%7==0)body+=bom;
            body+=std::to_string(i+1)+","+encoded(values[random()%values.size()],random()%2)+","+encoded(values[random()%values.size()],random()%2)+",1,0.00\n";
            ends.push_back(body.size());
        }
        check(body,ends);
    }
    std::cout<<"PASS CSV split monotonicity, true-boundary membership and complete record coverage; all offsets/quote runs/BOM/EOF/guard pages at1..12 workers\n";
}
