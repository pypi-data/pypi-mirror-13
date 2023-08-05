#pragma once
#include <string>
#include <sstream>

#include <glog/logging.h>
#include "hashing/HashFamily.h"
#include "hashing/BloomFilter.h"
#include "string_views/ShingleView2.h"

namespace texty { namespace hashing {

template<size_t NBloomBits, size_t NBloomHashes>
class ConstantSpaceSimHasher {
  static const size_t N = 64;
  using hashed_type = uint64_t;
  using value_type = std::string;
  using bloom_filter_type = BloomFilter<value_type, hashed_type, NBloomBits, NBloomHashes>;
  using hash_family_type = typename bloom_filter_type::hash_family_type;
  using HashFunc = std::function<hashed_type (const value_type&, hashed_type)>;
  using HashArray = std::array<int32_t, N>;

 protected:
  HashFunc hashFunc_;
  hashed_type seed_;
  hash_family_type hashfamily_;
  void addToHash(HashArray &data, const value_type &item) {
    std::bitset<N> hashBits = hashFunc_(item, seed_);
    for (size_t i = 0; i < N; i++) {
      if (hashBits[i] == 0) {
        data[i] -= 1;
      } else {
        data[i] += 1;
      }
    }
  }

 public:
  ConstantSpaceSimHasher(HashFunc hashFunc, size_t bloomSeed)
    : hashFunc_(hashFunc),
      seed_(bloomSeed),
      hashfamily_(hash_family_type::create(hashFunc_, bloomSeed)) {}

  hashed_type hash(const std::string &text) {
    HashArray hashAccumulator;
    for (size_t i = 0; i < N; i++) {
      hashAccumulator[i] = 0;
    }
    bloom_filter_type bloom(&hashfamily_);
    string_views::ShingleView2 shingleView(text);
    auto shingleIt = shingleView.begin();
    auto endShingle = shingleView.end();
    while (shingleIt.good()) {
      if (shingleIt == endShingle) {
        break;
      }
      std::ostringstream oss;
      auto shingle = *shingleIt;
      auto part1 = std::get<0>(shingle);
      auto part2 = std::get<1>(shingle);
      oss << text.substr(part1.first, part1.second - part1.first);
      oss << " ";
      oss << text.substr(part2.first, part2.second - part2.first);
      std::string currentShingle = oss.str();
      if (bloom.insertIfMissing(currentShingle)) {
        addToHash(hashAccumulator, currentShingle);
      }
      ++shingleIt;
    }
    std::bitset<N> hashBits;
    for (size_t i = 0; i < N; i++) {
      if (hashAccumulator[i] >= 0) {
        hashBits[i] = 1;
      }
    }
    return hashBits.to_ullong();    
  }

};

}} // texty::hashing

