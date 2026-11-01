                    struct Pending { uint32_t destination, weight, work_index; };
                    std::array<Pending,128> pending;
                    size_t pending_count=0;
                    auto flush=[&] {
                        size_t previous_index=work.size();bool active=false;
                        for(size_t j=0;j<pending_count;++j) {
                            const auto& edge=pending[j];
                            if(previous_index!=edge.work_index) {
                                previous_index=edge.work_index;
                                active=work[previous_index].first==own.get(work[previous_index].second);
                            }
                            if(!active)continue;
                            uint64_t candidate=work[edge.work_index].first+edge.weight;
                            if(own.improve(edge.destination,candidate)) {
                                heap.push({candidate,edge.destination});
                                uint64_t opposite=other.get(edge.destination);
                                if(opposite!=infinity)best=std::min(best,candidate+opposite);
                            }
                        }
                        pending_count=0;
                    };
                    for(size_t k=0;k<count;++k) {
                        for(uint32_t i=ranges[k].first;i<ranges[k].second;++i) {
                            auto [destination,tag]=adjacency.template get<Compact>(i);
                            uint32_t weight=tag==(Compact?EdgeStore::small_limit:uint32_t(UINT16_MAX))?wide_weights.at(i*2+(from_source?0:1)):tag;
                            own.prefetch(destination);other.prefetch(destination);
                            pending[pending_count++]={destination,weight,static_cast<uint32_t>(k)};
                            if(pending_count==pending.size())flush();
                        }
                    }
                    flush();
