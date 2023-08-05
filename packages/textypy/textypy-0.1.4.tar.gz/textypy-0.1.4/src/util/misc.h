#pragma once
#include <bitset>
#include <type_traits>
#include <vector>
#include <set>
#include <map>

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

template<typename T1, typename T2>
std::set<T1> keySet(const std::map<T1, T2> &aMap) {
  std::set<T1> result;
  for (auto &item: aMap) {
    result.insert(item.first);
  }
  return result;
}

template<typename T1, typename T2>
std::vector<T1> keyVec(const std::map<T1, T2> &aMap) {
  std::vector<T1> result;
  result.reserve(aMap.size());
  for (auto &item: aMap) {
    result.push_back(item.first);
  }
  return result;
}

template<
  typename T,
  typename TIgnore = typename std::enable_if<std::is_enum<T>::value>::type
>
size_t hashEnum(T enumVal) {
  using underlying = typename std::underlying_type<T>::type;
  return std::hash<underlying>()(
    static_cast<underlying>(enumVal)
  );
}

}} // texty::util
