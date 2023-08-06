#pragma once
#include <tuple>
#include "string_views/TokenView.h"

namespace texty { namespace string_views {

class ShingleView2 {
 protected:
  const std::string &text_;
  TokenView tokenView_;
 public:
  ShingleView2(const std::string &text);
  class Iterator {
   protected:
    TokenView::Iterator first_;
    TokenView::Iterator second_;
   public:
    Iterator(TokenView::Iterator first, TokenView::Iterator second);
    Iterator& operator++();
    using IndexPair = std::pair<size_t, size_t>;
    using IndexTuple = std::tuple<IndexPair, IndexPair>;
    IndexTuple operator*();
    bool good();
    operator bool();
    Iterator operator++(int);
    bool operator==(const Iterator &other) const;
    bool operator!=(const Iterator &other) const;
    Iterator& operator=(const Iterator &other);
  };
  Iterator begin();
  Iterator end();
};

}} // texty::string_views
