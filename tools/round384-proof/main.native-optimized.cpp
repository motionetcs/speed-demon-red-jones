#include "io.hpp"
#include "quote_scan.hpp"
#include "parallel.hpp"
#include <atomic>
#include "names.hpp"
#include <array>
#include <numeric>
#include <vector>

struct Field { std::string_view value; size_t bytes; bool escaped; };
struct Csv {
    const char* p;
    const char* end;
    void bom() {
        if (end - p >= 3 && std::memcmp(p, "\xef\xbb\xbf", 3) == 0) p += 3;
    }
    Field field(std::string& scratch, bool decode) {
        const char* start = p;
        if (p == end || *p != '"') {
            while (p < end && *p != ',' && *p != '\r' && *p != '\n') ++p;
            return {{start, static_cast<size_t>(p - start)}, static_cast<size_t>(p - start), false};
        }
        const char* segment = ++p;
        start = segment;
        size_t bytes = 0;
        bool escaped = false;
        while (p < end) {
            const char* quote = find_quote(p, end);
            if (!quote) throw std::runtime_error("unterminated quoted field");
            bytes += static_cast<size_t>(quote - segment);
            if (quote + 1 < end && quote[1] == '"') {
                if (decode) {
                    if (!escaped) scratch.assign(start, quote - start);
                    else scratch.append(segment, quote - segment);
                    scratch.push_back('"');
                }
                ++bytes;
                escaped = true;
                segment = p = quote + 2;
            } else {
                p = quote + 1;
                if (decode && escaped) scratch.append(segment, quote - segment);
                std::string_view value = escaped && decode ? std::string_view(scratch)
                    : std::string_view(start, static_cast<size_t>(quote - start));
                return {value, bytes, escaped};
            }
        }
        throw std::runtime_error("unterminated quoted field");
    }
    void comma() {
        if (p == end || *p++ != ',') throw std::runtime_error("expected CSV comma");
    }
    uint64_t integer() {
        const char* start = p;
        uint64_t value = 0;
        while (p < end && *p >= '0' && *p <= '9') value = value * 10 + *p++ - '0';
        if (p == start) throw std::runtime_error("missing CSV integer");
        comma();
        return value;
    }
    int64_t amount() {
        bool negative = p < end && *p == '-';
        if (negative) ++p;
        const char* start = p;
        uint64_t value = 0;
        while (p < end && *p >= '0' && *p <= '9') value = value * 10 + *p++ - '0';
        if (p == start || p == end || *p++ != '.' || end - p < 2 || p[0] < '0' || p[0] > '9' || p[1] < '0' || p[1] > '9')
            throw std::runtime_error("invalid money");
        value = value * 100 + (p[0] - '0') * 10 + p[1] - '0'; p += 2;
        return negative ? -static_cast<int64_t>(value) : static_cast<int64_t>(value);
    }
    void newline() {
        if (p == end) return; // The final record may omit its terminator.
        if (*p == '\r') ++p;
        if (p == end || *p++ != '\n') throw std::runtime_error("expected CSV terminator");
    }
};

// A singleton quote followed by comma, with a non-separator predecessor,
// cannot be an opening/escaped quote. It ends a quoted text field.
// Parse from that known field boundary to the next real record end.
std::vector<const char*> record_boundaries(const char* start,const char* end,unsigned threads) {
    std::vector<const char*> boundaries(threads+1);
    boundaries.front()=start;boundaries.back()=end;
    for(unsigned i=1;i<threads;++i){
        const char* p=start+(end-start)*i/threads;
        const char* boundary=end;
        while(p<end) {
            const char* quote=find_quote(p,end);if(!quote)break;p=quote+1;
            if(quote==start||quote+1==end||quote[1]!=',')continue;
            unsigned char before=static_cast<unsigned char>(quote[-1]);
            if(before=='"'||before==','||before=='\r'||before=='\n'||before==0xbf)continue;
            Csv tail{quote+2,end};std::string unused;
            for(;;){
                tail.field(unused,false);
                if(tail.p==end)break;
                if(*tail.p==','){tail.comma();continue;}
                tail.newline();break;
            }
            boundary=tail.p;break;
        }
        boundaries[i]=boundary;
    }
    return boundaries;
}

