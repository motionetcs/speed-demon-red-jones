#ifndef RECORD_SCAN_HEADER
#error "Supply the exact candidate header path"
#endif
#include RECORD_SCAN_HEADER
#include <cassert>
#include <iostream>
#include <random>
#include <string>
#include <sys/mman.h>
#include <unistd.h>
#include <vector>
struct Expected {std::array<std::string,5> fields;bool terminated;};
std::string encode(const std::string& value,bool quoted){
    if(!quoted)return value;
    std::string result="\"";
    for(char ch:value){result+=ch;if(ch=='"')result+=ch;}
    result+='"';return result;
}
uint64_t prefix_reference(uint64_t value){
    bool on=false;uint64_t result=0;
    for(unsigned i=0;i<64;++i){on^=((value>>i)&1)!=0;if(on)result|=uint64_t(1)<<i;}
    return result;
}
int main(){
    std::mt19937_64 random(0x121c5a1);
    for(uint64_t mask=0;mask<65536;++mask)assert(RecordScanner::prefix_xor(mask)==prefix_reference(mask));
    for(unsigned i=0;i<100000;++i){auto mask=random();assert(RecordScanner::prefix_xor(mask)==prefix_reference(mask));}
    size_t page=size_t(sysconf(_SC_PAGESIZE)),capacity=4*1024*1024;
    char* memory=static_cast<char*>(mmap(nullptr,capacity+2*page,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANON,-1,0));
    assert(memory!=MAP_FAILED);assert(mprotect(memory,page,PROT_NONE)==0);assert(mprotect(memory+page+capacity,page,PROT_NONE)==0);
    char* end=memory+page+capacity;
    auto check=[&](const std::string& input,const std::vector<Expected>& expected){
        assert(input.size()<=capacity);char* first=end-input.size();if(!input.empty())std::memcpy(first,input.data(),input.size());
        RecordScanner scanner(first,end);std::array<RawCsvField,5> fields;
        for(const auto& row:expected){
            assert(scanner.record(fields));assert(scanner.terminated==row.terminated);
            for(unsigned f=0;f<5;++f){
                assert(fields[f].first>=first&&fields[f].last<=end&&fields[f].first<=fields[f].last);
                assert(std::string_view(fields[f].first,size_t(fields[f].last-fields[f].first))==row.fields[f]);
                assert(fields[f].quotes==size_t(std::count(row.fields[f].begin(),row.fields[f].end(),'"')));
            }
        }
        assert(!scanner.record(fields));
    };
    auto one=[&](std::string name,std::string note,bool quoted_name,bool quoted_note,int term,unsigned padding){
        Expected row{{std::string(padding,'9'),encode(name,quoted_name),encode(note,quoted_note),"17","-0.05"},term!=0};
        std::string input=row.fields[0]+","+row.fields[1]+","+row.fields[2]+","+row.fields[3]+","+row.fields[4];
        if(term==2){input+='\r';row.fields[4]+='\r';}if(term)input+='\n';check(input,{row});
    };
    check("",{});
    for(unsigned offset=1;offset<=70;++offset)for(unsigned byte=0;byte<256;++byte){
        std::string text(73,'x');text[byte%text.size()]=char(byte);
        one(text,"a\"\",\r\nb",true,true,byte%3,offset);
    }
    for(unsigned length=0;length<=256;++length){
        one(std::string(length,'"'),std::string(256-length,'"'),true,true,length%3,1+length%64);
        one(std::string(length,'x'),"",false,length%2,length%3,1+length%64);
    }
    for(unsigned trial=0;trial<50000;++trial){
        std::string input;std::vector<Expected> expected;unsigned rows=1+random()%8;
        for(unsigned j=0;j<rows;++j){
            std::string name,note;unsigned nn=random()%80,nt=random()%100;
            for(unsigned k=0;k<nn;++k)name+=char(random()%256);
            for(unsigned k=0;k<nt;++k)note+=char(random()%256);
            int term=j+1<rows?1+random()%2:random()%3;
            Expected row{{std::to_string(random()%10000000),encode(name,true),encode(note,true),std::to_string(random()%1000000),"1234.56"},term!=0};
            for(unsigned f=0;f<5;++f){if(f)input+=',';input+=row.fields[f];}
            if(term==2){input+='\r';row.fields[4]+='\r';}if(term)input+='\n';expected.push_back(std::move(row));
        }
        check(input,expected);
    }
    std::string long_text(1024*1024,'x');for(size_t i=0;i<long_text.size();i+=113)long_text[i]='"';one(long_text,"",true,false,0,1);
    for(std::string bad:{"1,\"a\"b\"c\",n,1,0.00\n","1,a\"b\",n,1,0.00\n","1,\"a\n","1,a,n,1,0.00,2\n","1,a\n","1,a,n,1"}){
        bool threw=false;
        try{RecordScanner scanner(bad.data(),bad.data()+bad.size());std::array<RawCsvField,5> fields;while(scanner.record(fields)){};}catch(const std::runtime_error&){threw=true;}
        assert(threw);
    }
    assert(munmap(memory,capacity+2*page)==0);
    std::cout<<"PASS independent encoded field spans/counts, all bytes/offsets, quote runs,50000 random record sets,1MiB fields, protected tails and malformed quote/field counts; ";
#if defined(RECORD_SCAN_SCALAR)
    std::cout<<"forced scalar";
#elif defined(__AVX2__) && defined(__PCLMUL__)
    std::cout<<"AVX2+PCLMUL executed";
#elif defined(__SSE2__)
    std::cout<<"SSE2 executed";
#elif defined(__ARM_NEON)
    std::cout<<"NEON executed";
#endif
    std::cout<<"\n";
}
