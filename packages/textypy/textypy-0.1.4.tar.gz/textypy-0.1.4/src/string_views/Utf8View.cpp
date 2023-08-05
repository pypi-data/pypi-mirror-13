#include "string_views/Utf8View.h"
#include "string_views/Utf8Iterator.h"
#include <string>

using namespace std;

namespace texty { namespace string_views {

Utf8View::Utf8View(const string &text): text_(text){}

Utf8Iterator Utf8View::begin() {
  return Utf8Iterator(text_.data(), text_.data() + text_.size());
}

Utf8Iterator Utf8View::end() {
  auto endPtr = text_.data() + text_.size();
  return Utf8Iterator(endPtr, endPtr);
}

}} // texty::string_views
