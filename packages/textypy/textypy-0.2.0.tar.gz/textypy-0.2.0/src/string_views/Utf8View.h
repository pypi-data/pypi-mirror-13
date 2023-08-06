#pragma once

#include <string>
#include "string_views/Utf8Iterator.h"
#include "string_views/BaseUtf8View.h"

namespace texty { namespace string_views {

class Utf8View: public BaseUtf8View<Utf8View, Utf8Iterator> {
 public:
  using iterator = Utf8Iterator;
  using parent_type = BaseUtf8View<Utf8View, Utf8Iterator>;
  template<typename ...Args>
  Utf8View(Args... args)
    : parent_type(std::forward<Args>(args)...) {}  
};

}} // texty::string_views

