#include <glog/logging.h>
#include <folly/Format.h>
#include <folly/FileUtil.h>
#include <pthread.h>
#include <thread>
#include <chrono>
#include <bitset>
#include <mutex>
#include <memory>
#include <condition_variable>
#include <atomic>
#include <string>
#include <map>
#include <set>
#include <vector>
#include <iostream>

#include "util/pretty_print.h"
#include "hashing/hash_funcs.h"
#include "hashing/SimHasher.h"
#include "hashing/ConstantSpaceSimHasher.h"

#include "hashing/BloomFilter.h"

#include "util/misc.h"

using texty::hashing::SimHasher;

using namespace std;

struct Thing {
  string name;
  Thing(string name): name(name){}
  Thing() {
    LOG(INFO) << "construct (" << name << ")";
  }
  ~Thing() {
    LOG(INFO) << "destruct (" << name << ")";
  }
};

struct IntBox {
  int x;
  IntBox(int x): x(x){}
};

using texty::util::pretty_print::prettyLog;

struct AtomHaving {
  uint16_t x;
  std::atomic<uintptr_t> something {0};
  bool compare_exchange_strong(uintptr_t expect, uintptr_t next) {
    return something.compare_exchange_strong(expect, next);
  }
  void store(uintptr_t x) {
    something.store(x);
  }
  uintptr_t load() {
    return something.load();
  }
};

std::map<string, string> loadData() {
  std::vector<string> fnames;
  for (size_t i = 1; i < 5; i++) {
    ostringstream oss;
    oss << "text/doc" << i << ".txt";
    fnames.push_back(oss.str());
  }
  std::map<string, string> data;
  for (auto &fname: fnames) {
    string current;
    CHECK(folly::readFile(fname.c_str(), current));
    data[fname] = current;
  }
  return data;
}

int main() {
  auto docs = loadData();
  // std::random_device rd;
  auto seeded = 17;
  texty::hashing::ConstantSpaceSimHasher<1024, 30> hasher(
    [](const string &text, uint64_t seed) { return texty::hashing::city_hash_64(text, seed); },
    seeded
  );
  std::map<string, uint64_t> constantHashed;
  for (auto &item: docs) {
    constantHashed[item.first] = hasher.hash(item.second);
  }
  for (auto &item: constantHashed) {
    for (auto &other: constantHashed) {
      if (item.first == other.first) {
        continue;
      }
      auto dist = texty::util::hammingDistance(item.second, other.second);
      LOG(INFO) << item.first << " vs " << other.first << " -> " << dist;
    }
  }

}
