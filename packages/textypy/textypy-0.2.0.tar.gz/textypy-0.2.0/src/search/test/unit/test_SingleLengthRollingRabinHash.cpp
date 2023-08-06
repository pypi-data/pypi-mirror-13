#include <gtest/gtest.h>
#include <string>
#include <map>
#include <unordered_map>
#include <vector>
#include <glog/logging.h>
#include "search/SingleLengthRollingRabinHash.h"
#include "search/RabinFingerprinter.h"

#include "string_views/ByteStringWindow.h"
#include "string_views/Utf8View.h"

using namespace std;
using namespace texty::search;
using namespace texty::string_views;

TEST(TestSingleLengthRollingRabinHash, Basic) {
  const uint32_t ALPHA = 101;
  const uint64_t MOD_N = 5120000;
  string toHash = "fishes";
  vector<string> pieces {
    "fish", "ishe", "shes"
  };
  vector<uint64_t> expected;
  RabinFingerprinter finger(ALPHA, MOD_N);
  for (auto &item: pieces) {
    ByteStringWindow window(item);
    expected.push_back(finger.hash(window));
  }
  SingleLengthRollingRabinHash<ByteStringWindow, 32> roller(
    ALPHA, MOD_N, ByteStringWindow(toHash), 4
  );
  vector<uint64_t> actual;
  actual.push_back(roller.getHash());  
  while (roller.good()) {
    roller.step();
    actual.push_back(roller.getHash());
  }
  EXPECT_EQ(expected, actual);
}


