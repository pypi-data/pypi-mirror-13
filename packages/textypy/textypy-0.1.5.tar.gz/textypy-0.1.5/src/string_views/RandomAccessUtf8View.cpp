#include "string_views/RandomAccessUtf8View.h"
#include "string_views/Utf8View.h"
#include "string_views/Utf8Iterator.h"
#include <utf8/unchecked.h>
#include <string>

using namespace std;

namespace texty { namespace string_views {

RandomAccessUtf8View::RandomAccessUtf8View(const string &text, vector<size_t> &&offsets)
  : text_(text), offsets_(std::move(offsets)) {}

RandomAccessUtf8View::RandomAccessUtf8View(const RandomAccessUtf8View &other)
  : text_(other.text_), offsets_(other.offsets_) {}

RandomAccessUtf8View::RandomAccessUtf8View(RandomAccessUtf8View &&other)
  : text_(other.text_), offsets_(std::move(other.offsets_)) {}

RandomAccessUtf8View RandomAccessUtf8View::create(const string &text) {
  vector<size_t> offsets;
  offsets.reserve(text.size());
  Utf8View view(text);
  for (auto cpPair: view) {
    offsets.push_back(cpPair.first);
  }
  return RandomAccessUtf8View(text, std::move(offsets));
}

const vector<size_t>& RandomAccessUtf8View::getOffsets() const {
  return offsets_;
}

uint32_t RandomAccessUtf8View::at(size_t idx) const {
  const char *iter = text_.data();
  iter += offsets_[idx];
  return utf8::unchecked::next(iter);
}

uint32_t RandomAccessUtf8View::operator[](size_t idx) const {
  return at(idx);
}

size_t RandomAccessUtf8View::size() const {
  return offsets_.size();
}

size_t RandomAccessUtf8View::bytes() const {
  if (offsets_.size() == 0) {
    return 0;
  }
  return offsets_.back();
}

Utf8Iterator RandomAccessUtf8View::begin() {
  return Utf8Iterator(text_.data(), text_.data() + text_.size() - 1);
}

Utf8Iterator RandomAccessUtf8View::end() {
  auto endPtr = text_.data() + text_.size() - 1;
  return Utf8Iterator(endPtr, endPtr);
}

}} // texty::string_views
