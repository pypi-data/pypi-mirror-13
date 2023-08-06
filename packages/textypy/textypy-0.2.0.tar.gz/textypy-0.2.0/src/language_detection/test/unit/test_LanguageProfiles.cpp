#include <gtest/gtest.h>
#include <glog/logging.h>
#include <vector>
#include <string>
#include <map>

#include <iostream>

#include <vector>
#include <json.hpp>
#include "language_detection/LanguageProfiles.h"
#include "NGram.h"
#include "util/pretty_print.h"
#include "Language_pprint.h"
using namespace std;
using texty::language_detection::LanguageProfiles;
using texty::util::pretty_print::prettyPrint;
using texty::NGram;
using texty::Language;
using json = nlohmann::json;

TEST(TestLanguageProfiles, TestJsonLibSanity1) {
  json something = json::array({ 0.03, 0.15, 0.18 });
  auto asStr = something.dump();
  auto inflated = json::parse(asStr);
  double x = inflated[0];
  EXPECT_TRUE(x > 0.02);
  EXPECT_TRUE(x < 0.04);
  double y = inflated[1];
  EXPECT_TRUE(y > 0.14);
  EXPECT_TRUE(y < 0.16);
  double z = inflated[2];
  EXPECT_TRUE(z < 0.19);
  EXPECT_TRUE(z > 0.17);
}


TEST(TestLanguageProfiles, TestLoadFromJson) {
  json oneGrams {
    { json::array ({52}), json::array({ {"en", 0.31}, {"it", 0.17} }) },
    { json::array({17}), json::array({ {"en", 0.10}, {"it", 0.05} }) }    
  };
  json twoGrams {
    { json::array ({108, 57}), json::array({ {"de", 0.58}, {"en", 0.26} }) },
    { json::array({96, 105}), json::array({ {"fr", 0.12}, {"it", 0.07} }) }    
  };
  json threeGrams {
    { json::array ({519, 218, 105}), json::array({ {"en", 0.19}, {"es", 0.85} }) },
    { json::array({1283, 111, 2014}), json::array({
        {"de", 0.07}, {"en", 0.22}, {"fr", 0.04}
    }) }
  };  
  json allGrams = json::array({oneGrams, twoGrams, threeGrams});
  auto prof = LanguageProfiles::loadFromJson(allGrams.dump());
  auto scores1 = prof.getScores(NGram<uint32_t, 1> {52});
  EXPECT_TRUE(scores1[Language::EN] > 0.30);
  EXPECT_TRUE(scores1[Language::EN] < 0.32);
  EXPECT_TRUE(scores1[Language::IT] > 0.16);
  EXPECT_TRUE(scores1[Language::IT] < 0.18);

  auto scores2 = prof.getScores(NGram<uint32_t, 2> {96, 105});
  EXPECT_TRUE(scores2[Language::FR] > 0.11);
  EXPECT_TRUE(scores2[Language::FR] < 0.13);
  EXPECT_TRUE(scores2[Language::IT] > 0.06);
  EXPECT_TRUE(scores2[Language::IT] < 0.08);

  auto scores3 = prof.getScores(NGram<uint32_t, 3> {1283, 111, 2014});
  EXPECT_TRUE(scores3[Language::FR] > 0.03);
  EXPECT_TRUE(scores3[Language::FR] < 0.05);
  EXPECT_TRUE(scores3[Language::DE] > 0.06);
  EXPECT_TRUE(scores3[Language::DE] < 0.08);
  EXPECT_TRUE(scores3[Language::EN] > 0.21);  
  EXPECT_TRUE(scores3[Language::EN] < 0.23);
}
