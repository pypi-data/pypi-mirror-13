#include <gtest/gtest.h>
#include <vector>
#include <string>

#include "string_views/TokenView.h"
#include "string_views/Utf8View.h"

using namespace std;
using texty::string_views::TokenView;
using texty::string_views::Utf8View;

TEST(TestTokenView, SimpleAscii) {
  string text = "some text with tokens";
  vector<string> expected {
    "some", "text", "with", "tokens"
  };
  vector<string> actual;
  TokenView view(text);
  for (auto tokenIdx: view) {
    actual.push_back(text.substr(tokenIdx.first, tokenIdx.second - tokenIdx.first));
  }
  EXPECT_EQ(expected, actual);
}
