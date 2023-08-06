#include "string_views/ShingleView2.h"

using namespace std;

namespace texty { namespace string_views {

ShingleView2::ShingleView2(const string &text): text_(text), tokenView_(text) {}

ShingleView2::Iterator::Iterator(TokenView::Iterator first, TokenView::Iterator second)
  : first_(first), second_(second){}

ShingleView2::Iterator& ShingleView2::Iterator::operator++() {
  if (!second_.good()) {
    if (first_.good()) {
      ++second_;
      first_ = second_;
    }
    return *this;
  }
  first_ = second_;
  ++second_;
  return *this;
}

ShingleView2::Iterator::IndexTuple ShingleView2::Iterator::operator*() {
  return std::make_tuple(*first_, *second_);
}

bool ShingleView2::Iterator::good() {
  if (!first_.good() || first_ == second_) {
    return false;
  }
  return true;
}

ShingleView2::Iterator::operator bool() {
  return good();
}

ShingleView2::Iterator ShingleView2::Iterator::operator++(int) {
  Iterator result(first_, second_);
  ++result;
  return result;
}

bool ShingleView2::Iterator::operator==(const Iterator &other) const {
  return first_ == other.first_;
}

bool ShingleView2::Iterator::operator!=(const Iterator &other) const {
  return first_ != other.first_ && second_ != other.second_;
}

ShingleView2::Iterator& ShingleView2::Iterator::operator=(const Iterator &other) {
  first_ = other.first_;
  second_ = other.second_;
  return *this;
}

ShingleView2::Iterator ShingleView2::begin() {
  auto iter1 = tokenView_.begin();
  return Iterator(iter1, iter1++);
}

ShingleView2::Iterator ShingleView2::end() {
  auto iterEnd = tokenView_.end();
  return Iterator(iterEnd, iterEnd);
}

}} // texty::string_views
