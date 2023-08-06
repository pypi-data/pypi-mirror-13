#include <gtest/gtest.h>
#include <vector>
#include "util/RollingQueue.h"
#include "util/SmallVector.h"

using namespace std;
using texty::util::RollingQueue;
using texty::util::SmallVector;

TEST(TestRollingQueue, Basic) {
  RollingQueue<int, vector<int>> aQueue(4, 10);
  EXPECT_EQ(4, aQueue.size());
  for (int i = 20; i < 24; i++) {
    aQueue.push(i);
    EXPECT_EQ(4, aQueue.size());
  }
  EXPECT_EQ(20, aQueue.at(0));
  EXPECT_EQ(21, aQueue.at(1));
  EXPECT_EQ(22, aQueue.at(2));
  EXPECT_EQ(23, aQueue.at(3));
}

TEST(TestRollingQueue, BasicWithSmallVector) {
  RollingQueue<int, SmallVector<int>> aQueue(4, 10);
  EXPECT_EQ(4, aQueue.size());
  for (int i = 20; i < 24; i++) {
    aQueue.push(i);
    EXPECT_EQ(4, aQueue.size());
  }
  EXPECT_EQ(20, aQueue.at(0));
  EXPECT_EQ(21, aQueue.at(1));
  EXPECT_EQ(22, aQueue.at(2));
  EXPECT_EQ(23, aQueue.at(3));
}


TEST(TestRollingQueue, MoreInsertion) {
  RollingQueue<int, vector<int>> aQueue(4, 10);
  EXPECT_EQ(4, aQueue.size());
  for (int i = 20; i < 24; i++) {
    aQueue.push(i);
    EXPECT_EQ(4, aQueue.size());
  }
  aQueue.push(30);
  EXPECT_EQ(21, aQueue.at(0));
  EXPECT_EQ(22, aQueue.at(1));
  EXPECT_EQ(23, aQueue.at(2));
  EXPECT_EQ(30, aQueue.at(3));
}

