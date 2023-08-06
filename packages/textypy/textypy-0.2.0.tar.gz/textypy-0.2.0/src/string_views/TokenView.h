#pragma once
#include "string_views/Utf8IndexView.h"
#include "string_views/Utf8IndexIterator.h"

#include <string>

namespace texty { namespace string_views {

class TokenView {
  Utf8IndexView utf8View_;
 public:
  TokenView(const std::string &text);
  class Iterator {
   protected:
    Utf8IndexIterator start_;
    Utf8IndexIterator end_;
   public:
    Iterator(Utf8IndexIterator start, Utf8IndexIterator end);
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
