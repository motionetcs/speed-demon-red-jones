#include <algorithm>
#include <cassert>
#include <iostream>
#include <random>
#include "track-d/load_cursors.hpp"
int main() {
 std::mt19937 rng(0x4ca700);
 for(unsigned trial=0;trial<80;++trial) {
  size_t n = trial<4 ? 33000 : rng()%16000+1; unsigned workers=trial%4+1;
  std::vector<Degrees> degree; for(unsigned w=0;w<workers;++w) degree.emplace_back(n);
  std::vector<std::vector<uint32_t>> expected(workers,std::vector<uint32_t>(n));
  for(size_t k=0;k<50000;++k) { unsigned w=rng()%workers; uint32_t node=rng()%n;degree[w].add(node);++expected[w][node]; }
  // Force overflow degrees and wide cursor blocks on both low and high node IDs.
  for(unsigned w=0;w<workers;++w) for(unsigned k=0;k<70000;++k) {uint32_t node=w%2 ? n-1 : 0;degree[w].add(node);++expected[w][node];}
  std::vector<uint32_t> starts(n+1); for(size_t u=0;u<n;++u) { starts[u+1]=starts[u]; for(unsigned w=0;w<workers;++w){assert(degree[w].get(u)==expected[w][u]);starts[u+1]+=expected[w][u];}}
  const auto original=starts;CursorLayout layout(starts);
  std::vector<WriteCursor> cursor;cursor.reserve(workers);for(unsigned w=0;w<workers;++w)cursor.emplace_back(layout,starts,degree[w]);
  for(size_t u=0;u<n;++u) {uint32_t next=original[u];for(unsigned w=0;w<workers;++w)for(uint32_t k=0;k<expected[w][u];++k)assert(cursor[w].take(u)==next++);assert(next==original[u+1]);assert(starts[u]==original[u+1]);}
 }
 //65535 fits exactly;65536 must use a wide block.
 for(uint32_t count : {65535U,65536U}) {std::vector<uint32_t> starts{0,count,count};Degrees d(2);for(uint32_t k=0;k<count;++k)d.add(0);CursorLayout layout(starts);assert(layout.wide_blocks==(count>65535));WriteCursor cursor(layout,starts,d);for(uint32_t k=0;k<count;++k)assert(cursor.take(0)==k);}
 std::cout<<"PASS compressed degrees and relative cursors, overflow and 65535/65536 boundaries\n";
}
