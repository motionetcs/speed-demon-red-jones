// The model wrapper contains the exact production Field/Csv class token bytes.
#include CSV_MODEL_HEADER
#include <cassert>
#include <charconv>
#include <iostream>
#include <random>
#include <sys/mman.h>
#include <unistd.h>

static size_t checks = 0;
static void amount(const char* first, const char* last, int64_t expected) {
    Csv csv{first,last};
    assert(csv.amount()==expected);
    csv.newline();
    assert(csv.p==last);
    ++checks;
}
static void amount(const std::string& value, int64_t expected) {
    amount(value.data(),value.data()+value.size(),expected);
}
static void rejected(const std::string& value) {
    Csv csv{value.data(),value.data()+value.size()};
    bool failed=false;
    try { csv.amount(); csv.newline(); } catch(const std::runtime_error&) { failed=true; }
    assert(failed); ++checks;
}
static std::string money_text(uint64_t cents, bool negative) {
    auto result=std::to_string(cents/100)+".";
    result.push_back(char('0'+cents/10%10));result.push_back(char('0'+cents%10));
    return negative?"-"+result:result;
}
int main() {
    std::mt19937_64 rng(0xa23d74cc1159ULL);
    // from_chars is an independent numeric oracle; integers remain unchanged.
    for(unsigned i=0;i<100000;++i){
        auto value=rng();auto text=std::to_string(value);uint64_t reference=0;
        auto parsed=std::from_chars(text.data(),text.data()+text.size(),reference);
        assert(parsed.ec==std::errc{}&&parsed.ptr==text.data()+text.size());
        text+=',';Csv csv{text.data(),text.data()+text.size()};
        assert(csv.integer()==reference&&csv.p==csv.end);++checks;
        // Every generated monetary value is inside the frozen generator range.
        int64_t cents=int64_t(rng()%10100000)-99999;
        auto absolute=cents<0?uint64_t(-cents):uint64_t(cents);
        auto field=money_text(absolute,cents<0);
        amount(field,cents);amount(field+"\n",cents);amount(field+"\r\n",cents);
    }
    // Broader, defined signed-cent boundaries; no overflow acceptance is claimed.
    for(uint64_t cents:{uint64_t(0),uint64_t(1),uint64_t(99),uint64_t(100),
            uint64_t(99999),uint64_t(9999999),uint64_t(INT64_MAX)}){
        for(bool negative:{false,true}){
            auto text=money_text(cents,negative);int64_t expected=negative?-int64_t(cents):int64_t(cents);
            for(unsigned zeros=0;zeros<=24;++zeros){
                auto padded=text;padded.insert(negative?1:0,zeros,'0');
                amount(padded,expected);amount(padded+"\n",expected);amount(padded+"\r\n",expected);
            }
        }
    }
    for(unsigned byte=0;byte<256;++byte){
        auto text=std::string("1.")+char(byte)+"0";
        if(byte>='0'&&byte<='9')amount(text,100+int64_t(byte-'0')*10);else rejected(text);
        text=std::string(1,char(byte))+".00";
        if(byte>='0'&&byte<='9')amount(text,int64_t(byte-'0')*100);else rejected(text);
    }
    for(const auto& text:std::vector<std::string>{"","-",".00","-.00","+1.00","1","1.","1.0","1.000","1.00x","1.00\r","1.0a","1.a0"})rejected(text);
    for(const auto& text:std::vector<std::string>{"0.00","-0.00","99999.99","-999.99","12345678.12"}){
        for(size_t n=0;n<text.size();++n)rejected(text.substr(0,n));
    }
    size_t page=size_t(sysconf(_SC_PAGESIZE));
    char* memory=static_cast<char*>(mmap(nullptr,3*page,PROT_NONE,MAP_PRIVATE|MAP_ANON,-1,0));
    assert(memory!=MAP_FAILED&&mprotect(memory+page,page,PROT_READ|PROT_WRITE)==0);
    for(uint64_t cents:{uint64_t(0),uint64_t(99),uint64_t(9999999),uint64_t(INT64_MAX)}){
        for(bool negative:{false,true})for(unsigned zeros=0;zeros<=24;++zeros){
            auto text=money_text(cents,negative);text.insert(negative?1:0,zeros,'0');
            int64_t expected=negative?-int64_t(cents):int64_t(cents);
            for(const auto& suffix:std::vector<std::string>{"","\n","\r\n"}){
                auto field=text+suffix;
                for(char* destination:{memory+page,memory+2*page-field.size()}){
                    std::memcpy(destination,field.data(),field.size());
                    amount(destination,destination+field.size(),expected);
                }
            }
        }
    }
    assert(munmap(memory,3*page)==0);
    std::cout<<"PASS production CSV numeric independent integer/cents/error/guard model "<<checks<<" checks\n";
}
