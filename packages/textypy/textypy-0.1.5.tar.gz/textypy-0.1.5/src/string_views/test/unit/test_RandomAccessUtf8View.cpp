#include <gtest/gtest.h>
#include <vector>
#include <string>
#include <map>

#include "string_views/Utf8Iterator.h"
#include "string_views/Utf8View.h"
#include "string_views/RandomAccessUtf8View.h"

using namespace std;
using texty::string_views::RandomAccessUtf8View;

TEST(TestRandomAccessUtf8View, SimpleAscii) {
  string text = "cat text";
  map<size_t, uint32_t> expected;
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
