#ifndef ENDPOINTS_HEADER
#error "Pass the exact candidate endpoint_table.hpp as ENDPOINTS_HEADER"
#endif
#include ENDPOINTS_HEADER
#include <cassert>
#include <deque>
#include <iostream>
#include <set>
#include <string>
#include <thread>
#include <unordered_map>
#include <sys/mman.h>
#include <unistd.h>

static size_t checks=0;

template<size_t Slots>
void check(EndpointSpanCache<Slots>& cache, const char* start, size_t available) {
    size_t length=0;
    while (length<available && start[length]!=' ') ++length;
    const char* cursor=start;
    bool threw=false;
    try {
        uint16_t id=cache.read(cursor,start+available);
        assert(length<available);
        assert(cursor==start+length);
        assert(id<4096);
        assert(cache.shared.canonical[id]==std::string_view(start,length));
    } catch (const std::runtime_error&) {
        threw=true;
    }
    assert(threw==(length==available));
    ++checks;
}

template<size_t Slots>
void corpus() {
    for (unsigned byte=0;byte<256;++byte) {
        Endpoints shared;
        EndpointSpanCache<Slots> cache(shared);
        std::deque<std::string> stable;
        for (size_t length=0;length<=128;++length) {
            stable.emplace_back(length,char(byte));
            stable.back()+=" 200 17\n";
            const auto& text=stable.back();
            check(cache,text.data(),text.size());
            check(cache,text.data(),text.size());
            check(cache,text.data(),length);
        }
    }
    {
        Endpoints shared;
        EndpointSpanCache<Slots> cache(shared);
        std::deque<std::string> stable;
        for (size_t length:{0U,1U,3U,15U,16U,17U,125U,65534U,65535U,65536U,1048576U}) {
            stable.emplace_back(length,'z');
            stable.back()+=" 200 4294967295\n";
            const auto& text=stable.back();
            const char* first=text.data();
            auto id=cache.read(first,first+text.size());
            for (unsigned repeat=0;repeat<3;++repeat) {
                const char* again=text.data();
                assert(cache.read(again,again+text.size())==id);
                check(cache,text.data(),text.size());
                check(cache,text.data(),length);
            }
        }
    }
    {
        Endpoints shared;
        EndpointSpanCache<Slots> cache(shared);
        std::deque<std::string> stable;
        for (unsigned i=0;i<4097;++i) stable.push_back("/identical-first-sixteen/"+std::to_string(i)+" 500 1\n");
        for (unsigned i=0;i<4096;++i) {
            const auto& text=stable[i];const char* p=text.data();
            assert(cache.read(p,p+text.size())==i);
            check(cache,text.data(),text.size());
        }
        for (unsigned i=4096;i>0;--i) {
            const auto& text=stable[i-1];const char* p=text.data();
            assert(cache.read(p,p+text.size())==i-1);
        }
        bool threw=false;const auto& text=stable.back();const char* p=text.data();
        try { cache.read(p,p+text.size()); } catch(const std::runtime_error&) { threw=true; }
        assert(threw && shared.canceled.load());
    }
    // Stable equal prefixes with different lengths and suffixes exercise false
    // hint hits. Slots=1/2 deliberately force hint replacement collisions.
    {
        Endpoints shared;
        EndpointSpanCache<Slots> cache(shared);
        std::deque<std::string> stable;
        for (unsigned i=0;i<511;++i) stable.push_back(std::string(16,'x')+std::string(i%53,'a')+std::to_string(i)+" 200 1\n");
        std::unordered_map<std::string,unsigned> ids;
        for (unsigned i=0;i<7000;++i) {
            const auto& text=stable[(i*137)%stable.size()];const char* p=text.data();
            unsigned id=cache.read(p,p+text.size());
            auto [at,inserted]=ids.emplace(std::string(text.data(),size_t(p-text.data())),id);
            assert(inserted || at->second==id);
            check(cache,text.data(),text.size());
            check(cache,text.data(),size_t(p-text.data()));
        }
        std::set<unsigned> distinct;
        for (const auto& item:ids) distinct.insert(item.second);
        assert(distinct.size()==stable.size());
    }
}

void guards() {
    size_t page=size_t(sysconf(_SC_PAGESIZE));
    auto* mapping=static_cast<char*>(mmap(nullptr,page*2,PROT_READ|PROT_WRITE,MAP_PRIVATE|MAP_ANON,-1,0));
    assert(mapping!=MAP_FAILED && mprotect(mapping+page,page,PROT_NONE)==0);
    for (size_t length=0;length<=256;++length) {
        std::string stable(length,'x'); stable+=' ';
        char* start=mapping+page-stable.size();
        std::memcpy(start,stable.data(),stable.size());
        Endpoints shared;
        EndpointSpanCache<2048> cache(shared);
        check(cache,stable.data(),stable.size()); // Canonical view has stable ownership.
        for (size_t available=0;available<=stable.size();++available) check(cache,start,available);
        check(cache,start,stable.size()); // Actual physical protected-page end.
    }
    assert(munmap(mapping,page*2)==0);
    for (size_t offset=0;offset<64;++offset) {
        Endpoints shared;
        EndpointSpanCache<2048> cache(shared);
        std::string stable(offset,'!');stable+=std::string(79,'a')+" 200 7\n";
        const char* start=stable.data()+offset;
        check(cache,start,stable.size()-offset);
        check(cache,start,stable.size()-offset);
    }
}

void concurrent() {
    std::vector<std::string> stable;stable.reserve(701);
    for (unsigned i=0;i<701;++i) stable.push_back("/identical-first-sixteen/"+std::to_string(i)+std::string(i%13,'a')+" 200 1\n");
    for (unsigned workers=1;workers<=12;++workers) {
        Endpoints shared;
        std::array<std::atomic<unsigned>,701> ids;
        for (auto& id:ids) id.store(UINT32_MAX);
        std::atomic<bool> mismatch{false};std::vector<std::thread> threads;
        for (unsigned worker=0;worker<workers;++worker) threads.emplace_back([&,worker] {
            EndpointSpanCache<2048> cache(shared);
            for (unsigned i=0;i<2500;++i) {
                unsigned k=(i*137+worker*13)%stable.size();const auto& text=stable[k];const char* p=text.data();
                unsigned id=cache.read(p,p+text.size()),expected=UINT32_MAX;
                if (!ids[k].compare_exchange_strong(expected,id) && expected!=id) mismatch.store(true);
                if (shared.canonical[id]!=std::string_view(text.data(),size_t(p-text.data()))) mismatch.store(true);
            }
        });
        for (auto& thread:threads) thread.join();
        assert(!mismatch.load() && shared.used.load()==stable.size());
        std::set<unsigned> distinct;for (auto& id:ids) distinct.insert(id.load());
        assert(distinct.size()==stable.size());
    }
}

int main() {
    corpus<1>();corpus<2>();corpus<2048>();guards();concurrent();
    std::cout<<"PASS "<<checks<<" exact span/scalar-oracle, byte, truncation, alias, collision, long-key, ID4095/limit, guard/alignment, immutable lifetime and private-cache publication checks; concurrency all1..12\n";
}
