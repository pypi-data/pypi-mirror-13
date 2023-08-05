#pragma once
#include <bitset>
#include <type_traits>
#include <vector>
#include <set>

namespace texty { namespace util {

template<typename T>
void voidDeleter(void *data) {
  T* ptr = (T*) data;
  delete ptr;
}

bool isAsciiPunctuation(char c);

template<typename T, size_t N = (sizeof(T) * 8),
  typename Ignore = typename std::enable_if<std::is_scalar<T>::value>::type>
size_t hammingDistance(T t1, T t2) {
  std::bitset<N> b1 = t1;
  std::bitset<N> b2 = t2;
  size_t acc = 0;
  for (size_t i = 0; i < N; i++) {
    if (b1[i] != b2[i]) {
      acc++;
    }
  }
  return acc;
}

}} // texty::util
