#pragma once

#include <string>
#include "language_detection/LanguageProfiles.h"
#include "language_detection/DetectionRunner.h"
#include "string_views/RandomAccessNGramView.h"
#include "Language.h"

namespace texty { namespace language_detection {

template<typename TDerived>
class LanguageDetector {
 protected:
  TDerived* selfPtr() {
    return static_cast<TDerived*>(this);
  }
 public:
  Language detect(const std::string &text, size_t seed) {
    auto profiles = selfPtr()->getProfiles();
    auto ngramView = string_views::RandomAccessNGramView::create(text);
    DetectionRunner::sampler_type sampler(std::move(ngramView), seed);
    DetectionRunner runner(profiles, sampler);
    return runner.detect();
  }
  std::map<Language, double> getProbabilities(const std::string &text, size_t seed) {
    auto profiles = selfPtr()->getProfiles();
    auto ngramView = string_views::RandomAccessNGramView::create(text);
    DetectionRunner::sampler_type sampler(std::move(ngramView), seed);
    DetectionRunner runner(profiles, sampler);
    return runner.getProbabilities();
  }
};

}} // texty::language_detection