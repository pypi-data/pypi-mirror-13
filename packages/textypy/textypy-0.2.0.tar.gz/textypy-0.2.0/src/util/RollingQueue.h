#pragma once
#include "util/macros.h"

namespace texty { namespace util {

template<typename T, typename TContainer>
class RollingQueue {
 public:
  using underlying_type = TContainer;
  using value_type = T;
 protected:
  size_t capacity_ {0};
  T defaultVal_;
  TContainer underlying_;
  size_t front_ {0};
  size_t back_ {0};
 public:
  RollingQueue(size_t capacity, T defaultVal)
    : capacity_(capacity), defaultVal_(defaultVal) {
    DEBUG_CHECK(capacity > 0);
    underlying_.insert(underlying_.begin(), defaultVal, capacity+1);
    back_ = capacity;
  }
  T& front() {
    return underlying_[front_];
  }
  T& back() {
    return underlying_[back_];
  }
  size_t size() {
    if (back_ < front_) {
      return ((capacity_+1) - front_) + back_;
    }
    return back_ - front_;
  }
  void push(const T& value) {
    underlying_[back_] = value;
    back_++;
    front_++;
    if (back_ > capacity_) {
      back_ = 0;
    }
    if (front_ > capacity_) {
      front_ = 0;
    }
  }
 protected:
  size_t getEffectiveIndex(size_t idx) const {
    idx += front_;
    if (idx > capacity_) {
      idx -= (capacity_ + 1);
    }
    return idx;
  }
 public:
  T& at(size_t idx) {
    DEBUG_CHECK(idx <= capacity_);
    return underlying_[getEffectiveIndex(idx)];
  }
  T& operator[](size_t idx) {
    return at(idx);
  }
  const T& at(size_t idx) const {
    DEBUG_CHECK(idx <= capacity_);
    return underlying_[getEffectiveIndex(idx)];
  }
  const T& operator[](size_t idx) const {
    return at(idx);
  }
};

}} // texty::util
