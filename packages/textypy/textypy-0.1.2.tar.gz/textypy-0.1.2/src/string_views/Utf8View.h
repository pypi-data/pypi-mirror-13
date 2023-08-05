#pragma once

#include <string>

namespace texty { namespace string_views {

class Utf8View {
  const std::string &text_;
public:
  Utf8View(const std::string &text);

  class Iterator {
   protected:
    const char *position_;
    const char *endPos_;
    size_t distanceFromStart_ {0};
   public:
    Iterator(const char *pos, const char *endPos);
    Iterator(const char *pos, const char *endPos, size_t dist);
    std::pair<size_t, uint32_t> operator*();
    Iterator& operator=(const Iterator &other);
    Iterator& operator++();
    Iterator operator++(int);
    bool operator==(const Iterator &other) const;
    bool operator!=(const Iterator &other) const;
    bool good();
    operator bool();
  };

  Iterator begin();
  Iterator end();
};

}} // texty::string_views

