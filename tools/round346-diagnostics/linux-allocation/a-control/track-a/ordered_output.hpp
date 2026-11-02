#pragma once
#include "io.hpp"
#include <array>
#include <mutex>
#include <type_traits>

// A producer publishes only its completed hour; the mutex orders all writes.
struct OrderedOutput {
    std::array<Output,72> hours;
    std::array<bool,72> ready{};size_t next=0;std::mutex mutex;std::ofstream stream;
    explicit OrderedOutput(const std::filesystem::path& path):stream(path,std::ios::binary){
        if(!stream)throw std::runtime_error("cannot open summary.txt");
    }
    void publish(size_t hour){
        std::lock_guard guard(mutex);ready[hour]=true;
        while(next<72&&ready[next]){
            auto& bytes=hours[next].bytes;stream.write(bytes.data(),static_cast<std::streamsize>(bytes.size()));
            if(!stream)throw std::runtime_error("cannot write summary.txt");
            std::remove_reference_t<decltype(bytes)>().swap(bytes);++next;
        }
    }
    void finish(){
        if(next!=72)throw std::runtime_error("incomplete summary.txt");
        stream.close();if(!stream)throw std::runtime_error("cannot write summary.txt");
    }
};
