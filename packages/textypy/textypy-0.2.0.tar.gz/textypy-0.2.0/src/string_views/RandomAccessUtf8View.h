#pragma once

#include <string>
#include <vector>
#include "string_views/Utf8IndexIterator.h"

namespace texty { namespace string_views {

class RandomAccessUtf8View {
 public:
  using iterator = Utf8IndexIterator;
 protected:
  const std::string &text_;
  std::vector<size_t> offsets_;
  RandomAccessUtf8View(const std::string &text, std::vector<size_t> &&offsets);
 public:
  RandomAccessUtf8View(const RandomAccessUtf8View &other);
  RandomAccessUtf8View(RandomAccessUtf8View &&other);
  static RandomAccessUtf8View create(const std::string &text);
  const std::vector<size_t>& getOffsets() const;
  size_t size() const;
  size_t bytes() const;
  uint32_t at(size_t idx) const;
  uint32_t operator[](size_t idx) const;
  iterator begin();
  iterator end();
};

}} // texty::string_views

