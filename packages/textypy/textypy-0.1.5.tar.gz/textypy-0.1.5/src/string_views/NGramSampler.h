#pragma once
#include "string_views/RandomAccessNGramView.h"
#include "NGram.h"
namespace texty { namespace string_views {


template<typename TDistrib>
class NGramSampler {
 public:
  using distribution_type = TDistrib;
  using view_type = RandomAccessNGramView;
 protected:
  view_type view_;
  distribution_type dist_;
 public:
  NGramSampler(view_type &&view, size_t seed)
    : view_(std::move(view)),
      dist_(distribution_type::createMaxInterval(seed)){}
  NGramSampler(view_type &&view)
    : view_(std::move(view)),
      dist_(distribution_type::createMaxInterval()){}
  static NGramSampler create(const std::string &text) {
    auto view = view_type::create(text);
    return NGramSampler(std::move(view));
  }
  static NGramSampler create(const std::string &text, size_t seed) {
    auto view = view_type::create(text);
    return NGramSampler(std::move(view), seed);
  }

  template<size_t NGramSize>
  NGram<uint32_t, NGramSize> get() {
    NGram<uint32_t, NGramSize> result;
    size_t lastIndex = view_.size() - NGramSize;
    return view_.get<NGramSize>(dist_.getConstrained(0, lastIndex));
  }

};

}} // texty::string_views
