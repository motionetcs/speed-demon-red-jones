#include "io.hpp"
#include "parallel.hpp"
#include <array>
#include <atomic>
#include <iostream>
#include <sstream>
std::string render(const std::array<uint64_t,6>& values){
    Output out;
                    char numbers[128];char* number=numbers;
                    for (uint64_t value : values) {
                        *number++=' ';number=std::to_chars(number,numbers+sizeof numbers,static_cast<int64_t>(value)).ptr;
                    }
                    *number++='\n';out.text({numbers,static_cast<size_t>(number-numbers)});
    return std::string(out.bytes.data(),out.bytes.size());
}
int main(int argc,char**argv){
    if(argc!=3)return 2;
    std::ifstream input(argv[1]);if(!input)return 2;
    struct Case{std::array<uint64_t,6> values;std::string expected;};
    std::vector<Case> cases;std::string line;
    while(std::getline(input,line)){
        auto sep=line.find('|');if(sep==std::string::npos)return 2;
        std::istringstream in(line.substr(0,sep));Case c;
        for(auto& value:c.values)if(!(in>>value))return 2;
        c.expected=line.substr(sep+1)+"\n";cases.push_back(std::move(c));
    }
    std::atomic<size_t> next{0};unsigned threads=std::stoul(argv[2]);
    parallel(threads,[&](unsigned){for(;;){size_t i=next.fetch_add(1);if(i>=cases.size())return;if(render(cases[i].values)!=cases[i].expected)throw std::runtime_error("suffix mismatch");}});
    std::cout<<"PASS "<<cases.size()<<" "<<threads<<"\n";
}
