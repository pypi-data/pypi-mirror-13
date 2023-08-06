#pragma once
#include <algorithm>
#include <string>
#include <type_traits>
namespace texty { namespace search {

template<typename TIter>
uint64_t rabinFingerprint(uint32_t alpha, uint64_t modN, size_t count,
    TIter start, TIter end) {
  if (count == 0) {
    return 0;
  }
  size_t expo = count - 1;
  uint64_t acc = 0;
  for (TIter it = start; it != end; ++it) {
    auto codePoint = (uint32_t) *it;
    uint64_t powVal = std::pow(alpha, expo);
    powVal %= modN;
    powVal *= codePoint;
    powVal %= modN;
    acc = (acc + powVal) % modN;
    if (expo == 0) {
      break;
    }
    expo--;
  }
  return acc;
}

class RabinFingerprinter {
 protected:
  uint32_t alpha_ {0};
  uint64_t modN_ {0};
 public:
  RabinFingerprinter(uint32_t alpha, uint64_t modN);
  uint32_t alpha() const;
  uint32_t modN() const;
  uint64_t hash(const char*, const char*) const;
  uint64_t hash(const char*, size_t) const;

  template<typename TIter>
  uint64_t hash(size_t count, TIter start, TIter end) const {
    return rabinFingerprint(alpha_, modN_, count, start, end);
  }

  template<typename TCollection>
  uint64_t hash(const TCollection &collection) const {
    return hash(collection.size(),
      collection.begin(),
      collection.end()
    );
  }

  template<typename TCollection>
  uint64_t hash(const TCollection &collection,
      size_t start, size_t end) const {
    if (end <= start) {
      return 0;
    }
    size_t dist = end - start;
    auto startIt = collection.begin() + start;
    auto endIt = startIt + dist; 
    return hash(dist, startIt, endIt);
  } 
};


}} // texty::search
