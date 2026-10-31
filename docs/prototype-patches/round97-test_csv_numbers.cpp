#ifndef CSV_NUMBERS_HEADER
#define CSV_NUMBERS_HEADER "csv_numbers.hpp"
#endif
#include CSV_NUMBERS_HEADER
#include <algorithm>
#include <cassert>
#include <iostream>
#include <random>
#include <string>
#include <sys/mman.h>
#include <unistd.h>
int main(){
    size_t page=static_cast<size_t>(sysconf(_SC_PAGESIZE));
    char* region=static_cast<char*>(mmap(nullptr,page*2,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANON,-1,0));
    assert(region!=MAP_FAILED&&mprotect(region+page,page,PROT_NONE)==0);
    auto integer=[&](const std::string& text){
        assert(text.size()<=page);char* start=region+page-text.size();if(!text.empty())std::memcpy(start,text.data(),text.size());
        size_t comma=text.find(',');bool eligible=text.size()>=8&&comma>=1&&comma<=7;uint64_t expected=0;
        if(eligible)for(size_t i=0;i<comma;++i){eligible&=text[i]>='0'&&text[i]<='9';expected=expected*10+static_cast<unsigned char>(text[i])-'0';}
        if constexpr(std::endian::native!=std::endian::little)eligible=false;
        const char* p=start;uint64_t value=0xabcdef1234ULL;bool ok=csv_short_integer(p,region+page,value);assert(ok==eligible);
        if(ok)assert(value==expected&&p==start+comma+1);else assert(p==start&&value==0xabcdef1234ULL);
    };
    auto money=[&](const std::string& text){
        assert(text.size()<=page);char* start=region+page-text.size();if(!text.empty())std::memcpy(start,text.data(),text.size());
        bool eligible=text.size()>=8&&text[5]=='.';uint64_t expected=0;
        if(eligible)for(unsigned i=0;i<8;++i)if(i!=5){eligible&=text[i]>='0'&&text[i]<='9';expected=expected*10+static_cast<unsigned char>(text[i])-'0';}
        if constexpr(std::endian::native!=std::endian::little)eligible=false;
        const char* p=start;uint64_t value=0xabcdef1234ULL;bool ok=csv_common_cents(p,region+page,value);assert(ok==eligible);
        if(ok)assert(value==expected&&p==start+8);else assert(p==start&&value==0xabcdef1234ULL);
    };
    for(size_t length=0;length<40;++length){std::string text(length,'7');integer(text);money(text);for(size_t i=0;i<length;++i){text[i]=',';integer(text);text[i]='7';}}
    for(size_t at=0;at<12;++at)for(unsigned c=0;c<256;++c){std::string text="12345,6789xx";text[at]=char(c);integer(text);text="12345.67xxxx";text[at]=char(c);money(text);}
    std::mt19937_64 random(0x97bca124);
    for(unsigned i=0;i<100000;++i){
        size_t n=random()%25;std::string text;for(size_t j=0;j<n;++j)text.push_back(char('0'+random()%10));text+=',';text.append(random()%15,'x');integer(text);
        uint64_t whole=random()%100000,frac=random()%100;std::string decimal=std::to_string(whole);decimal.insert(decimal.begin(),5-decimal.size(),'0');decimal+='.';decimal+=char('0'+frac/10);decimal+=char('0'+frac%10);decimal.append(random()%8,'x');money(decimal);
        std::string arbitrary(random()%40,'x');for(char& b:arbitrary)b=char(random()%256);integer(arbitrary);money(arbitrary);
    }
    for(const char* text:{"0,xxxxxxxx","9999999,tail","10000000,tail","18446744073709551615,tail","12345.67","00000.00","99999.99","0.00","-0.01","12345.6","12345.678"}){integer(text);money(text);}
    munmap(region,page*2);std::cout<<"PASS scalar numeric references, every byte/offset,100000 randomized integer/money/binary buffers and protected-page tails; false paths preserve cursor/value\n";
}