void money(Output& out, int64_t value) {
    if (value < 0) out.text("-");
    uint64_t n = value < 0 ? uint64_t(-(value + 1)) + 1 : uint64_t(value);
    out.number(static_cast<int64_t>(n / 100)); out.text(".");
    char digits[2] = {char('0' + n / 10 % 10), char('0' + n % 10)};
    out.text({digits, 2});
}
struct Group {
    std::string_view country;
    int64_t count = 0, ids = 0, sum = 0, minimum = INT64_MAX, maximum = INT64_MIN;
    int64_t names = 0, name_bytes = 0, note_bytes = 0;
};

int main(int argc, char** argv) {
    try {
        Paths paths(argc, argv);
        MappedFile region_file(paths.data / "regions.csv"), records(paths.data / "records.csv");
        Csv region_csv{region_file.data, region_file.data + region_file.size};
        std::string scratch;
        auto h1 = region_csv.field(scratch, false); region_csv.comma();
        auto h2 = region_csv.field(scratch, false); region_csv.newline();
        if (h1.value != "region_id" || h2.value != "country") throw std::runtime_error("bad regions header");
        constexpr uint16_t missing = UINT16_MAX;
        std::vector<uint16_t> country_index(26 * 26 * 26, missing);
        std::vector<Group> groups;
        std::vector<uint16_t> lookup(1000000, missing);
        while (region_csv.p < region_csv.end) {
            uint64_t id = region_csv.integer();
            if (region_csv.end - region_csv.p < 3) throw std::runtime_error("short country code");
            std::string_view country(region_csv.p, 3); region_csv.p += 3; region_csv.newline();
            uint32_t code = 0;
            for (unsigned char byte : country) {
                if (byte < 'A' || byte > 'Z') throw std::runtime_error("invalid country code");
                code = code * 26 + byte - 'A';
            }
            auto& dense = country_index[code];
            if (dense == missing) { dense = static_cast<uint16_t>(groups.size()); groups.push_back(Group{country}); }
            if (id >= lookup.size()) lookup.resize(id + 1, missing);
            lookup[id] = dense;
        }
        size_t unmatched = groups.size();
        groups.push_back(Group{"_UNMATCHED"});
        std::vector<uint8_t> narrow_lookup;
        if (unmatched <= UINT8_MAX) {
            narrow_lookup.assign(lookup.begin(), lookup.end());
            std::vector<uint16_t>().swap(lookup);
        }
        Csv header{records.data, records.data + records.size};
        header.bom();
        for (auto expected : {"id", "name", "note", "region_id", "amount"}) {
            if (header.field(scratch, true).value != expected) throw std::runtime_error("bad records header");
            if (std::string_view(expected) != "amount") header.comma(); else header.newline();
        }
        unsigned threads = worker_count();
#ifndef PIPELINE_READERS
#define PIPELINE_READERS 8
#endif
#ifndef NAME_BATCH
#define NAME_BATCH 512
#endif
        unsigned readers=threads==1?1:std::clamp(threads*PIPELINE_READERS/12,1U,threads-1);
        unsigned owners=threads-readers;
        auto boundaries=record_boundaries(header.p,records.data+records.size,readers);
        struct Local{std::vector<Group> groups;};
        std::vector<Local> locals(readers);for(auto& local:locals)local.groups=groups;
        std::vector<std::vector<uint64_t>> distinct(owners,std::vector<uint64_t>(groups.size()));
        auto queues=std::make_unique<NameQueue[]>(size_t(readers)*owners);
        std::atomic<bool> canceled{false};
        auto consume=[&]<size_t FixedWords,typename Code>(const std::vector<Code>& region_lookup){
            constexpr Code no_region=std::numeric_limits<Code>::max();
            parallel(threads,[&](unsigned worker){
                try{
                    if(worker<readers){
                        auto& local=locals[worker];std::unique_ptr<Names> serial;
                        if(!owners)serial=std::make_unique<Names>(groups.size());
                        std::vector<std::vector<NameEvent>> batches(owners);
                        for(auto& batch:batches)batch.reserve(NAME_BATCH);
                        Csv csv{boundaries[worker],boundaries[worker+1]};std::string name_scratch,unused;
                        while(csv.p<csv.end){
                            if(canceled.load(std::memory_order_relaxed))throw std::runtime_error("name pipeline canceled");
                            csv.bom();uint64_t id=csv.integer();Field name=csv.field(name_scratch,false);csv.comma();
                            uint64_t hash=Names::hash_key(name.value);
                            Field note=csv.field(unused,false);csv.comma();uint64_t region=csv.integer();int64_t amount=csv.amount();csv.newline();
                            size_t country=region<region_lookup.size()&&region_lookup[region]!=no_region?region_lookup[region]:unmatched;
                            Group& group=local.groups[country];++group.count;group.ids+=static_cast<int64_t>(id);group.sum+=amount;
                            group.minimum=std::min(group.minimum,amount);group.maximum=std::max(group.maximum,amount);
                            group.name_bytes+=name.bytes;group.note_bytes+=note.bytes;
                            if(!owners){group.names+=serial->first<FixedWords>(name.value,country,hash);continue;}
                            unsigned owner=hash%owners;NameEvent event{name.value,hash,static_cast<uint16_t>(country)};
                            auto& batch=batches[owner];batch.push_back(std::move(event));
                            if(batch.size()==NAME_BATCH)queues[size_t(worker)*owners+owner].send(batch,canceled);
                        }
                        // An empty published batch is the ordered end-of-stream marker.
                        for(unsigned owner=0;owner<owners;++owner){auto& batch=batches[owner];auto& queue=queues[size_t(worker)*owners+owner];if(!batch.empty())queue.send(batch,canceled);queue.send(batch,canceled);}
                    }else{
                        unsigned owner=worker-readers;Names names(groups.size());std::array<bool,12> finished{};unsigned remaining=readers;
                        while(remaining){
                            if(canceled.load(std::memory_order_relaxed))throw std::runtime_error("name pipeline canceled");
                            bool progress=false;
                            for(unsigned reader=0;reader<readers;++reader){
                                if(finished[reader])continue;auto& queue=queues[size_t(reader)*owners+owner];
                                if(!queue.ready.load(std::memory_order_acquire))continue;progress=true;
                                if(queue.rows.empty()){finished[reader]=true;--remaining;}
                                else for(const auto& e:queue.rows)distinct[owner][e.country]+=names.first<FixedWords>(e.value(),e.country,e.hash);
                                queue.rows.clear();queue.ready.store(false,std::memory_order_release);
                            }
                            if(!progress)std::this_thread::yield();
                        }
                    }
                }catch(...){canceled.store(true,std::memory_order_relaxed);throw;}
            });
        };
        auto dispatch=[&]<typename Code>(const std::vector<Code>& values){
            if((groups.size()+63)/64==4)consume.template operator()<4>(values);
            else consume.template operator()<0>(values);
        };
        if(narrow_lookup.empty())dispatch(lookup);else dispatch(narrow_lookup);
        for(const auto& local:locals)for(size_t i=0;i<groups.size();++i){auto& group=groups[i];const auto& value=local.groups[i];group.count+=value.count;group.ids+=value.ids;group.sum+=value.sum;group.minimum=std::min(group.minimum,value.minimum);group.maximum=std::max(group.maximum,value.maximum);group.names+=value.names;group.name_bytes+=value.name_bytes;group.note_bytes+=value.note_bytes;}
        for(const auto& owner:distinct)for(size_t i=0;i<groups.size();++i)groups[i].names+=owner[i];
        std::sort(groups.begin(), groups.end(), [](const Group& a, const Group& b) { return a.country < b.country; });
        Output output;
        for (const Group& group : groups) if (group.count) {
            output.text(group.country); output.text(" "); output.number(group.count);
            output.text(" "); output.number(group.ids);
            for (int64_t value : {group.sum, group.minimum, group.maximum}) { output.text(" "); money(output, value); }
            for (int64_t value : {group.names, group.name_bytes, group.note_bytes}) { output.text(" "); output.number(value); }
            output.text("\n");
        }
        output.save(paths.out / "aggregates.txt");
    } catch (const std::exception& e) {
        std::fprintf(stderr, "track-c: %s\n", e.what());
        return 1;
    }
}
