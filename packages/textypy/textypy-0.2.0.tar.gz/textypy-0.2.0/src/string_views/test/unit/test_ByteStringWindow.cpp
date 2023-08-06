#include <gtest/gtest.h>
#include <vector>
#include <string>
#include "string_views/ByteStringWindow.h"

using namespace texty::string_views;
using namespace std;

TEST(TestByteStringWindow, EntireString) {
  string text = "this is a test";
  string expected = "this is a test";
  string actual = "";
  ByteStringWindow window(text);
  for (auto c: window) {
    actual += c;
  }
  EXPECT_EQ(expected, actual);
}

TEST(TestByteStringWindow, EntireStringFromPointers) {
  string text = "this is a test";
  string expected = "this is a test";
  string actual = "";
  ByteStringWindow window(text.data(), text.data() + text.size());
  for (auto c: window) {
    actual += c;
  }
  EXPECT_EQ(expected, actual);
}

TEST(TestByteStringWindow, EntireStringFromPointerAndSize) {
  string text = "this is a test";
  string expected = "this is a test";
  string actual = "";
  ByteStringWindow window(text.data(), text.size());
  for (auto c: window) {
    actual += c;
  }
  EXPECT_EQ(expected, actual);
}


TEST(TestByteStringWindow, HalfString1) {
  string text = "this is a test";
  string expected = "this is";
  string actual = "";
  ByteStringWindow window(text, 0, 7);
  for (auto c: window) {
    actual += c;
  }
  EXPECT_EQ(expected, actual);
}

TEST(TestByteStringWindow, HalfString2) {
  string text = "this is a test";
  string expected = "a test";
  string actual = "";
  ByteStringWindow window(text, 8, text.size());
  for (auto c: window) {
    actual += c;
  }
  EXPECT_EQ(expected, actual);
}


TEST(TestByteStringWindow, MidString) {
  string text = "this is a test";
  string expected = "is a";
  string actual = "";
  ByteStringWindow window(text, 5, 9);
  for (auto c: window) {
    actual += c;
  }
  EXPECT_EQ(expected, actual);
}


TEST(TestByteStringWindow, TestUtf8Window) {
  string text = "this isn\u2019t a test, or is it?";
  vector<uint32_t> expectedPoints;
  {
    string firstPart = "isn";
    for (auto c: firstPart) {
      expectedPoints.push_back((uint32_t) c);
    }
    expectedPoints.push_back(8217);
    string secondPart = "t a test";
    for (auto c: secondPart) {
      expectedPoints.push_back((uint32_t) c);
    }
  }
  vector<uint32_t> actual;
  ByteStringWindow window(text, 5, text.find(", or is it?"));
  for (auto c: window.asUtf8View()) {
    actual.push_back(c);
  }
  EXPECT_EQ(expectedPoints, actual);
}
