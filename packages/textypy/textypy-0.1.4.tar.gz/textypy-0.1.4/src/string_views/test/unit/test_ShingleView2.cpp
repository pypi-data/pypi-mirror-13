#include <gtest/gtest.h>
#include <vector>
#include <string>

#include "string_views/ShingleView2.h"

using namespace std;
using texty::string_views::ShingleView2;

TEST(TestShingleView2, SimpleAscii) {
  string text = "this is text about cats";
  vector<pair<string, string>> expected {
    {"this", "is"},
    {"is", "text"},
    {"text", "about"},
    {"about", "cats"}
  };
  vector<pair<string, string>> actual;
  ShingleView2 view(text);
  for (auto idxs: view) {
    auto shingle1 = std::get<0>(idxs);
    auto shingle2 = std::get<1>(idxs);
    actual.push_back(make_pair(
      text.substr(shingle1.first, shingle1.second - shingle1.first),
      text.substr(shingle2.first, shingle2.second - shingle2.first)
    ));
  }
  EXPECT_EQ(expected, actual);
}

TEST(TestShingleView2, SomeUnicode) {
  string text = "this is \u2018text\u2019 about cats";
  vector<pair<string, string>> expected {
    {"this", "is"},
    {"is", "text"},
    {"text", "about"},
    {"about", "cats"}
  };
  vector<pair<string, string>> actual;
  ShingleView2 view(text);
  for (auto idxs: view) {
    auto shingle1 = std::get<0>(idxs);
    auto shingle2 = std::get<1>(idxs);
    actual.push_back(make_pair(
      text.substr(shingle1.first, shingle1.second - shingle1.first),
      text.substr(shingle2.first, shingle2.second - shingle2.first)
    ));
  }
  EXPECT_EQ(expected, actual);
}

TEST(TestShingleView2, WithPeriod) {
  string text = "This is \u2018text\u2019. Text about cats.";
  vector<pair<string, string>> expected {
    {"This", "is"},
    {"is", "text"},
    {"text", "Text"},
    {"Text", "about"},
    {"about", "cats"}
  };
  vector<pair<string, string>> actual;
  ShingleView2 view(text);
  for (auto idxs: view) {
    auto shingle1 = std::get<0>(idxs);
    auto shingle2 = std::get<1>(idxs);
    actual.push_back(make_pair(
      text.substr(shingle1.first, shingle1.second - shingle1.first),
      text.substr(shingle2.first, shingle2.second - shingle2.first)
    ));
  }
  EXPECT_EQ(expected, actual);
}

