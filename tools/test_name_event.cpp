#ifdef NAMES_HEADER
#include NAMES_HEADER
#else
#include "../track-c/names.hpp"
#endif
#include <cassert>
#include <iostream>
#include <random>
#include <string>
#include <vector>

int main() {
#ifdef REQUIRE_PACKED_EVENT
    static_assert(sizeof(NameEvent) == 24);
#endif
    std::mt19937_64 random(0x9f760c1);
    std::string input(1048577, '\0');
    for (char& byte : input) byte = static_cast<char>(random());
    for (size_t length : {0U, 1U, 7U, 8U, 15U, 16U, 65535U, 65536U, 65537U, 1048576U}) {
        std::string_view key(input.data() + 1, length);
        for (uint16_t country : {uint16_t(0), uint16_t(63), uint16_t(64), uint16_t(255), uint16_t(256), uint16_t(17576), uint16_t(UINT16_MAX)}) {
            uint64_t hash = random();
            NameEvent event{key, hash, country};
            assert(event.value().data() == key.data() && event.value() == key);
            assert(event.hash == hash && event.country == country);
        }
    }
    std::vector<NameEvent> events;
    for (uint32_t country = 0; country <= UINT16_MAX; ++country) {
        size_t length = random() % input.size();
        uint64_t hash = random();
        events.emplace_back(std::string_view(input.data(), length), hash, static_cast<uint16_t>(country));
        const auto& event = events.back();
        assert(event.value().data() == input.data() && event.value().size() == length);
        assert(event.hash == hash && event.country == country);
    }
    std::vector<NameEvent> copied = events;
    for (size_t i = 0; i < copied.size(); ++i) {
        assert(copied[i].country == i && copied[i].hash == events[i].hash);
        assert(copied[i].value().data() == input.data());
        assert(copied[i].value().size() == events[i].value().size());
    }
    std::cout << "PASS" << sizeof(NameEvent) << "-byte name event: every16-bit country, random full64-bit hashes, stable binary keys through1MiB, length/copy/growth boundaries\n";
}
