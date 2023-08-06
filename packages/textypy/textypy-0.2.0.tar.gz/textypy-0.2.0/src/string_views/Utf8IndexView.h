#pragma once

#include <string>
#include "string_views/Utf8IndexIterator.h"
#include "string_views/BaseUtf8View.h"

namespace texty { namespace string_views {

class Utf8IndexView: public BaseUtf8View<
    Utf8IndexView, Utf8IndexIterator> {
 public:
  using iterator = Utf8IndexIterator;
  using parent_type = BaseUtf8View<Utf8IndexView, Utf8IndexIterator>;

  template<typename ...Args>
  Utf8IndexView(Args... args)
    : parent_type(std::forward<Args>(args)...) {}  
};

}} // texty::string_views

