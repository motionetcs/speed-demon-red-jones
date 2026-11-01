#include EDGE_HEADER
#include PARALLEL_HEADER
#include <algorithm>
#include <array>
#include <cassert>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <stdexcept>
#include <string>
#include <tuple>
#include <unordered_map>

using Pair=std::pair<uint32_t,uint32_t>;
using Key=std::pair<unsigned,uint32_t>;
constexpr uint64_t infinity=UINT64_MAX/4;
struct Input {
    std::string name;
    uint32_t n=0,k=0;
    int minimum=0,maximum=-1;
    bool shared=false;
    std::vector<uint32_t> ids,workers;
    std::vector<std::tuple<uint32_t,uint32_t,uint32_t>> edges;
    std::vector<Pair> queries;
};
using Matrix=std::vector<std::vector<uint64_t>>;
void close_paths(Matrix& distance){
    for(size_t via=0;via<distance.size();++via){
        for(size_t from=0;from<distance.size();++from){
            for(size_t to=0;to<distance.size();++to){
                if(distance[from][via]<infinity&&distance[via][to]<infinity){
                    distance[from][to]=std::min(distance[from][to],distance[from][via]+distance[via][to]);
                }
            }
        }
    }
}
Matrix original_paths(const Input& input){
    Matrix result(input.k,std::vector<uint64_t>(input.k,infinity));
    for(size_t i=0;i<input.k;++i){result[i][i]=0;}
    for(auto [u,v,w]:input.edges){result[u][v]=std::min(result[u][v],uint64_t(w));}
    close_paths(result);
    return result;
}
struct Context {
    const Input* input=nullptr;
    Matrix original;
    std::unordered_map<uint32_t,size_t> logical;
    std::vector<Pair> forward,reverse;
    std::set<uint32_t> selected;
    std::map<Key,Pair> expected;
    std::array<std::array<bool,12>,3> started{},finished{};
    unsigned phase=0,fail_phase=0,fail_worker=0;
    bool saw_shared=false;
};
Context* current=nullptr;
struct InjectedFailure:std::runtime_error {InjectedFailure():std::runtime_error("test-only worker failure") {}};
template<class Function> void observed_parallel(unsigned count,Function function){
    assert(current&&current->phase<3);
    unsigned phase=current->phase++;
    ::parallel(count,[&](unsigned worker){
        current->started[phase][worker]=true;
        struct Finish {bool& value;~Finish(){value=true;}} finish{current->finished[phase][worker]};
        if(current->fail_phase==phase+1&&current->fail_worker==worker){throw InjectedFailure();}
        function(worker);
    });
}
Pair decoded(const EdgeStore& store,uint32_t index,unsigned reverse,const std::unordered_map<uint32_t,uint32_t>& wide){
    auto [node,tag]=store.get(index);
    uint32_t weight=tag==store.weight_limit?wide.at(index*2+reverse):tag;
    return {node,weight};
}
std::vector<Pair> snapshot(const EdgeStore& store,unsigned reverse,const std::unordered_map<uint32_t,uint32_t>& wide,size_t size){
    std::vector<Pair> result;
    for(size_t index=0;index<size;++index){result.push_back(decoded(store,static_cast<uint32_t>(index),reverse,wide));}
    return result;
}
template<class Plans> void audit_plans(const Plans& plans,const std::vector<uint8_t>& flags,
    const std::vector<Pair>& queries,const std::vector<uint32_t>& offsets,
    const std::vector<uint32_t>& reverse_offsets,const EdgeStore& edges,
    const EdgeStore& reverse_edges,const std::unordered_map<uint32_t,uint32_t>& wide){
    assert(current->phase==2);
    assert(snapshot(edges,0,wide,current->forward.size())==current->forward);
    assert(snapshot(reverse_edges,1,wide,current->reverse.size())==current->reverse);
    std::set<uint32_t> pins;
    for(auto [source,target]:queries){pins.insert(source);pins.insert(target);}
    for(auto node:current->input->ids){
        assert((flags[node]==1)==bool(pins.count(node)));
    }
    for(const auto& worker:plans){
        for(auto plan:worker){
            assert(current->selected.insert(plan.node).second);
            assert(!pins.count(plan.node));
            assert(offsets[plan.node+1]-offsets[plan.node]==2);
            assert(reverse_offsets[plan.node+1]-reverse_offsets[plan.node]==2);
        }
    }
    assert(current->selected.size()>=static_cast<size_t>(current->input->minimum));
    if(current->input->maximum>=0){assert(current->selected.size()<=static_cast<size_t>(current->input->maximum));}
    std::map<uint32_t,unsigned> hubs;
    std::set<Key> reads;
    for(auto node:current->selected){
        for(uint32_t i=offsets[node];i<offsets[node+1];++i){reads.insert({0,i});}
        for(uint32_t i=reverse_offsets[node];i<reverse_offsets[node+1];++i){reads.insert({1,i});}
    }
    for(const auto& worker:plans){
        for(auto plan:worker){
            uint32_t node=plan.node;
            auto [u,a]=current->forward[offsets[node]];
            auto [v,b]=current->forward[offsets[node]+1];
            assert(u!=v&&u!=node&&v!=node);
            assert(!current->selected.count(u)&&!current->selected.count(v));
            current->saw_shared|=++hubs[u]>1;
            current->saw_shared|=++hubs[v]>1;
            assert(plan.iu>=offsets[u]&&plan.iu<offsets[u+1]);
            assert(plan.iv>=offsets[v]&&plan.iv<offsets[v+1]);
            assert(plan.ru>=reverse_offsets[u]&&plan.ru<reverse_offsets[u+1]);
            assert(plan.rv>=reverse_offsets[v]&&plan.rv<reverse_offsets[v+1]);
            auto [iu,c]=current->forward[plan.iu];
            auto [iv,d]=current->forward[plan.iv];
            auto ru=current->reverse[plan.ru],rv=current->reverse[plan.rv];
            assert(iu==node&&iv==node&&ru==Pair(node,a)&&rv==Pair(node,b));
            uint64_t first=uint64_t(c)+b,second=uint64_t(d)+a;
            assert(first<edges.weight_limit&&second<edges.weight_limit);
            std::array<std::pair<Key,Pair>,4> writes{
                std::pair{Key{0,plan.iu},Pair{v,static_cast<uint32_t>(first)}},
                std::pair{Key{0,plan.iv},Pair{u,static_cast<uint32_t>(second)}},
                std::pair{Key{1,plan.rv},Pair{u,static_cast<uint32_t>(first)}},
                std::pair{Key{1,plan.ru},Pair{v,static_cast<uint32_t>(second)}}
            };
            for(auto [key,value]:writes){
                assert(!reads.count(key));
                assert(current->expected.emplace(key,value).second);
            }
        }
    }
    if(current->input->shared){assert(current->saw_shared);}
}
void audit_result(const std::vector<uint32_t>& offsets,const std::vector<uint32_t>& reverse_offsets,
    const EdgeStore& edges,const EdgeStore& reverse_edges,const std::unordered_map<uint32_t,uint32_t>& wide){
    assert(current->phase==3);
    auto forward=snapshot(edges,0,wide,current->forward.size());
    auto reverse=snapshot(reverse_edges,1,wide,current->reverse.size());
    for(unsigned direction=0;direction<2;++direction){
        const auto& before=direction?current->reverse:current->forward;
        const auto& after=direction?reverse:forward;
        for(size_t i=0;i<after.size();++i){
            auto found=current->expected.find({direction,static_cast<uint32_t>(i)});
            assert(after[i]==(found==current->expected.end()?before[i]:found->second));
        }
    }
    std::multiset<std::tuple<uint32_t,uint32_t,uint32_t>> forward_edges,reverse_edges_set;
    const auto& input=*current->input;
    Matrix after(input.k,std::vector<uint64_t>(input.k,infinity));
    for(size_t i=0;i<input.k;++i){after[i][i]=0;}
    for(auto u:input.ids){
        if(current->selected.count(u)){continue;}
        for(uint32_t i=offsets[u];i<offsets[u+1];++i){
            auto [v,w]=forward[i];assert(!current->selected.count(v));
            forward_edges.insert({u,v,w});
            size_t from=current->logical.at(u),to=current->logical.at(v);
            after[from][to]=std::min(after[from][to],uint64_t(w));
        }
        for(uint32_t i=reverse_offsets[u];i<reverse_offsets[u+1];++i){
            auto [v,w]=reverse[i];assert(!current->selected.count(v));
            reverse_edges_set.insert({v,u,w});
        }
    }
    assert(forward_edges==reverse_edges_set);
    close_paths(after);
    for(size_t u=0;u<input.k;++u){
        if(current->selected.count(input.ids[u])){continue;}
        for(size_t v=0;v<input.k;++v){
            if(!current->selected.count(input.ids[v])){assert(after[u][v]==current->original[u][v]);}
        }
    }
}

