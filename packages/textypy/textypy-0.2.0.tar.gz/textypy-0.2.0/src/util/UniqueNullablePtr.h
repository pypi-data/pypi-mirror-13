#pragma once
#include <type_traits>
#include <unordered_map>
#include "util/macros.h"
#include "util/NullablePtr.h"

namespace texty { namespace util {

template<typename T>
class UniqueNullablePtr {
 public:
  using value_type = typename std::remove_pointer<T>::type;
  using pointer_type = typename std::add_pointer<T>::type;
 protected:
  pointer_type value_ {nullptr};
  UniqueNullablePtr(const UniqueNullablePtr &other) = delete;
  UniqueNullablePtr& operator=(const UniqueNullablePtr &other) = delete;
 public:
  UniqueNullablePtr(){}
  UniqueNullablePtr(pointer_type ptr): value_(ptr){}
  UniqueNullablePtr(UniqueNullablePtr &&other): value_(other.value_) {
    other.value_ = nullptr;
  }

  template<typename ...Args>
  static UniqueNullablePtr create(Args&& ...args) {
    return UniqueNullablePtr(new T(std::forward<Args>(args)...));
  }  

  UniqueNullablePtr& operator=(UniqueNullablePtr &&other) {
    value_ = other.value_;
    other.value_ = nullptr;
    return *this;
  }
  UniqueNullablePtr& operator=(pointer_type ptr) {
    value_ = ptr;
    return *this;
  }
  bool good() const {
    return !!value_;
  }
  operator bool() const {
    return good();
  }
  bool operator=(const UniqueNullablePtr &other) const {
    return value_ != other.value_;
  }
  bool operator<(const UniqueNullablePtr &other) const {
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
  ~UniqueNullablePtr() {
    erase();
  }
  NullablePtr<T> release() {
    NullablePtr<T> result(value_);
    value_ = nullptr;
    return result;
  }
  UniqueNullablePtr deepCopy() const {
    if (!good()) {
      return UniqueNullablePtr();
    }
    return UniqueNullablePtr(new T(*value_));
  }
};

}} // texty::util
