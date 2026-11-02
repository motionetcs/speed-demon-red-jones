#include <algorithm>
#include <array>
#include <atomic>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <random>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>
#include <sys/mman.h>
#include <unistd.h>
#include "partitions_extracted.hpp"

static uint64_t checks=0;
static void require(bool condition){++checks;if(!condition)throw std::runtime_error("partition model mismatch");}
static std::vector<size_t> ends_of(const char* data,size_t size){
    std::vector<size_t> result;
    for(size_t i=0;i<size;++i)if(data[i]=='\n')result.push_back(i+1);
    if(result.empty()||result.back()!=size)result.push_back(size);
    return result;
}
template<size_t Block> static void check_split(const char* data,size_t size){
    auto actual=split_actual<Block>(data,size);auto ends=ends_of(data,size);
    size_t parts=size/Block+(size%Block!=0);require(actual.parts==parts);
    require(actual.boundaries.size()==parts+1);
    require(actual.boundaries.front()==data&&actual.boundaries.back()==data+size);
    for(size_t i=1;i<parts;++i){
        size_t cut=i*Block;auto at=std::lower_bound(ends.begin(),ends.end(),cut);
        require(at!=ends.end());require(size_t(actual.boundaries[i]-data)==*at);
    }
    for(size_t i=0;i<parts;++i){
        require(actual.boundaries[i]<=actual.boundaries[i+1]);
        require(actual.boundaries[i]>=data&&actual.boundaries[i+1]<=data+size);
    }
}
template<size_t Block> static void check_claims(const std::string& input,unsigned workers){
    auto p=split_actual<Block>(input.data(),input.size());
    std::vector<size_t> starts{0};
    for(size_t i=0;i<input.size();++i)if(input[i]=='\n'&&i+1<input.size())starts.push_back(i+1);
    if(input.empty())starts.clear();
    std::vector<std::atomic<unsigned>> seen(starts.size()),claimed(p.parts);
    std::atomic<size_t> next_part{0};std::atomic<bool> bad{false};
    std::array<std::vector<size_t>,12> ownership;
    std::vector<std::jthread> threads;
    for(unsigned worker=0;worker<workers;++worker)threads.emplace_back([&,worker]{
        claims_actual(p.boundaries,p.parts,next_part,[&](size_t part,const char* begin,const char* end){
            if(claimed[part].fetch_add(1,std::memory_order_relaxed)!=0)bad=true;
            auto& mine=ownership[worker];if(!mine.empty()&&mine.back()>=part)bad=true;mine.push_back(part);
            size_t first=size_t(begin-input.data()),last=size_t(end-input.data());
            auto at=std::lower_bound(starts.begin(),starts.end(),first);
            if(first<last&&(at==starts.end()||*at!=first))bad=true;
            for(;at!=starts.end()&&*at<last;++at){
                size_t index=size_t(at-starts.begin());
                size_t finish=index+1<starts.size()?starts[index+1]:input.size();
                if(finish>last||seen[index].fetch_add(1,std::memory_order_relaxed)!=0)bad=true;
            }
            if((part+worker)%11==0)std::this_thread::yield();
        });
    });
    threads.clear();require(!bad.load());
    for(auto& value:seen)require(value.load()==1);
    for(auto& value:claimed)require(value.load()==1);
    require(next_part.load()==p.parts+workers);
}
int main(){
    std::mt19937_64 rng(0x376cefa17ULL);
    for(size_t n=0;n<=128;++n){
        for(size_t place=0;place<=n;++place){
            std::string text(n,'a');if(place<n)text[place]='\n';
            check_split<1>(text.data(),text.size());check_split<7>(text.data(),text.size());
            check_split<31>(text.data(),text.size());check_split<(size_t(1)<<22)>(text.data(),text.size());
        }
    }
    for(unsigned repeat=0;repeat<1200;++repeat){
        std::string text(rng()%16385,'x');
        for(auto& c:text){c=char(rng()%256);if(rng()%5==0)c='\n';}
        check_split<7>(text.data(),text.size());check_split<64>(text.data(),text.size());
        check_split<511>(text.data(),text.size());check_split<4096>(text.data(),text.size());
        check_split<(size_t(1)<<22)>(text.data(),text.size());
    }
    std::string long_lines(65537,'x');long_lines[32000]='\n';long_lines.back()='\n';
    std::string records;
    while(records.size()<(size_t(1)<<23)+257){
        records.append(40+rng()%137,'z');records.push_back('\n');
    }
    for(unsigned workers=1;workers<=12;++workers){
        check_claims<7>(long_lines,workers);check_claims<4096>(records.substr(0,32771),workers);
        check_claims<(size_t(1)<<22)>(records,workers);
        check_claims<(size_t(1)<<22)>(std::string(),workers);
    }
    long page_value=sysconf(_SC_PAGESIZE);require(page_value>0);size_t page=size_t(page_value);
    for(size_t delta:std::array<size_t,5>{0,1,31,255,4095}){
        size_t length=(size_t(1)<<22)+delta;
        size_t middle=(length+page-1)/page*page,total=middle+2*page;
        void* allocation=mmap(nullptr,total,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANONYMOUS,-1,0);
        require(allocation!=MAP_FAILED);char* base=static_cast<char*>(allocation);
        require(mprotect(base,page,PROT_NONE)==0&&mprotect(base+page+middle,page,PROT_NONE)==0);
        for(bool right:{false,true}){
            char* bytes=right?base+page+middle-length:base+page;
            std::memset(base+page,'\n',middle);std::memset(bytes,'a',length);
            for(size_t i=39;i<length;i+=73)bytes[i]='\n';
            check_split<(size_t(1)<<22)>(bytes,length);
        }
        require(munmap(allocation,total)==0);
    }
    std::printf("PASS376 extracted partition/claim independent-oracle/empty/equal-boundary/all-worker/guard model %llu checks\n",static_cast<unsigned long long>(checks));
}
