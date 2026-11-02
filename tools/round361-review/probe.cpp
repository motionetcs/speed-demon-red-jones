#include <cstring>
extern "C" __attribute__((noinline)) bool same(const char* a,const char* b,unsigned long size){return std::memcmp(a,b,size)==0;}
int main(int argc,char** argv){return same(argv[0],argv[argc-1],1)?0:1;}
