#pragma once

#include <string>
#include "string_views/BaseUtf8Iterator.h"

namespace texty { namespace string_views {

class Utf8IndexIterator : public BaseUtf8Iterator<Utf8IndexIterator,
    std::pair<size_t, uint32_t>>  {
 protected:
  using deref_result = std::pair<size_t, uint32_t>;
 public:
  using parent_type = BaseUtf8Iterator<Utf8IndexIterator, deref_result>;
  deref_result dereference() const;
  template<typename ...Args>
  Utf8IndexIterator(Args... args)
    : parent_type(std::forward<Args>(args)...) {}  
};

}} // texty::string_views

