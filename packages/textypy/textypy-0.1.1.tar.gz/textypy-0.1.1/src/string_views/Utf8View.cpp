#include "string_views/Utf8View.h"
#include <string>
#include <utf8/unchecked.h>

using namespace std;

namespace texty { namespace string_views {

Utf8View::Utf8View(const string &text): text_(text){}

Utf8View::Iterator::Iterator(const char *pos, const char *endPos)
  : position_(pos), endPos_(endPos) {}

Utf8View::Iterator::Iterator(const char *pos, const char *endPos, size_t dist)
  : position_(pos), endPos_(endPos), distanceFromStart_(dist) {}

pair<size_t, uint32_t> Utf8View::Iterator::operator*() {
  return std::make_pair(distanceFromStart_, utf8::unchecked::peek_next(position_));
}

Utf8View::Iterator& Utf8View::Iterator::operator=(const Iterator &other) {
  position_ = other.position_;
  endPos_ = other.endPos_;
  distanceFromStart_ = other.distanceFromStart_;
  return *this;
}

Utf8View::Iterator& Utf8View::Iterator::operator++() {
  const char *previous = position_;
  utf8::unchecked::next(position_);
  uintptr_t prevPtr = (uintptr_t) previous;
  uintptr_t currentPtr = (uintptr_t) position_;
  size_t offset = currentPtr - prevPtr;
  distanceFromStart_ += offset;
  return *this;
}

Utf8View::Iterator Utf8View::Iterator::operator++(int) {
  Iterator result(position_, endPos_, distanceFromStart_);
  ++result;
  return result;
}

bool Utf8View::Iterator::operator==(const Utf8View::Iterator &other) const {
  return position_ == other.position_;
}

bool Utf8View::Iterator::operator!=(const Utf8View::Iterator &other) const {
  return position_ != other.position_;
}

bool Utf8View::Iterator::good() {
  return ((uintptr_t) position_) < ((uintptr_t) endPos_);
}

Utf8View::Iterator::operator bool() {
  return good();
}

Utf8View::Iterator Utf8View::begin() {
  return Iterator(text_.data(), text_.data() + text_.size() - 1);
}

Utf8View::Iterator Utf8View::end() {
  auto endPtr = text_.data() + text_.size() - 1;
  return Iterator(endPtr, endPtr);
}

}} // texty::string_views
