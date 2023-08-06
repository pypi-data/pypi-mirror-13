#include "string_views/Utf8IndexView.h"
#include "string_views/TokenView.h"
#include "util/misc.h"
#include "unicode/support.h"
#include <string>

using namespace std;

namespace texty { namespace string_views {

TokenView::TokenView(const string &text): utf8View_(text){}

TokenView::Iterator::Iterator(Utf8IndexIterator start, Utf8IndexIterator end)
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
  Utf8IndexIterator nextStart = end_;
  if (!nextStart) {
    start_ = end_;
    return *this;
  }
  while (nextStart.good()) {
    auto current = *nextStart;
    if (!unicode::isLetterPoint(current.second)) {
      ++nextStart;
      continue;
    }
    break;
  }
  start_ = nextStart;
  Utf8IndexIterator nextEnd = start_;
  if (!nextEnd.good()) {
    end_ = nextEnd;
    return *this;
  }
  size_t prevIdx = 999;
  while (nextEnd.good()) {
    auto current = *nextEnd;
    if (current.first == prevIdx) {
      break;
    }
    prevIdx = current.first;
    if (unicode::isLetterPoint(current.second)) {
      ++nextEnd;
      continue;
    }
    break;
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
  Utf8IndexIterator startIter = utf8View_.begin();
  Utf8IndexIterator firstEnd = startIter;
  while (firstEnd.good()) {
    auto current = *firstEnd;
    if (!unicode::isLetterPoint(current.second)) {
      break;
    }
    ++firstEnd;
  }
  return Iterator(startIter, firstEnd);
}

TokenView::Iterator TokenView::end() {
  return Iterator(utf8View_.end(), utf8View_.end());
}

}} // texty::string_views
