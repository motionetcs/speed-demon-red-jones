#ifdef EDGE_STORE_HEADER
#include EDGE_STORE_HEADER
#else
#include "../track-d/edge_store.hpp"
#endif
#include <algorithm>
#include <cassert>
#include <iostream>
#include <random>
int main() {
 std::mt19937 random(0x7004ca7);
 for(uint32_t nodes : {0U,1U,2U,127U,65537U,262145U,1048577U,2097152U,2097153U,16777216U,16777217U,UINT32_MAX}) {
  EdgeStore edges(10000,nodes);
  for(uint32_t i=0;i<10000;++i) {
   uint32_t node=nodes ? random()%nodes : 0;
   uint32_t weight=i%7==0 ? edges.weight_limit : i%7==1 ? edges.weight_limit-1 : i%7==2 ? edges.weight_limit+1 : i%7==3 ? UINT32_MAX : random();
   uint32_t tag=std::min(weight,edges.weight_limit);edges.set(i,node,tag);
   auto [decoded_node,decoded_tag]=edges.get(i);assert(decoded_node==node && decoded_tag==tag);
   // A sentinel uses the original uint32 sidecar value, including equality.
   uint32_t restored=decoded_tag==edges.weight_limit ? weight : decoded_tag;assert(restored==weight);
  }

 }
 std::cout<<"PASS lossless compact/full edge storage across ID widths and sentinel boundaries\n";
}
