#pragma once
#include <string>
#include "string_views/ConstByteStringIterator.h"
#include "string_views/Utf8View.h"
#include "string_views/Utf8IndexView.h"


namespace texty { namespace string_views {
  
class ByteStringWindow {
 public:
  using iterator = ConstByteStringIterator<char>;
  using value_type = char;
  using size_type = size_t;
 protected:
  const char *start_;
  const char *end_;
 public:
  ByteStringWindow(const char *start, const char *end);
  ByteStringWindow(const char *start, size_t offset);
  ByteStringWindow(const std::string&, size_t start, size_t end);
  ByteStringWindow(const std::string&);
  size_type size() const;
  iterator begin() const;
  iterator end() const;
  iterator cbegin() const;
  iterator cend() const;
  value_type at(size_type idx) const;
  value_type operator[](size_type idx) const;
  Utf8View asUtf8View() const;
  Utf8IndexView asUtf8IndexView() const;
};

}} // texty::string_views
