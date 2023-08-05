#pragma once
#include <vector>
#include <map>
#include <random>
#include <string>
#include "language_detection/LanguageProfiles.h"
#include "randomness/RandomDistribution.h"
#include "randomness/RandomVariable.h"
#include "string_views/NGramSampler.h"
#include "NGram.h"
#include "Language.h"

namespace texty { namespace language_detection {

class DetectionRunner {
 public:
  using sampler_type = string_views::NGramSampler<
      randomness::RandomDistribution<std::uniform_int_distribution, size_t>>;
 protected:
  LanguageProfiles *profiles_;
  sampler_type &ngramSampler_;
  std::map<Language, double> langScores_;
  randomness::RandomDistribution<std::uniform_int_distribution, size_t>
    ngramLengthDist_ {1, 3};

  randomness::RandomVariable<
    randomness::RandomDistribution<std::normal_distribution, double>>
    alpha_ {0.5, 0.05};

  std::map<Language, double> runTrial();
  Language getBestScore();
  const LanguageProfiles::lang_map& getRandomNGramScores();
  void run();
 public:
  DetectionRunner(
    LanguageProfiles *profiles,
    sampler_type &ngramSampler
  );
  Language detect();
  std::map<Language, double> getProbabilities();
};

}} // langdetectpp::detection