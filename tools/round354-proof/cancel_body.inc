        auto cancel_pipeline=[&]{
            canceled.store(true,std::memory_order_release);
            for(size_t i=0;i<size_t(readers)*owners;++i)queues[i].cancel();
            for(unsigned i=0;i<owners;++i)wakes[i].signal();
        };
