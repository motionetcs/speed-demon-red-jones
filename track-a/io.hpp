#pragma once
#include <algorithm>
#include <charconv>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <stdexcept>
#include <string>
#include <string_view>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>

struct MappedFile {
    const char* data = "";
    size_t size = 0;
    explicit MappedFile(const std::filesystem::path& path) {
        int fd = open(path.c_str(), O_RDONLY);
        if (fd < 0) throw std::runtime_error("cannot open " + path.string());
        struct stat st{};
        if (fstat(fd, &st) != 0 || st.st_size < 0) {
            close(fd);
            throw std::runtime_error("cannot stat " + path.string());
        }
        size = static_cast<size_t>(st.st_size);
        if (size) {
            void* p = mmap(nullptr, size, PROT_READ, MAP_PRIVATE, fd, 0);
            close(fd);
            if (p == MAP_FAILED) throw std::runtime_error("cannot map " + path.string());
            data = static_cast<const char*>(p);
        } else close(fd);
    }
    MappedFile(const MappedFile&) = delete;
    MappedFile& operator=(const MappedFile&) = delete;
    ~MappedFile() { if (size) munmap(const_cast<char*>(data), size); }
};

struct Paths {
    std::filesystem::path data = "/data", out = "/out";
    Paths(int argc, char** argv) {
        for (int i = 1; i < argc; i += 2) {
            if (i + 1 == argc) throw std::runtime_error("missing option value");
            std::string_view option(argv[i]);
            if (option == "--data") data = argv[i + 1];
            else if (option == "--out") out = argv[i + 1];
            else throw std::runtime_error("unknown option");
        }
        std::filesystem::create_directories(out);
    }
};

inline uint64_t unsigned_number(std::string_view text) {
    uint64_t value = 0;
    auto result = std::from_chars(text.data(), text.data() + text.size(), value);
    if (result.ec != std::errc{} || result.ptr != text.data() + text.size())
        throw std::runtime_error("invalid unsigned number");
    return value;
}

struct Output {
    std::string bytes;
    void text(std::string_view s) { bytes.append(s); }
    void number(int64_t n) {
        char b[32];
        auto r = std::to_chars(b, b + sizeof b, n);
        bytes.append(b, r.ptr);
    }
};
