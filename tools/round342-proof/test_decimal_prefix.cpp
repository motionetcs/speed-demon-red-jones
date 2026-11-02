#include DECIMAL_HEADER
#include <cassert>
#include <charconv>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <random>
#include <string>
#include <sys/mman.h>
#include <unistd.h>

static void check(const char* start,const char* end){
    const char* scalar=start;uint64_t expected=0;
    while(scalar<end&&*scalar>='0'&&*scalar<='9')expected=expected*10+*scalar++-'0';
    const char* actual=start;assert(decimal_digits(actual,end)==expected&&actual==scalar);
}
int main(){
    std::mt19937_64 rng(0x61d5c03b9);
    for(unsigned n=0;n<100000;++n){std::string s=std::to_string(rng());uint64_t v=0;auto ref=std::from_chars(s.data(),s.data()+s.size(),v);const char* p=s.data();assert(decimal_digits(p,s.data()+s.size())==v&&p==ref.ptr);s+='\n';s+=std::to_string(rng());check(s.data(),s.data()+s.size());}
    for(unsigned length=0;length<=24;++length)for(unsigned position=0;position<=length;++position)for(unsigned byte=0;byte<256;++byte){
        std::string s(length,'9');if(position<length)s[position]=char(byte);check(s.data(),s.data()+s.size());
    }
    // Every first invalid byte amid digit prefixes and arbitrary-byte suffixes.
    for(unsigned prefix=0;prefix<8;++prefix)for(unsigned first=0;first<256;++first)for(unsigned tail=0;tail<256;++tail){std::string s(16,char(tail));for(unsigned i=0;i<prefix;++i)s[i]=char('0'+rng()%10);s[prefix]=char(first);check(s.data(),s.data()+s.size());}
    for(unsigned trial=0;trial<200000;++trial){std::string s(rng()%65,'\0');for(char& c:s)c=char(rng());check(s.data(),s.data()+s.size());}
    size_t page=size_t(sysconf(_SC_PAGESIZE));char* mem=static_cast<char*>(mmap(nullptr,3*page,PROT_NONE,MAP_PRIVATE|MAP_ANON,-1,0));assert(mem!=MAP_FAILED&&mprotect(mem+page,page,PROT_READ|PROT_WRITE)==0);
    for(unsigned length=0;length<=64;++length)for(unsigned trial=0;trial<256;++trial){std::string s(length,'9');for(char& c:s)if(rng()%3)c=char(rng());for(char* dst:{mem+page,mem+2*page-length}){std::memcpy(dst,s.data(),length);check(dst,dst+length);}}
    assert(munmap(mem,3*page)==0);std::cout<<"PASS leading decimal byte/reference/guard-page model\n";
}
