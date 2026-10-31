#include ORDERED_OUTPUT_HEADER
#include <algorithm>
#include <atomic>
#include <cassert>
#include <iostream>
#include <iterator>
#include <numeric>
#include <random>
#include <thread>
#include <vector>
#include <unistd.h>

using Bytes=decltype(Output{}.bytes);
void string_lifetime(size_t n){
    Bytes value;for(size_t i=0;i<n;++i)value.push_back(char(i%251));
    assert(value.size()==n&&value.data()[n]=='\0');for(size_t i=0;i<n;++i)assert(static_cast<unsigned char>(value[i])==i%251);
    auto* address=value.data();size_t bytes=value.capacity()+1;unsigned char state[16384];size_t pages=(bytes+size_t(sysconf(_SC_PAGESIZE))-1)/size_t(sysconf(_SC_PAGESIZE));assert(pages<=sizeof(state));
    std::thread other([&]{Bytes().swap(value);});other.join();assert(value.empty());
#ifdef __APPLE__
    assert(mincore(address,bytes,reinterpret_cast<char*>(state))==0);for(size_t i=0;i<pages;++i)assert((state[i]&MINCORE_INCORE)==0);
#else
    assert(mincore(address,bytes,state)!=0);
#endif
}
int main(int argc,char** argv){
    assert(argc==2);std::filesystem::path root=argv[1];std::filesystem::create_directories(root);
    for(size_t n:{1023U,1024U,1025U,4095U,4096U,4097U,100003U,500001U})string_lifetime(n);
    for(unsigned workers=1;workers<=12;++workers)for(unsigned pattern=0;pattern<4;++pattern){
        auto path=root/(std::to_string(workers)+"-"+std::to_string(pattern));OrderedOutput writer(path);
        std::array<std::string,72> expected;std::vector<unsigned> order(72);std::iota(order.begin(),order.end(),0);
        std::mt19937 rng(workers*7937+pattern);if(pattern==1)std::reverse(order.begin(),order.end());if(pattern>=2)std::shuffle(order.begin(),order.end(),rng);
        // Empty hours, NUL-containing bytes, long first-hour lag and varying growth.
        for(unsigned h=0;h<72;++h){size_t n=h%7?size_t(h+1)*193:0;if(h==0&&pattern==3)n=1048576;expected[h].resize(n);for(size_t i=0;i<n;++i)expected[h][i]=char((i+h)%251);}
        std::atomic<unsigned> next{0};std::vector<std::thread> threads;
        for(unsigned w=0;w<workers;++w)threads.emplace_back([&]{for(;;){unsigned k=next.fetch_add(1);if(k>=72)return;unsigned h=order[k];auto& bytes=writer.hours[h].bytes;bytes.append(expected[h].data(),expected[h].size());if((h+k)%5==0)std::this_thread::yield();writer.publish(h);}});
        for(auto& t:threads)t.join();writer.finish();assert(writer.next==72);for(const auto& h:writer.hours)assert(h.bytes.empty());
        std::ifstream input(path,std::ios::binary);std::string actual((std::istreambuf_iterator<char>(input)),{}),joined;for(const auto& h:expected)joined+=h;assert(actual==joined);
    }
    auto bad=root/"directory";std::filesystem::create_directory(bad);bool threw=false;try{OrderedOutput writer(bad);}catch(const std::runtime_error&){threw=true;}assert(threw);
#ifdef __linux__
    threw=false;try{OrderedOutput writer("/dev/full");writer.hours[0].bytes.append(32768,'x');writer.publish(0);}catch(const std::runtime_error&){threw=true;}assert(threw);
#endif
    std::cout<<"PASS mapped char growth/NUL/terminator/direct cross-thread release; all1..12 producers ordered/reverse/random/empty/lag output and normal sink failures\n";
}
