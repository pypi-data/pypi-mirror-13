#include <string>
#include <vector>
#include <gtest/gtest.h>
#include <glog/logging.h>
#include <folly/FileUtil.h>
#include "language_detection/LanguageProfiles.h"
#include "language_detection/OwningLanguageDetector.h"
#include "Language_pprint.h"
#include "util/pretty_print.h"
#include "util/fs.h"


using namespace std;
using texty::language_detection::LanguageProfiles;
using texty::language_detection::OwningLanguageDetector;
using texty::Language;
using texty::util::pretty_print::prettyPrint;
using texty::util::fs::readFileSync;

TEST(TestLanguageDetection, TestWorkiness) {
  auto profiles = LanguageProfiles::loadFromFile("data/language_profiles.json");
  OwningLanguageDetector detector(profiles);
  const size_t seed = 7;
  vector<pair<string, Language>> files {
    {"ar_from_wikipedia.txt", Language::AR},
    {"en_jezebel.txt", Language::EN},
    {"ru_from_wikipedia.txt", Language::RU},
    {"de_from_wikipedia.txt", Language::DE},
    {"fr_from_wikipedia.txt", Language::FR},
    {"es_from_wikipedia.txt", Language::ES}
  };
  for (auto &item: files) {
    string fullPath = "text/language_detection/" + item.first;
    string data;
    readFileSync(fullPath, data);
    auto lang = detector.detect(data, seed);
    EXPECT_EQ(item.second, lang);
  }
}
