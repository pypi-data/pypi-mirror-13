#pragma once
#include <type_traits>
#include <unordered_map>
#include "util/macros.h"

namespace texty { namespace util {

template<typename T>
class NullablePtr {
 public:
  using value_type = typename std::remove_pointer<T>::type;
  using pointer_type = typename std::add_pointer<T>::type;
 protected:
  pointer_type value_ {nullptr};
 public:
  NullablePtr(){}
  NullablePtr(pointer_type ptr): value_(ptr){}
  NullablePtr(const NullablePtr &other): value_(other.value_){}
  NullablePtr(NullablePtr &&other): value_(other.value_) {
    other.value_ = nullptr;
  }
  NullablePtr& operator=(const NullablePtr &other) {
    value_ = other.value_;
    return *this;
  }
  NullablePtr& operator=(NullablePtr &&other) {
    value_ = other.value_;
    other.value_ = nullptr;
    return *this;
  }
  NullablePtr& operator=(pointer_type ptr) {
    value_ = ptr;
    return *this;
  }
  bool good() const {
    return !!value_;
  }
  operator bool() const {
    return good();
  }
  bool operator=(const NullablePtr &other) const {
    return value_ != other.value_;
  }
  bool operator<(const NullablePtr &other) const {
    return value_ < other.value_;
  }
  pointer_type get() const {
    DEBUG_CHECK(good());
    return value_;
  }
  pointer_type operator->() const {
    DEBUG_CHECK(good());
    return value_;
  }
  value_type operator*() const {
    DEBUG_CHECK(good());
    return (*value_);
  }
  void erase() {
    if (value_) {
      delete value_;
      value_ = nullptr;
    }
  }
};

}} // texty::util
