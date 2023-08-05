#pragma once
#include "string_views/Utf8View.h"
#include "string_views/Utf8Iterator.h"

#include <string>

namespace texty { namespace string_views {

class TokenView {
  const std::string &text_;
  Utf8View utf8View_;
 public:
  TokenView(const std::string &text);
  class Iterator {
   protected:
    Utf8Iterator start_;
    Utf8Iterator end_;
   public:
    Iterator(Utf8Iterator start, Utf8Iterator end);
    bool operator==(const Iterator &other) const;
    bool operator!=(const Iterator &other) const;
    bool good();
    operator bool();
    std::pair<size_t, size_t> operator*();
    Iterator& operator++();
    Iterator operator++(int);
  };
  Iterator begin();
  Iterator end();
};

}} // texty::string_views
