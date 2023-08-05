#include <gtest/gtest.h>
#include <vector>
#include <string>

#include "string_views/Utf8Iterator.h"
#include "string_views/Utf8View.h"

using namespace std;
using texty::string_views::Utf8Iterator;
using texty::string_views::Utf8View;

TEST(TestUtf8View, SimpleAscii) {
  string text = "cat-related text";
  vector<pair<size_t, uint32_t>> expected;
  expected.reserve(text.size());
  for (size_t i = 0; i < text.size(); i++) {
    expected.push_back(make_pair(i, (uint32_t) text[i]));
  }
  Utf8View view(text);
  vector<pair<size_t, uint32_t>> actual;
  actual.reserve(text.size());
  for (auto cpPair: view) {
    actual.push_back(cpPair);
  }
  EXPECT_EQ(expected, actual);
}

TEST(TestUtf8View, SomeUnicode) {
  string text = "cat\u2014related text";
  vector<pair<size_t, uint32_t>> expected {
    {0, 99}, {1, 97}, {2, 116}, {3, 8212},
    {6, 114}, {7, 101}, {8, 108}, {9, 97},
    {10, 116}, {11, 101}, {12, 100}, {13, 32},
    {14, 116}, {15, 101}, {16, 120}, {17, 116}
  };
  Utf8View view(text);
  vector<pair<size_t, uint32_t>> actual;
  actual.reserve(text.size());
  for (auto cpPair: view) {
    actual.push_back(cpPair);
  }
  EXPECT_EQ(expected, actual);
}

