#include "string_views/Utf8View.h"
#include "string_views/TokenView.h"
#include "util/misc.h"
#include <string>

using namespace std;

namespace texty { namespace string_views {

TokenView::TokenView(const string &text): text_(text), utf8View_(text){}

TokenView::Iterator::Iterator(Utf8View::Iterator start, Utf8View::Iterator end)
  : start_(start), end_(end) {}

bool TokenView::Iterator::operator==(const Iterator &other) const {
  return start_ == other.start_ && end_ == other.end_;
}

bool TokenView::Iterator::operator!=(const Iterator &other) const {
  return start_ != other.start_ || end_ != other.end_;
}

bool TokenView::Iterator::good() {
  if (!start_.good() || start_ == end_) {
    return false;
  }
  return true;
}

TokenView::Iterator::operator bool() {
  return good();
}

std::pair<size_t, size_t> TokenView::Iterator::operator*() {
  return std::make_pair((*start_).first, (*end_).first);
}

TokenView::Iterator& TokenView::Iterator::operator++() {
  Utf8View::Iterator nextStart = end_;
  if (!nextStart) {
    return *this;
  }
  while (nextStart.good()) {
    auto current = *nextStart;
    if (current.second > 255) {
      break;
    }
    uint8_t cc = (uint8_t) current.second;
    char c = cc;
    if (c == ' ' || util::isAsciiPunctuation(c)) {
      ++nextStart;
      continue;
    }
    break;
  }
  start_ = nextStart;
  Utf8View::Iterator nextEnd = start_;
  if (!nextEnd.good()) {
    end_ = nextEnd;
    return *this;
  }
  while (nextEnd.good()) {
    auto current = *nextEnd;
    if (current.second > 255) {
      continue;
    }
    uint8_t c = (uint8_t) current.second;
    if (c == ' ' || util::isAsciiPunctuation(c)) {
      break;
    }
    ++nextEnd;
  }
  end_ = nextEnd;
  return *this;
}

TokenView::Iterator TokenView::Iterator::operator++(int) {
  TokenView::Iterator result(start_, end_);
  ++result;
  return result;
}

TokenView::Iterator TokenView::begin() {
  Utf8View::Iterator startIter = utf8View_.begin();
  Utf8View::Iterator firstEnd = startIter;
  while (firstEnd.good()) {
    auto current = *firstEnd;
    if (current.second < 255) {
      uint8_t cc = (uint8_t) current.second;
      char c = cc;
      if (c == ' ' || util::isAsciiPunctuation(c)) {
        break;
      }
    }
    ++firstEnd;
  }
  return Iterator(startIter, firstEnd);
}

TokenView::Iterator TokenView::end() {
  return Iterator(utf8View_.end(), utf8View_.end());
}

}} // texty::string_views
