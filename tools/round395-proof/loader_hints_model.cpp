#include "source/track-d/mapped_allocator.hpp"
#include "source/track-d/load_cursors.hpp"
#include "source/track-d/edge_store.hpp"
#include <array>
#include <cstdio>
#include <cstdlib>
#include <limits>
#include <numeric>
#include <random>
#include <thread>

using Prefix=std::vector<uint32_t,MappedAllocator<uint32_t>>;
static std::atomic<uint64_t> checks{0};
static void require(bool condition) {
    if (!condition) { std::fputs("joined cursor model mismatch\n",stderr);std::abort(); }
    checks.fetch_add(1,std::memory_order_relaxed);
}
template<bool Wide> static void read_after_join(const SharedCursor& cursor,const std::vector<uint32_t>& expected) {
    for (size_t node=0;node+1<expected.size();++node) {
        auto range=cursor.range<Wide>(static_cast<uint32_t>(node));
        require(range.first==expected[node]&&range.second==expected[node+1]);
        require(cursor.end<Wide>(static_cast<uint32_t>(node))==expected[node+1]);
        cursor.prefetch<Wide,false>(node?static_cast<uint32_t>(node-1):0);
    }
}
static void actual_claims(const std::vector<uint32_t>& degrees,unsigned workers,bool force_wide) {
    Prefix prefix(degrees.size()+1);
    uint64_t sum=0;
    for (size_t node=0;node<degrees.size();++node) {
        sum+=degrees[node];require(sum<=UINT32_MAX);prefix[node+1]=static_cast<uint32_t>(sum);
    }
    std::vector<uint32_t> expected(prefix.begin(),prefix.end());
    SharedCursor cursor(prefix);
    std::vector<uint32_t> events;
    for (uint32_t node=0;node<degrees.size();++node) {
        for (uint32_t i=0;i<degrees[node];++i) events.push_back(node);
    }
    std::mt19937 rng(static_cast<uint32_t>(degrees.size()+workers*334));
    std::shuffle(events.begin(),events.end(),rng);
    std::vector<std::vector<uint32_t>> claims(workers);
    std::vector<std::thread> threads;
    for (unsigned worker=0;worker<workers;++worker) {
        threads.emplace_back([&,worker] {
            for (size_t i=worker;i<events.size();i+=workers) {
                uint32_t node=events[i];
                cursor.prefetch<true,true>(node);
                if(!cursor.wide_blocks)cursor.prefetch<false,true>(node);
                uint32_t slot=force_wide?cursor.take<true>(node):cursor.take(node);
                require(slot>=expected[node]&&slot<expected[node+1]);
                claims[worker].push_back(slot);
            }
        });
    }
    for (auto& thread:threads) thread.join();
    std::vector<uint32_t> all;
    for (const auto& row:claims) all.insert(all.end(),row.begin(),row.end());
    std::sort(all.begin(),all.end());require(all.size()==events.size());
    for (size_t i=0;i<all.size();++i) require(all[i]==i);
    Prefix().swap(prefix);require(prefix.empty()&&prefix.capacity()==0);
    // These range reads occur after the actual mapped prefix has been unmapped.
    read_after_join<true>(cursor,expected);
    if (!cursor.wide_blocks) read_after_join<false>(cursor,expected);
}
static void synthetic_extremes(const std::vector<uint32_t>& expected,unsigned workers) {
    Prefix prefix(expected.begin(),expected.end());
    SharedCursor cursor(prefix);
    std::vector<std::thread> threads;
    for (unsigned worker=0;worker<workers;++worker) {
        threads.emplace_back([&,worker] {
            for (size_t node=worker;node+1<expected.size();node+=workers) {
                size_t block=node>>SharedCursor::shift;
                uint32_t wide_index=cursor.wide_index[block];
                if (wide_index==UINT32_MAX) {
                    uint32_t delta=expected[node+1]-cursor.base[block];require(delta<=UINT16_MAX);
                    std::atomic_ref(cursor.small[node]).store(static_cast<uint16_t>(delta),std::memory_order_relaxed);
                } else {
                    std::atomic_ref(cursor.wide[size_t(wide_index)*SharedCursor::block_size+(node&(SharedCursor::block_size-1))]).store(expected[node+1],std::memory_order_relaxed);
                }
            }
        });
    }
    for (auto& thread:threads) thread.join();
    Prefix().swap(prefix);
    read_after_join<true>(cursor,expected);
    if (!cursor.wide_blocks) read_after_join<false>(cursor,expected);
}
template<bool Compact> static void edge_hints(){
    for(size_t count:{size_t(0),size_t(1),size_t(15),size_t(16),size_t(17),size_t(257)}){
        EdgeStore edges(count,Compact?100U:(1U<<21)+1);
        for(uint32_t i=0;i<count;++i){
            edges.prefetch<Compact,true>(i);
            edges.set<Compact>(i,i*7,Compact?i%2048:i%65536);
        }
        for(uint32_t i=0;i<count;++i){
            edges.prefetch<Compact,false>(i);
            auto value=edges.get<Compact>(i);
            require(value.first==i*7&&value.second==(Compact?i%2048:i%65536));
        }
    }
}
int main() {
    edge_hints<true>();edge_hints<false>();

    for (unsigned workers:{1U,2U,6U,12U}) {
        actual_claims({},workers,false);
        actual_claims({0},workers,true);
        actual_claims({1,0,2,0},workers,false);
        actual_claims({65535,0,0},workers,true);
        actual_claims({65536,0,0},workers,false);
        for (size_t nodes:{size_t(4095),size_t(4096),size_t(4097),size_t(8191),size_t(8192),size_t(8193)}) {
            std::vector<uint32_t> degrees(nodes);
            for (size_t node=0;node<nodes;++node) degrees[node]=static_cast<uint32_t>((node*17+3)%4);
            degrees.front()+=257;degrees.back()+=511;
            actual_claims(degrees,workers,true);
        }
        std::vector<uint32_t> mixed(17000);
        for (size_t i=0;i<mixed.size();++i) mixed[i]=static_cast<uint32_t>(i%6);
        mixed[0]+=70000;mixed[8192]+=65536;mixed.back()+=100000;
        actual_claims(mixed,workers,true);
        synthetic_extremes({0,UINT32_MAX-5,UINT32_MAX},workers);
        synthetic_extremes({0,0,UINT16_MAX,UINT16_MAX+1,UINT32_MAX},workers);
        std::vector<uint32_t> large(8194);
        for (size_t i=4096;i<large.size();++i) {
            uint64_t delta=uint64_t(i-4096)*UINT16_MAX/(large.size()-4097);
            large[i]=UINT32_MAX-UINT16_MAX+static_cast<uint32_t>(delta);
        }
        require(large.back()==UINT32_MAX);
        synthetic_extremes(large,workers);
    }
    std::printf("PASS joined cursor model %llu checks; actual atomic claims/unique coverage/post-unmap readonly ranges, narrow/wide block seams, forced-wide dispatch,0/65535/65536/uint32 extremes; synthetic final-state stores are separate from literal claim coverage\n",static_cast<unsigned long long>(checks.load()));
}
