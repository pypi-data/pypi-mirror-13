#include <vector>
#include <string>
#include <map>

#include "language_detection/DetectionRunner.h"
#include "util/macros.h"
#include "util/pretty_print.h"

using namespace std;

namespace texty { namespace language_detection {

using util::pretty_print::prettyPrint;

using string_views::RandomAccessNGramView;
const double CONV_THRESHOLD = 0.99999;
const size_t BASE_FREQ = 10000;
const size_t ITERATION_LIMIT = 1000;

DetectionRunner::DetectionRunner(LanguageProfiles *profiles,
    sampler_type &ngramSampler)
  : profiles_(profiles), ngramSampler_(ngramSampler) {}

Language DetectionRunner::getBestScore() {
  double maxScore = 0.0;
  Language maxLang = Language::UNKNOWN;

  for (auto &item: langScores_) {
    if (item.second > maxScore) {
      maxScore = item.second;
      maxLang = item.first;
    }
  }
  return maxLang;
}

map<Language, double> DetectionRunner::getProbabilities() {
  run();
  return langScores_;
}

Language DetectionRunner::detect() {
  run();
  return getBestScore();
}

void DetectionRunner::run() {
  const size_t numTrials = 7;
  for (size_t trialN = 0; trialN < numTrials; trialN++) {
    alpha_.warble();
    auto probs = runTrial();
    double divisor = (double) trialN;
    if (divisor <= 0) {
      divisor = 1.0;
    }
    for (auto &item: probs) {
      double toAdd = item.second / divisor;
      langScores_[item.first] += toAdd;
    }
  }
}

const LanguageProfiles::lang_map& DetectionRunner::getRandomNGramScores() {
  auto ngLen = ngramLengthDist_.get();
  if (ngLen == 1) {
    auto sample = ngramSampler_.get<1>();
    return profiles_->getScores(sample);
  } else if (ngLen == 2) {
    auto sample = ngramSampler_.get<2>();
    return profiles_->getScores(sample);
  } else if (ngLen == 3) {
    auto sample = ngramSampler_.get<3>();
    return profiles_->getScores(sample);
  }
  DEBUG_CHECK(false);
  return profiles_->getEmptyScores();
}


std::map<Language, double> DetectionRunner::runTrial() {
  std::map<Language, double> probs;
  auto &allLangs = getAllLanguages();
  double startingProb = 1.0 / (double) allLangs.size();
  for (auto lang: allLangs) {
    probs.insert(make_pair(lang, startingProb));
  }
  for (size_t i = 0;; i++) {
    double weight = alpha_.get() / BASE_FREQ;
    auto langWordScores = getRandomNGramScores();
    for (auto &item: probs) {
      double score = 0.0;
      auto found = langWordScores.find(item.first);
      if (found != langWordScores.end()) {
        score = found->second;
      }
      item.second *= score + weight;
    }
    if (i % 5 == 0) {
      double maxp = 0.0;
      double sump = 0.0;
      for (auto &elem: probs) {
        sump += elem.second;
      }
      for (auto &elem: probs) {
        double p = elem.second / sump;
        if (maxp < p) {
          maxp = p;
        }
        elem.second = p;
      }
      if (maxp > CONV_THRESHOLD || i >= ITERATION_LIMIT) {
        break;
      }
    }
  }
  return probs;
}

}} // langdetectpp::detection
