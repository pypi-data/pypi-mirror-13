#pragma once
#include <functional>

namespace texty { namespace util {

class ScopeGuard {
 protected:
  bool dismissed_ {false};
  std::function<void()> func_;
 public:
  ScopeGuard(std::function<void()> func);
  ~ScopeGuard();
  void dismiss();
};


}} // texty::util
