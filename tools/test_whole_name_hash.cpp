#ifndef NAME_HASH_HEADER
#error Explicit candidate NAME_HASH_HEADER required
#endif
#include NAME_HASH_HEADER
#include <algorithm>
#include <cassert>
#include <iostream>
#include <random>
#include <string>
#include <vector>
#include <sys/mman.h>
#include <unistd.h>

#ifndef EXPECT_NAME_CRC
#error Explicit hardware/fallback expectation required
#endif
static_assert(NAME_HASH_CRC==EXPECT_NAME_CRC);
uint64_t reference(std::string_view key){
#if EXPECT_NAME_CRC
    uint32_t state=static_cast<uint32_t>(key.size())^0x9e3779b9U;
    auto byte=[&](unsigned char b){state^=b;for(unsigned k=0;k<8;++k)state=(state>>1)^(0x82f63b78U&(0U-(state&1)));};
    for(unsigned char b:key)byte(b);
#if PADDED_NAME_REFERENCE
    if(key.size()%8)for(size_t k=key.size()%8;k<8;++k)byte(0);
#endif
    uint64_t hash=uint64_t(state)*0x9e3779b97f4a7c15ULL;
#else
    uint64_t hash=std::hash<std::string_view>{}(key);
#endif
    return hash<2?hash+2:hash;
}
void check(std::string_view key){assert(whole_name_hash(key)==reference(key));}
int main(){
    std::mt19937_64 random(0xc1480001);
    for(size_t n=0;n<=257;++n)for(unsigned b=0;b<256;++b)check(std::string(n,char(b)));
    for(unsigned i=0;i<20000;++i){std::string s(random()%513,'\0');for(char& b:s)b=char(random());check(s);}
    for(size_t n:{1023U,1024U,1025U,65535U,65536U,65537U,1048576U}){std::string s(n,'\0');for(char& b:s)b=char(random());check(s);}
    size_t page=static_cast<size_t>(sysconf(_SC_PAGESIZE));
    void* memory=mmap(nullptr,page*3,PROT_NONE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);assert(memory!=MAP_FAILED);
    char* begin=static_cast<char*>(memory)+page;assert(mprotect(begin,page,PROT_READ|PROT_WRITE)==0);
    std::vector<size_t> lengths;for(size_t n=0;n<=257;++n)lengths.push_back(n);
    for(size_t n=page-16;n<=page;++n)lengths.push_back(n);
    for(unsigned i=0;i<32;++i)lengths.push_back(random()%(page+1));
    for(size_t n:lengths){char* p=begin+page-n;for(size_t i=0;i<n;++i)p[i]=char((i*47+n)%256);check({p,n});}
    for(size_t n:lengths)check({begin,n});
    assert(munmap(memory,page*3)==0);
    std::cout<<"PASS whole-key hash scalar bit-polynomial/fallback oracle; all bytes, tails, random/1MiB and both protected-page boundaries; hardware="<<NAME_HASH_CRC<<" padded="<<PADDED_NAME_REFERENCE<<'\n';
}