size_t execute(const Input& input,unsigned loaders,unsigned fail_phase=0){
    uint32_t n=input.n;
    std::vector<Pair> queries;
    for(auto [u,v]:input.queries){queries.emplace_back(input.ids[u],input.ids[v]);}
    std::vector<uint32_t> offsets(size_t(n)+1),reverse_offsets(size_t(n)+1);
    for(auto [u,v,w]:input.edges){(void)w;++offsets[size_t(input.ids[u])+1];++reverse_offsets[size_t(input.ids[v])+1];}
    for(size_t node=1;node<=n;++node){offsets[node]+=offsets[node-1];reverse_offsets[node]+=reverse_offsets[node-1];}
    auto forward_cursor=offsets,reverse_cursor=reverse_offsets;
    EdgeStore edges(input.edges.size(),n),reverse_edges(input.edges.size(),n);
    std::unordered_map<uint32_t,uint32_t> wide_weights;
    for(auto [u,v,w]:input.edges){
        uint32_t from=input.ids[u],to=input.ids[v],f=forward_cursor[from]++,r=reverse_cursor[to]++;
        uint32_t tag=std::min(w,edges.weight_limit);
        edges.set(f,to,tag);reverse_edges.set(r,from,tag);
        if(w>=edges.weight_limit){wide_weights.emplace(f*2,w);wide_weights.emplace(r*2+1,w);}
    }
    Context context;context.input=&input;context.original=original_paths(input);context.fail_phase=fail_phase;context.fail_worker=loaders-1;
    for(size_t i=0;i<input.ids.size();++i){context.logical.emplace(input.ids[i],i);}
    context.forward=snapshot(edges,0,wide_weights,input.edges.size());context.reverse=snapshot(reverse_edges,1,wide_weights,input.edges.size());current=&context;
    bool failed=false;
    try{
#define parallel observed_parallel
#include OBSERVED_BLOCK
#undef parallel
    }catch(const InjectedFailure&){failed=true;}
    if(fail_phase){
        assert(failed&&context.phase==fail_phase);
        assert(snapshot(edges,0,wide_weights,input.edges.size())==context.forward);
        assert(snapshot(reverse_edges,1,wide_weights,input.edges.size())==context.reverse);
    }else{assert(!failed&&context.phase==3);}
    for(unsigned phase=0;phase<context.phase;++phase){
        for(unsigned worker=0;worker<loaders;++worker){assert(context.started[phase][worker]&&context.finished[phase][worker]);}
    }
    current=nullptr;
    return context.selected.size();
}
int main(int argc,char** argv){
    assert(argc==2);
    std::ifstream stream(argv[1]);size_t count=0;stream>>count;assert(stream);
    size_t runs=0,active=0,eliminated=0,shared=0,cancellations=0;
    std::vector<Input> inputs;
    for(size_t test=0;test<count;++test){
        Input input;size_t m=0,q=0,workers=0;unsigned require_shared=0;
        stream>>input.name>>input.n>>input.k>>m>>q>>input.minimum>>input.maximum>>require_shared>>workers;input.shared=require_shared;
        input.ids.resize(input.k);input.workers.resize(workers);
        for(auto& id:input.ids){stream>>id;assert(id<input.n);}
        assert(std::set<uint32_t>(input.ids.begin(),input.ids.end()).size()==input.k);
        for(auto& worker:input.workers){stream>>worker;assert(worker>=1&&worker<=12);}
        for(size_t i=0;i<m;++i){uint32_t u=0,v=0,w=0;stream>>u>>v>>w;assert(u<input.k&&v<input.k);input.edges.emplace_back(u,v,w);}
        for(size_t i=0;i<q;++i){uint32_t u=0,v=0;stream>>u>>v;assert(u<input.k&&v<input.k);input.queries.emplace_back(u,v);}
        assert(stream);
        for(auto worker:input.workers){
            std::cout<<"CASE "<<input.name<<' '<<worker<<'\n'<<std::flush;
            size_t selected=execute(input,worker);++runs;active+=selected>0;eliminated+=selected;shared+=input.shared;
        }
        inputs.push_back(std::move(input));
    }
    for(unsigned worker=1;worker<=12;++worker){
        for(unsigned phase=1;phase<=2;++phase){execute(inputs.front(),worker,phase);++cancellations;}
    }
    assert(active>0&&eliminated>0&&shared>0);
    std::cout<<"PASS exact extracted bypass: "<<count<<" original-Floyd cases, "<<runs<<" topology runs, "<<active<<" active runs, "<<eliminated<<" eliminated vertices, "<<shared<<" shared-hub runs, "<<cancellations<<" injected collect/flag failures joined; all write/read sets, reverse multiplicities, untouched slots, all-survivor distances and0/MAX/wide fallbacks verified\n";
}
