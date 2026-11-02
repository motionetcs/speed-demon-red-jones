extern "C" void write_low(const void* p){__builtin_prefetch(p,1,1);}
extern "C" void write_high(const void* p){__builtin_prefetch(p,1,3);}
extern "C" void read_low(const void* p){__builtin_prefetch(p,0,1);}
extern "C" void read_high(const void* p){__builtin_prefetch(p,0,3);}
