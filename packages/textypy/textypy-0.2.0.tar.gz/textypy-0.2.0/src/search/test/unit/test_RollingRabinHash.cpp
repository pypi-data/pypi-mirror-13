#include <gtest/gtest.h>
#include <string>
#include <map>
#include <unordered_map>
#include <vector>
#include <glog/logging.h>
#include "search/RollingRabinHash.h"
#include "search/RabinFingerprinter.h"

#include "string_views/ByteStringWindow.h"
#include "string_views/Utf8View.h"

using namespace std;
using namespace texty::search;
using namespace texty::string_views;

TEST(TestRollingRabinHash, JustOneLength) {
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

  RollingRabinHash<ByteStringWindow, 32> roller(
    ALPHA, MOD_N, ByteStringWindow(toHash), std::set<size_t> {4}
  );
  vector<uint64_t> actual;
  actual.push_back(roller.getHash(4));  
  while (roller.good()) {
    roller.step();
    actual.push_back(roller.getHash(4));
  }
  EXPECT_EQ(expected, actual);
}

TEST(TestRollingRabinHash, MultipleLengths) {
  const uint32_t ALPHA = 101;
  const uint64_t MOD_N = 5120000;
  string toHash = "fishes";
  map<size_t, vector<string>> pieces {
    {5, {"fishe", "ishes"}},
    {3, {"fis", "ish", "she", "hes"}},
    {2, {"fi", "is", "sh", "he", "es"}}
  };
  map<size_t, vector<uint64_t>> expected;
  RabinFingerprinter finger(ALPHA, MOD_N);
  for (auto &elem: pieces) {
    expected.insert(std::make_pair(elem.first, vector<uint64_t> {}));
    for (auto &part: elem.second) {
      expected.at(elem.first).push_back(
        finger.hash(ByteStringWindow(part))
      );
    }
  }
  RollingRabinHash<ByteStringWindow, 32> roller(
    ALPHA, MOD_N, ByteStringWindow(toHash), std::set<size_t> {2, 3, 5}
  );
  map<size_t, vector<uint64_t>> actual;
  for (auto &elem: roller.getHashes()) {
    actual.insert(std::make_pair(
      elem.first, std::vector<uint64_t> {elem.second}
    ));
  }
  while (roller.good()) {
    roller.step();
    for (auto &elem: roller.getHashes()) {
      if (elem.second != 0) {
        actual.at(elem.first).push_back(elem.second);
      }
    }
  }
  // for (auto elem: expected) {
  //   vector<uint64_t> expectedVec = elem.second;
  //   vector<uint64_t> actualVec = actual[elem.first];
  //   EXPECT_EQ(expectedVec, actualVec);
  // }
  EXPECT_EQ(expected, actual);
}


