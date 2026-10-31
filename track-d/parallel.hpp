#pragma once
#include <array>
#include <cstdlib>
#include <exception>
#include <thread>
#include <vector>

template<class Function> void parallel(unsigned count, Function function) {
    std::array<std::exception_ptr, 12> errors;
    auto run = [&](unsigned i) {
        try { function(i); } catch (...) { errors[i] = std::current_exception(); }
    };
    std::vector<std::jthread> workers;
    for (unsigned i = 1; i < count; ++i) workers.emplace_back(run, i);
    run(0);
    workers.clear();
    for (unsigned i = 0; i < count; ++i) if (errors[i]) std::rethrow_exception(errors[i]);
}
