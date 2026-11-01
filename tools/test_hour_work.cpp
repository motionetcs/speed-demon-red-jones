#include HOUR_WORK_HEADER
#include ORDERED_OUTPUT_HEADER
#include <algorithm>
#include <atomic>
#include <cassert>
#include <chrono>
#include <climits>
#include <condition_variable>
#include <fstream>
#include <iostream>
#include <iterator>
#include <thread>
#include <vector>

// Exercise the actual semaphore and writer as one protocol. The independent
// oracle is byte concatenation, and each hour must have exactly one owner.
void complete(const std::filesystem::path& path,unsigned workers,unsigned pattern) {
    HourWorkWindow work(workers);OrderedOutput writer(path);
    std::array<std::string,72> expected;
    for(unsigned h=0;h<72;++h) {
        size_t n=(h%7==0)?0:(h+1)*193;
        if(pattern==2&&h==0)n=1048576;
        expected[h].resize(n);
        for(size_t k=0;k<n;++k)expected[h][k]=char((k+h)%251);
    }
    std::array<std::atomic<unsigned>,72> seen{};
    std::atomic<unsigned> retired{0},flushed_total{0},high_water{0};
    std::mutex gate;std::condition_variable cv;unsigned later=0;
    std::vector<std::thread> threads;
    for(unsigned w=0;w<workers;++w)threads.emplace_back([&]{
        try {
            for(;;) {
                unsigned h=work.claim();
                if(h>=72){++retired;return;}
                assert(seen[h].fetch_add(1)==0);
                {
                    std::lock_guard lock(writer.mutex);
                    unsigned pending=std::min(work.next.load(),72U)-unsigned(writer.next);
                    assert(pending<=workers);
                    unsigned previous=high_water.load();
                    while(previous<pending&&!high_water.compare_exchange_weak(previous,pending)){}
                }
                if(pattern&&h==0&&workers>1) {
                    std::unique_lock lock(gate);
                    assert(cv.wait_for(lock,std::chrono::seconds(10),[&]{return later==workers-1;}));
                }
                writer.hours[h].bytes.append(expected[h].data(),expected[h].size());
                if((h+pattern)%3==0)std::this_thread::yield();
                size_t flushed=writer.publish(h);
                flushed_total.fetch_add(unsigned(flushed));
                if(pattern&&h>0&&h<workers) {
                    std::lock_guard lock(gate);++later;cv.notify_all();
                }
                work.completed(flushed);
            }
        } catch(...) {work.cancel();throw;}
    });
    for(auto& thread:threads)thread.join();
    writer.finish();assert(!work.canceled.load());assert(retired==workers);
    assert(work.next==72+workers&&flushed_total==72&&high_water<=workers);
    if(pattern&&workers>1)assert(high_water==workers);
    for(auto& value:seen)assert(value==1);
    for(const auto& hour:writer.hours)assert(hour.bytes.empty());
    std::ifstream input(path,std::ios::binary);
    std::string actual((std::istreambuf_iterator<char>(input)),{}),joined;
    for(const auto& hour:expected)joined+=hour;
    assert(actual==joined);
}

void abort_waiters(const std::filesystem::path& path,unsigned workers) {
    HourWorkWindow work(workers);OrderedOutput writer(path);
    std::atomic<unsigned> catches{0};std::mutex gate;std::condition_variable cv;unsigned later=0;
    std::vector<std::thread> threads;
    for(unsigned w=0;w<workers;++w)threads.emplace_back([&]{
        try {
            for(;;) {
                unsigned h=work.claim();assert(h<workers);
                if(h==0) {
                    std::unique_lock lock(gate);
                    assert(cv.wait_for(lock,std::chrono::seconds(10),[&]{return later==workers-1;}));
                    work.cancel();throw std::runtime_error("injected first-hour failure");
                }
                writer.hours[h].text("ready");work.completed(writer.publish(h));
                {std::lock_guard lock(gate);++later;cv.notify_all();}
            }
        }catch(const std::runtime_error&){++catches;work.cancel();}
    });
    for(auto& thread:threads)thread.join();
    assert(catches==workers&&work.canceled&&work.next==workers&&writer.next==0);
    bool failed=false;try{writer.finish();}catch(const std::runtime_error&){failed=true;}assert(failed);
}

void canceled_before_claim(unsigned workers) {
    HourWorkWindow work(workers);work.cancel();std::atomic<unsigned> catches{0};
    std::vector<std::thread> threads;
    for(unsigned w=0;w<workers;++w)threads.emplace_back([&]{
        work.cancel();
        try{(void)work.claim();assert(false);}catch(const std::runtime_error&){++catches;}
    });
    for(auto& thread:threads)thread.join();
    assert(catches==workers&&work.next==0);
}

#ifdef __linux__
void sink_failure(unsigned workers) {
    HourWorkWindow work(workers);OrderedOutput writer("/dev/full");std::atomic<unsigned> failures{0};
    std::vector<std::thread> threads;
    for(unsigned w=0;w<workers;++w)threads.emplace_back([&]{
        try {
            for(;;){unsigned h=work.claim();if(h>=72)return;writer.hours[h].bytes.append(32768,'x');work.completed(writer.publish(h));}
        }catch(const std::runtime_error&){++failures;work.cancel();}
    });
    for(auto& thread:threads)thread.join();
    assert(failures>0&&work.canceled);
}
#endif

int main(int argc,char** argv) {
    assert(argc==2);std::filesystem::path root=argv[1];std::filesystem::create_directories(root);
    for(unsigned invalid:{0U,13U,128U,UINT_MAX}) {
        bool failed=false;try{HourWorkWindow work(invalid);}catch(const std::runtime_error&){failed=true;}assert(failed);
    }
    for(unsigned workers=1;workers<=12;++workers) {
        for(unsigned pattern=0;pattern<3;++pattern)complete(root/(std::to_string(workers)+"-"+std::to_string(pattern)),workers,pattern);
        abort_waiters(root/("abort-"+std::to_string(workers)),workers);canceled_before_claim(workers);
#ifdef __linux__
        sink_failure(workers);
#endif
    }
    std::cout<<"PASS exact hour credit/prefix publication/one owner/bounded lag/empty/NUL/retirement/cancel-wakeup and sink protocol all1..12 workers\n";
}
