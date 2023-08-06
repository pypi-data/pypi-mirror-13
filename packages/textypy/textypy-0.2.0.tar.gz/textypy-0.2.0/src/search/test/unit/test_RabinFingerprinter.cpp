#include <gtest/gtest.h>
#include <string>
#include "search/RabinFingerprinter.h"
#include "string_views/ByteStringWindow.h"

using namespace std;
using namespace texty::search;
using namespace texty::string_views;

TEST(TestRabinFingerprinter, BasicString) {
  RabinFingerprinter finger(101, 5120000);
  string something = "fish";
  auto hashed = finger.hash(something);
  EXPECT_EQ(3773526, hashed);
}

TEST(TestRabinFingerprinter, BasicStringOffsets) {
  RabinFingerprinter finger(101, 5120000);
  string something = " fish ";
  auto hashed = finger.hash(something, 1, 5);
  EXPECT_EQ(3773526, hashed);
}

TEST(TestRabinFingerprinter, CharPointers) {
  RabinFingerprinter finger(101, 5120000);
  string something = " fish ";
  auto hashed = finger.hash(
    something.data() + 1,
    something.data() + 5
  );
  EXPECT_EQ(3773526, hashed);
}

TEST(TestRabinFingerprinter, TestByteStringWindow) {
  RabinFingerprinter finger(101, 5120000);
  string something = "bad fish yes";
  ByteStringWindow window(something,
    something.find("fish"),
    something.find(" yes")
  );
  EXPECT_EQ(4, window.size());
  string expectedWindow = "fish";
  string actual = "";
  for (auto c: window) {
    actual += c;
  }
  EXPECT_EQ(expectedWindow, actual);
  auto hashed = finger.hash(window);
  EXPECT_EQ(3773526, hashed);
}
