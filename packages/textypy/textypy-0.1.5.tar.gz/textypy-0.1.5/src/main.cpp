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
#include "string_views/RandomAccessNGramView.h"
#include "string_views/RandomAccessUtf8View.h"
#include "string_views/NGramSampler.h"
#include "language_detection/LanguageProfiles.h"
#include "randomness/RandomDistribution.h"

#include "hashing/BloomFilter.h"

#include "util/misc.h"

using texty::hashing::SimHasher;

using namespace std;


std::map<string, string> loadData() {
  std::vector<string> fnames;
  for (size_t i = 1; i < 6; i++) {
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

using texty::string_views::NGramSampler;
using texty::randomness::RandomDistribution;
using texty::language_detection::LanguageProfiles;
int main() {
  google::InstallFailureSignalHandler();
  string fname = "data/language_profiles.json";
  auto profs = LanguageProfiles::loadFromFile(fname);
}

// int main() {
//   auto docs = loadData();
//   auto keys = texty::util::keyVec(docs);
//   auto data = docs[keys[0]];
//   LOG(INFO) << data;
//   auto sampler = NGramSampler<RandomDistribution<uniform_int_distribution, size_t>>::create(data);
//   for (size_t i = 0; i < 10; i++) {
//     prettyLog(sampler.get<1>());
//   }
//   for (size_t i = 0; i < 10; i++) {
//     prettyLog(sampler.get<2>());
//   }
//   for (size_t i = 0; i < 10; i++) {
//     prettyLog(sampler.get<3>());
//   }
// }
