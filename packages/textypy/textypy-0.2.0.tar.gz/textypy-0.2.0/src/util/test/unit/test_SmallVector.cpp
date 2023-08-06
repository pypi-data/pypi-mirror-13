#include <gtest/gtest.h>
#include <vector>
#include "util/SmallVector.h"

using namespace std;
using texty::util::SmallVector;

TEST(TestSmallVector, ConstructionNotOverflown) {
  SmallVector<int, 4> nums {5, 2, 1, 8};
  vector<int> expected {5, 2, 1, 8};

  EXPECT_EQ(4, nums.size());
  EXPECT_FALSE(nums.isOverflown());
  vector<int> actual;
  for (auto item: nums) {
    actual.push_back(item);
  }
  EXPECT_EQ(expected, actual);
}

TEST(TestSmallVector, ConstructionOverflown) {
  SmallVector<int, 4> nums {5, 2, 1, 8, 9};
  vector<int> expected {5, 2, 1, 8, 9};

  EXPECT_EQ(5, nums.size());
  EXPECT_TRUE(nums.isOverflown());
  vector<int> actual;
  for (auto item: nums) {
    actual.push_back(item);
  }
  EXPECT_EQ(expected, actual);
}

TEST(TestSmallVector, TestOverflowAfterConstruction) {
  SmallVector<int, 4> nums {5, 2, 1};
  for (int x = 8; x < 10; x++) {
    nums.push_back(x);
  }
  EXPECT_EQ(5, nums.size());
  EXPECT_TRUE(nums.isOverflown());
  vector<int> expected {5, 2, 1, 8, 9};
  vector<int> actual;
  for (auto item: nums) {
    actual.push_back(item);
  }
  EXPECT_EQ(expected, actual);
}

TEST(TestSmallVector, TestPopFromOverflow) {
  SmallVector<int, 4> nums {5, 2, 1, 7, 8, 9};
  EXPECT_EQ(6, nums.size());
  for (size_t i = 0; i < 3; i++) {
    nums.pop_back();
  }
  EXPECT_EQ(3, nums.size());
  vector<int> expected {5, 2, 1};
  auto actual = nums.copyToVector();
  EXPECT_EQ(expected, actual);
}
