#include "source/track-d/distance_map.hpp"
#include "source/track-d/radix_heap.hpp"
#include "source/track-d/edge_store.hpp"
#include <algorithm>
#include <cassert>
#include <iostream>
#include <map>
#include <random>
#include <unordered_map>
using Item=std::pair<uint64_t,uint32_t>;
struct State {
    static constexpr uint64_t infinity=UINT64_MAX;
    FastDistances own,other;RadixHeap heap;uint64_t best=infinity;
    std::array<Item,32> work{};std::array<std::pair<uint32_t,uint32_t>,32> ranges{};size_t count=0;
    EdgeStore adjacency;std::unordered_map<uint32_t,uint32_t> wide_weights;bool from_source;
    State(size_t edges,uint32_t nodes,bool side):adjacency(edges,nodes),from_source(side){}
    template<bool Compact> void kernel(){
#include "pending-block.hpp"
    }
};
static uint64_t value(const std::map<uint32_t,uint64_t>& map,uint32_t node){auto it=map.find(node);return it==map.end()?UINT64_MAX:it->second;}
template<bool Compact> void stream(bool side){
    std::mt19937_64 random(0x2900d+unsigned(Compact)*31+unsigned(side));
    uint64_t full_flushes=0,partial_flushes=0,split_nodes=0,stale_nodes=0,growth=0,wide_runs=0,checks=0;
    const unsigned boundaries[]={0,1,2,31,32,63,64,127,128,129,255,256,257,513};
    for(unsigned iteration=0;iteration<174;++iteration){
        size_t count=iteration<14?1:32;std::vector<std::vector<std::pair<uint32_t,uint32_t>>> rows(count);size_t total=0;
        uint64_t base=iteration%9==0?uint64_t(UINT32_MAX)+64:0;
        std::array<Item,32> work{};
        for(size_t k=0;k<count;++k){
            uint32_t source=uint32_t(k);if(!Compact&&iteration%7==0)source=UINT32_MAX-uint32_t(k)-1;
            work[k]={base+(k?uint64_t(10+k%32):0),source};
            unsigned degree=iteration<14?boundaries[iteration]:unsigned(random()%320);
            for(unsigned j=0;j<degree;++j){
                uint32_t to=uint32_t(random()%65536);if(j%11==0)to=source;if(j%13==0)to=uint32_t((k+1)%count);
                if(!Compact&&j%29==0)to=UINT32_MAX-j-1;
                uint32_t weights[]={0,1,31,63,64,127,2046,2047,65534,65535,UINT32_MAX};uint32_t weight=weights[random()%11];rows[k].emplace_back(to,weight);
            }
            if(degree&&k==0&&count>1)rows[k][0]={work[1].second,1};
            if(degree>128)++split_nodes;total+=degree;
        }
        // The work[1] source is fixed1 except the explicit wide-ID stream.
        if(count>1&&!rows[0].empty())rows[0][0]={work[1].second,1};
        State state(total,Compact?(1U<<21):UINT32_MAX,side);state.count=count;state.work=work;
        std::map<uint32_t,uint64_t> expected,opposite;std::vector<Item> pushed;
        for(size_t k=0;k<count;++k){uint64_t d=work[k].first;if(iteration%5==0&&k%3==0&&d)d-=1;state.own.improve(work[k].second,d);expected[work[k].second]=d;}
        bool grow_case=iteration==173;
        if(grow_case){for(uint32_t node=0;node<4095;++node){state.own.improve(node,base+1000);expected[node]=std::min(value(expected,node),base+1000);}assert(state.own.bits==10);}
        for(unsigned j=0;j<128;++j){uint32_t node=uint32_t(random()%65536);uint64_t d=base+random()%100000;state.other.improve(node,d);opposite[node]=std::min(value(opposite,node),d);}
        uint32_t edge_index=0;
        for(size_t k=0;k<count;++k){state.ranges[k].first=edge_index;for(auto [node,weight]:rows[k]){uint32_t tag=std::min(weight,Compact?EdgeStore::small_limit:uint32_t(UINT16_MAX));state.adjacency.template set<Compact>(edge_index,node,tag);if(weight>=(Compact?EdgeStore::small_limit:uint32_t(UINT16_MAX)))state.wide_weights.emplace(edge_index*2+(side?0:1),weight);++edge_index;}state.ranges[k].second=edge_index;}
        uint64_t best=UINT64_MAX;
        for(size_t k=0;k<count;++k){auto [distance,source]=work[k];if(distance!=value(expected,source)){++stale_nodes;continue;}for(auto [node,weight]:rows[k]){uint64_t candidate=distance+weight;if(candidate<value(expected,node)){expected[node]=candidate;pushed.emplace_back(candidate,node);uint64_t d=value(opposite,node);if(d!=UINT64_MAX)best=std::min(best,candidate+d);}}}
        unsigned before=state.own.bits;state.template kernel<Compact>();if(state.own.bits>before)++growth;if(base)++wide_runs;
        for(auto [node,d]:expected){assert(state.own.get(node)==d);++checks;}for(auto [node,d]:opposite){assert(state.other.get(node)==d);++checks;}assert(state.best==best);assert(state.heap.count==pushed.size());std::vector<Item> actual;while(!state.heap.empty())actual.push_back(state.heap.pop());std::sort(actual.begin(),actual.end());std::sort(pushed.begin(),pushed.end());assert(actual==pushed);full_flushes+=total/128;partial_flushes+=total%128!=0;
        if(grow_case)assert(state.own.bits>before);
    }
    assert(full_flushes&&partial_flushes&&split_nodes&&stale_nodes&&growth&&wide_runs);
    std::cout<<"PASS gathered-relax exact-block compact="<<Compact<<" side="<<side<<" model-checks="<<checks<<" full="<<full_flushes<<" partial="<<partial_flushes<<" split="<<split_nodes<<" stale="<<stale_nodes<<" growth="<<growth<<" wide="<<wide_runs<<"\n";
}
int main(){stream<true>(false);stream<true>(true);stream<false>(false);stream<false>(true);}
