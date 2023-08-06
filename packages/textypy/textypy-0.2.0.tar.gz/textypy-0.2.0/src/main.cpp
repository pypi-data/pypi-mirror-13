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
#include <eigen3/Eigen/Dense>

#include "stemming/StemmerManager.h"
#include "stemming/ThreadSafeStemmerManager.h"
#include "html/goose/GooseContentExtractor.h"
#include "util/pretty_print.h"
#include "cleaning/basic.h"
#include "hashing/hash_funcs.h"
#include "hashing/SimHasher.h"
#include "hashing/ConstantSpaceSimHasher.h"
#include "string_views/RandomAccessNGramView.h"
#include "string_views/RandomAccessUtf8View.h"
#include "string_views/NGramSampler.h"
#include "language_detection/LanguageProfiles.h"
#include "randomness/RandomDistribution.h"
#include "Language.h"
#include "hashing/BloomFilter.h"
#include "corpus/Vocabulary.h"
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
using texty::stemming::ThreadSafeStemmerManager;
using texty::html::goose::GooseContentExtractor;
using texty::corpus::Vocabulary;

class TempDoc {
 public:
  using map_type = map<string, size_t>;
  using value_type = typename map_type::value_type;
  using iterator = typename map_type::iterator;
  using const_iterator = typename map_type::const_iterator;

  using term_type = string;
  using init_list = std::initializer_list<value_type>;
 protected:
  map_type terms_;
 public:
  TempDoc(init_list init)
    : terms_(init){}
  const_iterator begin() const {
    return terms_.begin();
  }
  const_iterator end() const {
    return terms_.end();
  }
};

using vocab_type = Vocabulary<TempDoc, string>;

int main() {
  google::InstallFailureSignalHandler();
  vocab_type vocab {
    {"dog", {0, 5}},
    {"cat", {1, 3}},
    {"fish", {2, 10}}
  };
  TempDoc doc {
    {"dog", 2},
    {"fish", 1},
    {"trolls", 16}
  };
  auto vec = vocab.vectorizeDenseFloatTfidf(doc);
  LOG(INFO) << vec;
}
