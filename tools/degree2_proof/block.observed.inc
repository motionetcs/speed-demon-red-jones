        // Select nonadjacent reciprocal degree-two vertices from the actual graph.
        // Collect against immutable CSR, then apply disjoint exact bypass slots.
        std::vector<uint8_t> protected_node(n,0);
        for(auto [source,target]:queries){protected_node[source]=1;protected_node[target]=1;}
        // Immutable flags distinguish vertices eligible for this optimization
        // from pinned or non-degree-two neighbours before selecting local maxima.
        parallel(loaders,[&](unsigned worker){
            uint32_t begin=uint64_t(n)*worker/loaders,end=uint64_t(n)*(worker+1)/loaders;
            for(uint32_t node=begin;node<end;++node)if(!protected_node[node]&&offsets[node+1]-offsets[node]==2&&reverse_offsets[node+1]-reverse_offsets[node]==2)protected_node[node]=2;
        });
        struct Shortcut {uint32_t node,iu,iv,ru,rv;};
        std::vector<std::vector<Shortcut>> shortcuts(loaders);
        parallel(loaders,[&](unsigned worker){
            uint32_t begin=uint64_t(n)*worker/loaders,end=uint64_t(n)*(worker+1)/loaders;
            auto& plans=shortcuts[worker];
            for(uint32_t node=begin;node<end;++node){
                if(protected_node[node]!=2)continue;
                auto [u,a]=edges.get(offsets[node]);auto [v,b]=edges.get(offsets[node]+1);
                if(u==v||u==node||v==node||(protected_node[u]==2&&u>node)||(protected_node[v]==2&&v>node))continue;
                auto [x,c]=reverse_edges.get(reverse_offsets[node]);auto [y,d]=reverse_edges.get(reverse_offsets[node]+1);
                if(x!=u){std::swap(x,y);std::swap(c,d);}
                if(x!=u||y!=v)continue;
                uint32_t limit=edges.weight_limit;
                if(a>=limit||b>=limit||c>=limit||d>=limit||uint64_t(c)+b>=limit||uint64_t(d)+a>=limit)continue;
                if(offsets[u+1]-offsets[u]>64||offsets[v+1]-offsets[v]>64||reverse_offsets[u+1]-reverse_offsets[u]>64||reverse_offsets[v+1]-reverse_offsets[v]>64)continue;
                auto incoming_slot=[&](const auto& starts,const EdgeStore& store,uint32_t from){
                    uint32_t found=UINT32_MAX;unsigned count=0;
                    for(uint32_t i=starts[from];i<starts[from+1];++i)if(store.get(i).first==node){found=i;++count;}
                    return count==1?found:UINT32_MAX;
                };
                uint32_t iu=incoming_slot(offsets,edges,u),iv=incoming_slot(offsets,edges,v);
                uint32_t ru=incoming_slot(reverse_offsets,reverse_edges,u),rv=incoming_slot(reverse_offsets,reverse_edges,v);
                if(iu!=UINT32_MAX&&iv!=UINT32_MAX&&ru!=UINT32_MAX&&rv!=UINT32_MAX)plans.push_back({node,iu,iv,ru,rv});
            }
        });
        audit_plans(shortcuts,protected_node,queries,offsets,reverse_offsets,edges,reverse_edges,wide_weights);
        parallel(loaders,[&](unsigned worker){
            for(auto plan:shortcuts[worker]){
                auto [u,a]=edges.get(offsets[plan.node]);auto [v,b]=edges.get(offsets[plan.node]+1);
                auto first=reverse_edges.get(reverse_offsets[plan.node]);auto second=reverse_edges.get(reverse_offsets[plan.node]+1);
                uint32_t c=first.first==u?first.second:second.second,d=first.first==v?first.second:second.second;
                edges.set(plan.iu,v,c+b);reverse_edges.set(plan.rv,u,c+b);
                edges.set(plan.iv,u,d+a);reverse_edges.set(plan.ru,v,d+a);
            }
        });
        audit_result(offsets,reverse_offsets,edges,reverse_edges,wide_weights);
        shortcuts.clear();shortcuts.shrink_to_fit();protected_node.clear();protected_node.shrink_to_fit();
