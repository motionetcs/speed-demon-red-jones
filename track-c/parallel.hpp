#pragma once
#include <array>
#include <cstdlib>
#include <exception>
#include <thread>
#include <vector>

inline unsigned worker_count() {
    if (const char* text = std::getenv("SPEED_DEMON_THREADS")) {
        auto n = unsigned_number(text);
        if (n < 1 || n > 12) throw std::runtime_error("threads must be 1 to 12");
        return static_cast<unsigned>(n);
    }
    return 12;
}

template<class Function,class Cancel> void parallel(unsigned count, Function function,Cancel cancel) {
    static_assert(noexcept(cancel()),"parallel cancellation must not throw");
    std::array<std::exception_ptr, 12> errors;
    auto run = [&](unsigned i) {
        try { function(i); } catch (...) { errors[i] = std::current_exception(); }
    };
    std::vector<std::jthread> workers;
    try { for (unsigned i = 1; i < count; ++i) workers.emplace_back(run, i); }
    catch (...) { cancel(); throw; }
    run(0);
    workers.clear();
    for (unsigned i = 0; i < count; ++i) if (errors[i]) std::rethrow_exception(errors[i]);
}
