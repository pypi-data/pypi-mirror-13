#pragma once
#include <map>
#include "util/RollingQueue.h"
#include "util/SmallVector.h"
#include "util/misc.h"

namespace texty { namespace search {

template<typename TString, size_t SmallQueueSize>
class RollingRabinHash {
 public:
  using string_type = TString;
  using string_iter = typename TString::iterator;
 protected:

  using codepoint_queue = util::RollingQueue<
    uint32_t, util::SmallVector<uint32_t, SmallQueueSize>
  >;

  uint32_t alpha_;
  uint64_t modN_;
  std::map<size_t, uint64_t> currentHashes_;
  string_type target_;
  string_iter currentIt_;
  string_iter endIt_;
  size_t currentOffset_ {0};

  // number of places we've gone beyond end iterator,
  // to finish fingerprinting shortest term lengths
  size_t overFlowOffset_ {0};
  codepoint_queue cpQueue_;
  size_t maxTerm_ {0};
  size_t minTerm_ {0};
  void initialize() {
    while (currentOffset_ < maxTerm_ && currentIt_ != endIt_) {
      auto cp = (uint32_t) *currentIt_;
      cpQueue_.push(cp);
      ++currentIt_;
      ++currentOffset_;
    }
    for (auto &elem: currentHashes_) {
      if (currentOffset_ < elem.first) {
        // the string was't long enough to reach this term
        continue;
      }
      size_t n = elem.first - 1;
      for (size_t i = 0; i < elem.first; i++) {
        uint32_t cp = cpQueue_[i];
        uint64_t powVal = std::pow(alpha_, n);
        powVal = (cp * powVal) % modN_;
        auto current = currentHashes_[elem.first];
        current = (current + powVal) % modN_;
        currentHashes_[elem.first] = current;
        --n;
      }
    }
  }

 public:
  RollingRabinHash(uint32_t alpha, uint32_t modN,
      string_type target, const std::set<size_t> &sizes)
    : alpha_(alpha),
      modN_(modN),
      target_(target),
      currentIt_(target.begin()),
      endIt_(target.end()),
      cpQueue_(util::largestKey(sizes), 0),
      maxTerm_(util::largestKey(sizes)),
      minTerm_(util::smallestKey(sizes)) {
    for (auto idx: sizes) {
      currentHashes_.insert(std::make_pair(idx, 0));
    }
    initialize();
  }

  size_t currentOffset() const {
    return currentOffset_;
  }

  bool atEnd() const {
    return currentIt_ == endIt_ && overFlowOffset_ == (maxTerm_ - minTerm_);
  }

  bool good() const {
    return !atEnd();
  }

  const std::map<size_t, uint64_t>& getHashes() const {
    return currentHashes_;
  }

  uint64_t getHash(size_t termSize) const {
    auto found = currentHashes_.find(termSize);
    if (found == currentHashes_.end()) {
      return 0;
    }
    return found->second;
  }

  void reset() {
    for (auto &item: currentHashes_) {
      item.second = 0;
    }
    currentOffset_ = 0;
    overFlowOffset_ = 0;
    currentIt_ = target_.begin();
    initialize();
  }

  uint32_t alpha() const {
    return alpha_;
  }

  uint64_t modN() const {
    return modN_;
  }

 protected:
  bool preOverflowStep() {
    uint32_t front = cpQueue_.at(0);
    for (auto &elem: currentHashes_) {
      uint64_t maxPow = std::pow(alpha_, elem.first - 1);
      maxPow %= modN_;
      maxPow *= front;
      maxPow %= modN_;
      elem.second -= maxPow;
      elem.second *= alpha_;
      elem.second %= modN_;
    }
    auto nextCp = (uint32_t) *currentIt_;
    for (auto &elem: currentHashes_) {
      if (elem.first == maxTerm_) {
        elem.second += nextCp;
      } else {
        elem.second += cpQueue_.at(elem.first);
      }
      elem.second %= modN_;
    }
    cpQueue_.push(nextCp);
    ++currentOffset_;
    ++currentIt_;
    return true;
  }

  bool postOverflowStep() {
    uint32_t front = cpQueue_.at(0);
    for (auto &elem: currentHashes_) {
      if (overFlowOffset_ >= (maxTerm_ - elem.first)) {
        elem.second = 0;
      } else {
        uint64_t maxPow = std::pow(alpha_, elem.first - 1);
        maxPow %= modN_;
        maxPow *= front;
        maxPow %= modN_;
        elem.second -= maxPow;
        elem.second %= modN_;
        elem.second *= alpha_;
        elem.second %= modN_;        

        auto nextCp = cpQueue_.at(elem.first);
        elem.second += nextCp;
        elem.second %= modN_;
      }
    }
    overFlowOffset_++;
    cpQueue_.push(0);
    return true;
  }
 public:
  bool step() {
    if (atEnd()) {
      return false;
    }
    if (currentIt_ == endIt_) {
      return postOverflowStep();
    }
    return preOverflowStep();
  }
};

}} // texty::search