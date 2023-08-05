#pragma once
#include <pthread.h>
#include "util/misc.h"

namespace texty { namespace util {

template<typename T>
class ThreadLocalPointer {
 protected:
  pthread_key_t ptKey_;
 public:
  ThreadLocalPointer(){
    pthread_key_create(&ptKey_, voidDeleter<T>);
  }
  T* get() {
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
  ~TLocalPtr() {
    pthread_key_delete(ptKey_);
  }
};

}} // texty::util
