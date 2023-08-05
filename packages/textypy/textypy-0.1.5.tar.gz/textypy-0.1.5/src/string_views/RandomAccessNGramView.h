#pragma once
#include <string>
#include <cassert>
#include "NGram.h"
#include "string_views/RandomAccessUtf8View.h"
#include "util/macros.h"

namespace texty { namespace string_views {

class RandomAccessNGramView {
 protected:
  const std::string &text_;
  RandomAccessUtf8View view_;
 public:
  RandomAccessNGramView(
    const std::string &text,
    RandomAccessUtf8View &&view
  );
  size_t size();
  static RandomAccessNGramView create(const std::string &text);

  template<size_t NGramSize>
  NGram<uint32_t, NGramSize> get(size_t idx) {
    DEBUG_CHECK(idx + NGramSize <= size());
    NGram<uint32_t, NGramSize> result;
    for (size_t i = 0; i < NGramSize; i++) {
      result[i] = view_[idx+i];
    }
    return result;
  }
};


}} // texty::string_views

