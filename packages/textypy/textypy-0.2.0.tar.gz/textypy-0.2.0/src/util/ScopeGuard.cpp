#include "util/ScopeGuard.h"

using namespace std;

namespace texty { namespace util {

ScopeGuard::ScopeGuard(function<void()> func)
  : func_(std::move(func)){}

ScopeGuard::~ScopeGuard() {
  if (!dismissed_) {
    func_();
  }
}

void ScopeGuard::dismiss() {
  dismissed_ = true;
}

}} // texty::util
