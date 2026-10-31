#include NAMES_HEADER
#include <cstdio>
int main(){
 for(unsigned i=0;i<4;++i){
  std::vector<uint16_t> lookup(1000000,UINT16_MAX);std::vector<uint8_t> narrow(1000000,255);std::vector<uint16_t>().swap(lookup);
  Names names(131072,241);
#ifdef ALIGNED_GROUP
  auto address=reinterpret_cast<uintptr_t>(names.groups.get());
#else
  auto address=reinterpret_cast<uintptr_t>(names.entries.get());
#endif
  std::printf("pointer_array_mod64=%llu\n",static_cast<unsigned long long>(address%64));
 }
}
