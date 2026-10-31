#ifndef ENDPOINTS_HEADER
#define ENDPOINTS_HEADER "../track-a/endpoint_table.hpp"
#endif
#include ENDPOINTS_HEADER
#include <cassert>
#include <iostream>
#include <random>
#include <sys/mman.h>
#include <unistd.h>
#include <vector>

template<class Table> constexpr bool has_endpoint_hash=requires(std::string_view key){Table::hash_key(key);};
template<class Table> uint64_t subject(std::string_view key){if constexpr(has_endpoint_hash<Table>)return Table::hash_key(key);else return std::hash<std::string_view>{}(key);}
uint32_t crc_byte(uint32_t crc,unsigned char byte){crc^=byte;for(unsigned i=0;i<8;++i)crc=(crc>>1)^(0x82f63b78U&uint32_t(-int32_t(crc&1)));return crc;}
uint64_t portable_crc(std::string_view key){
    uint32_t crc=static_cast<uint32_t>(key.size());
    for(unsigned char byte:key)crc=crc_byte(crc,byte);
    if(key.size()%8)for(size_t i=key.size()%8;i<8;++i)crc=crc_byte(crc,0);
    return uint64_t(crc)*0x9e3779b97f4a7c15ULL;
}
void check(std::string_view key){
    uint64_t expected=std::hash<std::string_view>{}(key);
#if defined(__SSE4_2__)
    if constexpr(has_endpoint_hash<Endpoints>)expected=portable_crc(key);
#endif
    assert(subject<Endpoints>(key)==expected);
}
int main(){
#ifdef REQUIRE_ENDPOINT_CRC
#ifndef __SSE4_2__
#error CRC instruction path must be enabled.
#endif
    static_assert(has_endpoint_hash<Endpoints>);
#endif
    for(unsigned byte=0;byte<256;++byte)for(unsigned length=0;length<34;++length)check(std::string(length,char(byte)));
    std::mt19937_64 random(0x69acfe21);
    for(unsigned i=0;i<10000;++i){std::string key(random()%257,' ');for(char& byte:key)byte=char(random());check(key);}
    size_t page=size_t(sysconf(_SC_PAGESIZE));char* memory=static_cast<char*>(mmap(nullptr,page*2,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANON,-1,0));assert(memory!=MAP_FAILED&&mprotect(memory+page,page,PROT_NONE)==0);
    for(size_t length=0;length<=512;++length)for(size_t offset=0;offset<8;++offset){char* start=memory+page-offset-length;for(size_t i=0;i<length;++i)start[i]=char(random());check({start,length});}
    munmap(memory,page*2);
    std::vector<std::string> keys;keys.reserve(4096);for(unsigned i=0;i<4096;++i)keys.push_back("/full-name/"+std::to_string(i));Endpoints table;
    for(unsigned i=0;i<4096;++i)assert(table.intern(keys[i],subject<Endpoints>(keys[i]))==i);
    for(unsigned i=4096;i>0;--i)assert(table.intern(keys[i-1],subject<Endpoints>(keys[i-1]))==i-1);
    assert(table.used.load()==4096);
#ifdef REQUIRE_ENDPOINT_CRC
    std::cout<<"PASS active SSE4.2 endpoint CRC versus independent polynomial reference, all bytes/lengths/random/guard pages and4096 exact IDs\n";
#else
    std::cout<<"PASS endpoint hash reference, all bytes/lengths/random/guard pages and4096 exact IDs\n";
#endif
}
