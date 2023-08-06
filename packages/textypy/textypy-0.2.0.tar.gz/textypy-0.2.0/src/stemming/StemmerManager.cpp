#include "stemming/Utf8Stemmer.h"
#include "stemming/StemmerManagerIf.h"
#include "stemming/StemmerManager.h"
#include "Language.h"
#include <memory>
#include <string>
#include <map>

using namespace std;

namespace texty { namespace stemming {

shared_ptr<Utf8Stemmer>& StemmerManager::getOrCreate(Language lang) {
  if (stemmers_.count(lang) == 0) {
    stemmers_.insert(std::make_pair(
      lang, std::make_shared<Utf8Stemmer>(lang)
    ));
  }
  return stemmers_[lang];
}

shared_ptr<Utf8Stemmer> StemmerManager::getShared(Language lang) {
  return getOrCreate(lang);
}

Utf8Stemmer* StemmerManager::get(Language lang) {
  return getOrCreate(lang).get();
}

}} // texty::stemming
