#include <gtest/gtest.h>
#include <vector>
#include <string>
#include <map>

#include "string_views/RandomAccessNGramView.h"

using namespace std;
using texty::string_views::RandomAccessNGramView;

TEST(TestRandomAccessNGramView, SimpleAscii) {
  string text = "cat text";
  map<size_t, pair<uint32_t, uint32_t>> expected2grams;
  for (size_t i = 0; i < text.size() - 1; i++) {
    expected2grams.insert(make_pair(i, make_pair(text[i], text[i+1])));
  }
  map<size_t, pair<uint32_t, uint32_t>> actual;
  for (size_t i = 0; i < text.size(); i++) {
    expected.insert(make_pair(i, (uint32_t) text[i]));
  }
  map<size_t, uint32_t> actual;
  auto view = RandomAccessUtf8View::create(text);
  for (size_t i = 0; i < view.size(); i++) {
    actual.insert(make_pair(i, view[i]));
  }
  EXPECT_EQ(expected, actual);
}
