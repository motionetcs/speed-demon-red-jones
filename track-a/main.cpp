#include "io.hpp"
#include "decimal.hpp"
#include "parallel.hpp"
#include "aggregate.hpp"
#include <numeric>

struct Header {unsigned hour;std::string_view endpoint,label;bool error;};
Header read_header(const char*& p,const char* end) {
    const char* record=p;
    if(end-p<28)throw std::runtime_error("truncated timestamp");
    int month=(p[5]-'0')*10+p[6]-'0',day=(p[8]-'0')*10+p[9]-'0';
    int hour=(month==10 ? day-30:day+1)*24+(p[11]-'0')*10+p[12]-'0'-18;
    if(hour<0 || hour>=72)throw std::runtime_error("hour outside specification");
    p+=28;while(p<end && *p!=' ')++p;
    if(p==end)throw std::runtime_error("missing endpoint");
    const char* start=++p;p=static_cast<const char*>(std::memchr(start,' ',end-start));
    if(!p || end-p<5)throw std::runtime_error("missing endpoint/status");
    Header result{static_cast<unsigned>(hour),{start,static_cast<size_t>(p-start)},{record,13},p[1]=='5'};
    p+=5;return result;
}
struct Group {uint32_t count,errors,begin;};

int main(int argc,char** argv) {
    try {
        Paths paths(argc,argv);MappedFile file(paths.data/"requests.log");
        if(!file.size){Output{}.save(paths.out/"summary.txt");return 0;}
        unsigned threads=worker_count();const char* end=file.data+file.size;
        std::vector<const char*> boundaries(threads+1);boundaries.front()=file.data;boundaries.back()=end;
        for(unsigned i=1;i<threads;++i){const char* p=file.data+file.size*i/threads;
            if(p>file.data && p[-1]!='\n'){const char* newline=static_cast<const char*>(std::memchr(p,'\n',end-p));p=newline ? newline+1:end;}boundaries[i]=p;
        }
        for(size_t capacity=2048;;capacity*=2) {
            Endpoints endpoints(capacity);size_t group_count=72*capacity;
            std::vector<CountChunk> chunks;chunks.reserve(threads);for(unsigned w=0;w<threads;++w)chunks.emplace_back(group_count);
            parallel(threads,[&](unsigned w){try{
                auto& local=chunks[w];const char* p=boundaries[w];const char* limit=boundaries[w+1];
                while(p<limit){Header h=read_header(p,limit);uint64_t hash=Endpoints::hash_key(h.endpoint);endpoints.prefetch(hash);
                    const char* newline=static_cast<const char*>(std::memchr(p,'\n',limit-p));if(!newline)throw std::runtime_error("missing latency newline");p=newline+1;
                    uint32_t id=endpoints.intern(h.endpoint,hash);local.add(h.hour*capacity+id,h.error);if(local.labels[h.hour].empty())local.labels[h.hour]=h.label;
                }
            }catch(const RetryEndpoints&){return;}catch(...){endpoints.canceled.store(true);throw;}});
            if(endpoints.too_small.load())continue;
            std::array<std::string,72> labels;
            for(unsigned h=0;h<72;++h)for(const auto& chunk:chunks)if(!chunk.labels[h].empty()){labels[h]=std::string(chunk.labels[h])+":00:00Z";break;}
            std::vector<Group> groups(group_count);uint64_t prefix=0;
            for(size_t g=0;g<group_count;++g){std::array<uint64_t,12> counts{};uint64_t count=0,errors=0;
                for(unsigned w=0;w<threads;++w){WideCounts value=chunks[w].total(g);counts[w]=value.count;count+=value.count;errors+=value.errors;}
                if(count>UINT32_MAX-prefix || errors>count)throw std::runtime_error("request count exceeds uint32 capacity");
                groups[g]={static_cast<uint32_t>(count),static_cast<uint32_t>(errors),static_cast<uint32_t>(prefix)};
                for(unsigned w=0;w<threads;++w){chunks[w].cells[g].cursor=static_cast<uint32_t>(prefix);prefix+=counts[w];}
            }
            std::unique_ptr<uint32_t[]> latencies(new uint32_t[prefix]);
            parallel(threads,[&](unsigned w){auto& local=chunks[w];const char* p=boundaries[w];const char* limit=boundaries[w+1];
                while(p<limit){Header h=read_header(p,limit);uint64_t hash=Endpoints::hash_key(h.endpoint);uint32_t id=endpoints.lookup(h.endpoint,hash);
                    const char* start=p;uint64_t value=decimal_digits(p,limit);
                    if(p==start || p-start>10 || value>UINT32_MAX || p==limit || *p!='\n')throw std::runtime_error("invalid latency line");++p;
                    latencies[local.cells[h.hour*capacity+id].cursor++]=static_cast<uint32_t>(value);
                }
            });
            chunks.clear();std::vector<uint32_t> order(endpoints.used.load());std::iota(order.begin(),order.end(),0);
            std::sort(order.begin(),order.end(),[&](auto a,auto b){return endpoints.paths[a]<endpoints.paths[b];});
            std::ofstream stream(paths.out/"summary.txt",std::ios::binary);if(!stream)throw std::runtime_error("cannot open summary.txt");
            std::atomic<unsigned> next_hour{0};std::atomic<bool> failed{false};
            //0 waits,1 permits writing,2 cancels. A normal handoff never overwrites cancellation.
            std::array<std::atomic<unsigned>,72> ready{};ready[0].store(1,std::memory_order_relaxed);
            parallel(threads,[&](unsigned){try{
                Output out;out.bytes.reserve(order.size()*112);
                for(;;){if(failed.load(std::memory_order_relaxed))return;unsigned hour=next_hour.fetch_add(1,std::memory_order_relaxed);if(hour>=72)return;out.bytes.clear();
                    for(uint32_t id:order){Group group=groups[hour*capacity+id];uint64_t n=group.count,errors=group.errors;if(!n)continue;uint32_t* first=latencies.get()+group.begin;
                        if(n<64)std::sort(first,first+n);else{size_t unselected=0;for(uint64_t percentile:{50,95,99}){size_t rank=(percentile*n+99)/100-1;if(rank>=unselected){std::nth_element(first+unselected,first+rank,first+n);unselected=rank+1;}}}
                        out.text(labels[hour]);out.text(" ");out.text(endpoints.paths[id]);
                        for(uint64_t value:{n,uint64_t(first[(50*n+99)/100-1]),uint64_t(first[(95*n+99)/100-1]),uint64_t(first[(99*n+99)/100-1]),errors,errors*1000000/n}){out.text(" ");out.number(static_cast<int64_t>(value));}out.text("\n");
                    }
                    unsigned state=ready[hour].load(std::memory_order_acquire);while(state==0){ready[hour].wait(0,std::memory_order_relaxed);state=ready[hour].load(std::memory_order_acquire);}if(state==2)return;
                    if(!out.bytes.empty())stream.write(out.bytes.data(),static_cast<std::streamsize>(out.bytes.size()));if(!stream)throw std::runtime_error("cannot write summary.txt");
                    if(hour+1<72){unsigned expected=0;ready[hour+1].compare_exchange_strong(expected,1,std::memory_order_release,std::memory_order_relaxed);ready[hour+1].notify_one();}
                }
            }catch(...){failed.store(true);for(auto& flag:ready){flag.store(2,std::memory_order_release);flag.notify_one();}throw;}});
            stream.close();if(!stream)throw std::runtime_error("cannot close summary.txt");return 0;
        }
    }catch(const std::exception& error){std::fprintf(stderr,"track-a: %s\n",error.what());return 1;}
}
