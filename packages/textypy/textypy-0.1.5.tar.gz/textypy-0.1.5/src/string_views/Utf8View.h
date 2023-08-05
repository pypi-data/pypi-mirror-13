#pragma once

#include <string>
#include "string_views/Utf8Iterator.h"

namespace texty { namespace string_views {

class Utf8View {
  const std::string &text_;
public:
  Utf8View(const std::string &text);
  Utf8Iterator begin();
  Utf8Iterator end();
};

}} // texty::string_views

