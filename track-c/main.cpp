#include "io.hpp"
#include <array>
#include <deque>
#include <numeric>
#include <unordered_map>
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
            const char* quote = static_cast<const char*>(std::memchr(p, '"', end - p));
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
    void newline() {
        if (p == end) return; // The final record may omit its terminator.
        if (*p == '\r') ++p;
        if (p == end || *p++ != '\n') throw std::runtime_error("expected CSV terminator");
    }
};

int64_t cents(std::string_view value) {
    bool negative = !value.empty() && value.front() == '-';
    if (negative) value.remove_prefix(1);
    size_t dot = value.find('.');
    if (dot == std::string_view::npos || value.size() - dot != 3)
        throw std::runtime_error("invalid money");
    uint64_t result = unsigned_number(value.substr(0, dot)) * 100 + unsigned_number(value.substr(dot + 1));
    return negative ? -static_cast<int64_t>(result) : static_cast<int64_t>(result);
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
        std::unordered_map<std::string_view, uint16_t> countries;
        std::vector<Group> groups;
        constexpr uint16_t missing = UINT16_MAX;
        std::vector<uint16_t> lookup(1000000, missing);
        while (region_csv.p < region_csv.end) {
            uint64_t id = unsigned_number(region_csv.field(scratch, false).value); region_csv.comma();
            auto country = region_csv.field(scratch, false).value; region_csv.newline();
            auto [it, added] = countries.try_emplace(country, static_cast<uint16_t>(groups.size()));
            if (added) groups.push_back(Group{country});
            if (id >= lookup.size()) lookup.resize(id + 1, missing);
            lookup[id] = it->second;
        }
        size_t unmatched = groups.size();
        groups.push_back(Group{"_UNMATCHED"});
        size_t words = (groups.size() + 63) / 64;
        std::unordered_map<std::string_view, uint32_t> names;
        names.reserve(120000);
        std::deque<std::string> decoded_names;
        std::vector<uint64_t> membership;
        Csv csv{records.data, records.data + records.size};
        csv.bom();
        for (auto expected : {"id", "name", "note", "region_id", "amount"}) {
            if (csv.field(scratch, true).value != expected) throw std::runtime_error("bad records header");
            if (std::string_view(expected) != "amount") csv.comma(); else csv.newline();
        }
        std::string name_scratch, unused;
        while (csv.p < csv.end) {
            csv.bom();
            uint64_t id = unsigned_number(csv.field(unused, false).value); csv.comma();
            Field name = csv.field(name_scratch, true); csv.comma();
            Field note = csv.field(unused, false); csv.comma();
            uint64_t region = unsigned_number(csv.field(unused, false).value); csv.comma();
            int64_t amount = cents(csv.field(unused, false).value); csv.newline();
            size_t country = region < lookup.size() && lookup[region] != missing ? lookup[region] : unmatched;
            auto it = names.find(name.value);
            if (it == names.end()) {
                std::string_view stable = name.value;
                if (name.escaped) { decoded_names.emplace_back(name.value); stable = decoded_names.back(); }
                it = names.emplace(stable, static_cast<uint32_t>(names.size())).first;
                membership.resize(membership.size() + words, 0);
            }
            // Exact country membership per interned name replaces millions of set nodes.
            uint64_t& word = membership[size_t(it->second) * words + country / 64];
            uint64_t bit = uint64_t(1) << (country % 64);
            Group& group = groups[country];
            group.names += (word & bit) == 0; word |= bit;
            ++group.count; group.ids += static_cast<int64_t>(id); group.sum += amount;
            group.minimum = std::min(group.minimum, amount); group.maximum = std::max(group.maximum, amount);
            group.name_bytes += name.bytes; group.note_bytes += note.bytes;
        }
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
