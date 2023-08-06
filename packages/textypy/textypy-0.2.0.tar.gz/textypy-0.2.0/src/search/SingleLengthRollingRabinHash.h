#pragma once
#include <map>
#include "util/RollingQueue.h"
#include "util/SmallVector.h"
#include "util/misc.h"

namespace texty { namespace search {

template<typename TString, size_t SmallQueueSize>
class SingleLengthRollingRabinHash {
 public:
  using string_type = TString;
  using string_iter = typename TString::iterator;
  using value_type = uint64_t;
 protected:

  using codepoint_queue = util::RollingQueue<
    uint32_t, util::SmallVector<uint32_t, SmallQueueSize>
  >;

  uint32_t alpha_;
  uint64_t modN_;
  string_type target_;
  size_t size_;
  uint64_t currentHash_ {0};
  string_iter currentIt_;
  string_iter endIt_;
  size_t currentOffset_ {0};
  codepoint_queue cpQueue_;

  void initialize() {
    while (currentOffset_ < size_ && currentIt_ != endIt_) {
      auto cp = (uint32_t) *currentIt_;
      cpQueue_.push(cp);
      currentHash_ *= alpha_;
      currentHash_ %= modN_;
      currentHash_ += cp;
      currentHash_ %= modN_;
      ++currentIt_;
      ++currentOffset_;
    }
    if (currentOffset_ < (size_ - 1)) {
      currentHash_ = 0;
    } 
  }

 public:

  SingleLengthRollingRabinHash(uint32_t alpha, uint32_t modN,
      string_type target, size_t size)
    : alpha_(alpha),
      modN_(modN),
      target_(target),
      size_(size),
      currentIt_(target.begin()),
      endIt_(target.end()),
      cpQueue_(size, 0) {
    initialize();
  }

  size_t size() const {
    return size_;
  }

  size_t currentOffset() const {
    return currentOffset_;
  }

  bool atEnd() const {
    return !good();
  }

  bool good() const {
    return currentIt_ != endIt_;
  }

  uint64_t getHash() const {
    return currentHash_;
  }

  void reset() {
    currentHash_ = 0;
    currentOffset_ = 0;
    currentIt_ = target_.begin();
    initialize();
  }

  uint32_t alpha() const {
    return alpha_;
  }

  uint64_t modN() const {
    return modN_;
  }

  bool step() {
    if (atEnd()) {
      return false;
    }
    uint32_t front = cpQueue_.at(0);
    uint64_t maxPow = std::pow(alpha_, size_ - 1);
    maxPow %= modN_;
    maxPow *= front;
    maxPow %= modN_;
    currentHash_ -= maxPow;
    currentHash_ *= alpha_;
    currentHash_ %= modN_;
    uint32_t cp = *currentIt_;
    currentHash_ += cp;
    currentHash_ %= modN_;
    cpQueue_.push(cp);
    ++currentOffset_;
    ++currentIt_;
    return true;
  }
};

}} // texty::search