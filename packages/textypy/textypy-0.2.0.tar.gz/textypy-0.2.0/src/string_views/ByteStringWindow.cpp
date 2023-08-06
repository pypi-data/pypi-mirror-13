#include <string>
#include "string_views/ByteStringWindow.h"

using namespace std;

namespace texty { namespace string_views {

ByteStringWindow::ByteStringWindow(const char *start, const char *end)
  : start_(start), end_(end) {}

ByteStringWindow::ByteStringWindow(const char *start, size_t offset)
  : start_(start), end_(start+offset) {}

ByteStringWindow::ByteStringWindow(const string &text, size_t start, size_t end)
  : start_(text.data() + start), end_(text.data() + end) {}

ByteStringWindow::ByteStringWindow(const string &text)
  : start_(text.data()), end_(text.data() + text.size()) {}

ByteStringWindow::size_type ByteStringWindow::size() const {
  auto startPtr = (uintptr_t) start_;
  auto endPtr = (uintptr_t) end_;
  if (endPtr <= startPtr) {
    return 0;
  }
  return endPtr - startPtr;
}

ByteStringWindow::iterator ByteStringWindow::begin() const {
  return ByteStringWindow::iterator(start_, end_, 0);
}

ByteStringWindow::iterator ByteStringWindow::cbegin() const {
  return ByteStringWindow::iterator(start_, end_, 0);
}

ByteStringWindow::iterator ByteStringWindow::end() const {
  return ByteStringWindow::iterator(start_, end_, size());
}

ByteStringWindow::iterator ByteStringWindow::cend() const {
  return ByteStringWindow::iterator(start_, end_, size());
}

ByteStringWindow::value_type ByteStringWindow::at(size_t idx) const {
  const char *ptr = start_;
  ptr += idx;
  return *ptr;
}

ByteStringWindow::value_type ByteStringWindow::operator[](size_t idx) const {
  return at(idx);
}

Utf8View ByteStringWindow::asUtf8View() const {
  return Utf8View(start_, end_);
}

Utf8IndexView ByteStringWindow::asUtf8IndexView() const {
  return Utf8IndexView(start_, end_);
}

}} // texty::string_views
