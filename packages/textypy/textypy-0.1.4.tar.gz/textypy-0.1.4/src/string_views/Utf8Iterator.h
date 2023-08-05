#pragma once

#include <string>

namespace texty { namespace string_views {

class Utf8Iterator {
 protected:
  const char *position_;
  const char *endPos_;
  size_t distanceFromStart_ {0};
 public:
  Utf8Iterator(const char *pos, const char *endPos);
  Utf8Iterator(const char *pos, const char *endPos, size_t dist);
  std::pair<size_t, uint32_t> operator*();
  Utf8Iterator& operator=(const Utf8Iterator &other);
  Utf8Iterator& operator++();
  Utf8Iterator operator++(int);
  bool operator==(const Utf8Iterator &other) const;
  bool operator!=(const Utf8Iterator &other) const;
  bool good();
  operator bool();
};

}} // texty::string_views

