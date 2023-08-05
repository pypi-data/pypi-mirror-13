#include <unordered_map>
#include <map>
#include <string>
#include <json.hpp>
#include "language_detection/LanguageProfiles.h"
#include "NGram.h"
#include "Language.h"
#include "util/fs.h"

using namespace std;
using json = nlohmann::json;

namespace texty { namespace language_detection {

LanguageProfiles::LanguageProfiles(one_gram_map ones,
    two_gram_map twos, three_gram_map threes)
  : oneGrams_(std::move(ones)),
    twoGrams_(std::move(twos)),
    threeGrams_(std::move(threes)) {}

LanguageProfiles::LanguageProfiles(){}

LanguageProfiles::LanguageProfiles(LanguageProfiles &&other) {
  oneGrams_ = std::move(other.oneGrams_);
  twoGrams_ = std::move(other.twoGrams_);
  threeGrams_ = std::move(other.threeGrams_);
}

LanguageProfiles::LanguageProfiles(const LanguageProfiles &other) {
  oneGrams_ = other.oneGrams_;
  twoGrams_ = other.twoGrams_;
  threeGrams_ = other.threeGrams_;
}

LanguageProfiles& LanguageProfiles::operator=(LanguageProfiles &&other) {
  oneGrams_ = std::move(other.oneGrams_);
  twoGrams_ = std::move(other.twoGrams_);
  threeGrams_ = std::move(other.threeGrams_);
  return *this;
}

LanguageProfiles& LanguageProfiles::operator=(const LanguageProfiles &other) {
  oneGrams_ = other.oneGrams_;
  twoGrams_ = other.twoGrams_;
  threeGrams_ = other.threeGrams_;
  return *this;
}

const LanguageProfiles::lang_map& LanguageProfiles::getScores(NGram<uint32_t, 1> ngram) {
  auto found = oneGrams_.find(ngram);
  if (found == oneGrams_.end()) {
    return emptyScores_;
  }
  return found->second;
}

const LanguageProfiles::lang_map& LanguageProfiles::getScores(NGram<uint32_t, 2> ngram) {
  auto found = twoGrams_.find(ngram);
  if (found == twoGrams_.end()) {
    return emptyScores_;
  }
  return found->second;
}

const LanguageProfiles::lang_map& LanguageProfiles::getScores(NGram<uint32_t, 3> ngram) {
  auto found = threeGrams_.find(ngram);
  if (found == threeGrams_.end()) {
    return emptyScores_;    
  }
  return found->second;
}

const LanguageProfiles::lang_map& LanguageProfiles::getEmptyScores() {
  return emptyScores_;
}

void LanguageProfiles::initFromJson(LanguageProfiles *target, const std::string &jsonData) {
  auto data = json::parse(jsonData);
  for (auto gramPair: data[0]) {
    uint32_t x = gramPair[0][0];
    NGram<uint32_t, 1> key {x};
    std::unordered_map<Language, double> langScores;
    for (auto langPair: gramPair[1]) {
      string langName = langPair[0];
      auto lang = languageFromCode(langName);
      double score = langPair[1];
      langScores.insert(std::make_pair(lang, score));
    }
    target->oneGrams_.insert(std::make_pair(
      key, langScores
    ));
  }
  for (auto gramPair: data[1]) {
    uint32_t x = gramPair[0][0];
    uint32_t y = gramPair[0][1];

    NGram<uint32_t, 2> key {x, y};
    std::unordered_map<Language, double> langScores;
    for (auto langPair: gramPair[1]) {
      string langName = langPair[0];
      auto lang = languageFromCode(langName);
      double score = langPair[1];
      langScores.insert(std::make_pair(lang, score));
    }
    target->twoGrams_.insert(std::make_pair(
      key, langScores
    ));
  }
  for (auto gramPair: data[2]) {
    uint32_t x = gramPair[0][0];
    uint32_t y = gramPair[0][1];
    uint32_t z = gramPair[0][2];

    NGram<uint32_t, 3> key {x, y, z};
    std::unordered_map<Language, double> langScores;
    for (auto langPair: gramPair[1]) {
      string langName = langPair[0];
      auto lang = languageFromCode(langName);
      double score = langPair[1];
      langScores.insert(std::make_pair(lang, score));
    }
    target->threeGrams_.insert(std::make_pair(
      key, langScores
    ));
  }  
}

void LanguageProfiles::initFromFile(LanguageProfiles *target, const std::string& fpath) {
  string data;
  util::fs::readFileSync(fpath, data);
  LanguageProfiles::initFromJson(target, data);
}

LanguageProfiles LanguageProfiles::loadFromJson(const std::string& jsonData) {
  LanguageProfiles result;
  LanguageProfiles::initFromJson(&result, jsonData);
  return result;
}

LanguageProfiles LanguageProfiles::loadFromFile(const std::string& fpath) {
  LanguageProfiles result;
  LanguageProfiles::initFromFile(&result, fpath);
  return result;
}


}} // texty::language_detection
