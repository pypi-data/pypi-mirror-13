#include "string_views/Utf8Iterator.h"
#include <utf8/unchecked.h>

using namespace std;

namespace texty { namespace string_views {

Utf8Iterator::Utf8Iterator(const char *pos, const char *endPos)
  : position_(pos), endPos_(endPos) {}

Utf8Iterator::Utf8Iterator(const char *pos, const char *endPos, size_t dist)
  : position_(pos), endPos_(endPos), distanceFromStart_(dist) {}

pair<size_t, uint32_t> Utf8Iterator::operator*() {
  return std::make_pair(distanceFromStart_, utf8::unchecked::peek_next(position_));
}

Utf8Iterator& Utf8Iterator::operator=(const Utf8Iterator &other) {
  position_ = other.position_;
  endPos_ = other.endPos_;
  distanceFromStart_ = other.distanceFromStart_;
  return *this;
}

Utf8Iterator& Utf8Iterator::operator++() {
  const char *previous = position_;
  utf8::unchecked::next(position_);
  uintptr_t prevPtr = (uintptr_t) previous;
  uintptr_t currentPtr = (uintptr_t) position_;
  size_t offset = currentPtr - prevPtr;
  distanceFromStart_ += offset;
  return *this;
}

Utf8Iterator Utf8Iterator::operator++(int) {
  Utf8Iterator result(position_, endPos_, distanceFromStart_);
  ++result;
  return result;
}

bool Utf8Iterator::operator==(const Utf8Iterator &other) const {
  return position_ == other.position_;
}

bool Utf8Iterator::operator!=(const Utf8Iterator &other) const {
  return position_ != other.position_;
}

bool Utf8Iterator::good() {
  return ((uintptr_t) position_) < ((uintptr_t) endPos_);
}

Utf8Iterator::operator bool() {
  return good();
}

}} // texty::string_views
