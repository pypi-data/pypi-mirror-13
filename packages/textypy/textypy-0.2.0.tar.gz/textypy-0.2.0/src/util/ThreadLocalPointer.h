#pragma once
#include <pthread.h>
#include "util/misc.h"

namespace texty { namespace util {

template<typename T>
class ThreadLocalPointer {
 protected:
  pthread_key_t ptKey_;
  bool empty_ {false};
  ThreadLocalPointer(const ThreadLocalPointer &other) = delete;
  ThreadLocalPointer& operator=(const ThreadLocalPointer &other) = delete;
  ThreadLocalPointer& operator=(ThreadLocalPointer other) = delete;
 public:
  ThreadLocalPointer(){
    pthread_key_create(&ptKey_, voidDeleter<T>);
  }
  ThreadLocalPointer(ThreadLocalPointer &&other) {
    ptKey_ = other.ptKey_;
    empty_ = other.empty_;
    other.empty_ = true;
  }
  ThreadLocalPointer& operator=(ThreadLocalPointer &&other) {
    if (!empty()) {
      pthread_key_delete(ptKey_);
    }
    ptKey_ = other.ptKey_;
    empty_ = other.empty_;
    other.empty_ = true;
    return *this;
  }
  bool empty() {
    return empty_;
  }
  bool good() {
    return !empty_;
  }
  operator bool() {
    return good();
  }
  T* get() {
    if (empty_) {
      return nullptr;
    }
    void *ptr = pthread_getspecific(ptKey_);
    if (ptr == nullptr) {
      ptr = (void*) new T;
      pthread_setspecific(ptKey_, ptr);
    }
    return (T*) ptr;
  }
  T* operator->() {
    return get();
  }
  ~ThreadLocalPointer() {
    if (!empty_) {
      pthread_key_delete(ptKey_);
    }
  }
};

}} // texty::util
