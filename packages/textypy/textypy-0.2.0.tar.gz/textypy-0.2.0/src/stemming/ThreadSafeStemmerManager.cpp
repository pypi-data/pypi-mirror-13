#include "stemming/ThreadSafeStemmerManager.h"

using namespace std;

namespace texty { namespace stemming {

shared_ptr<Utf8Stemmer> ThreadSafeStemmerManager::getShared(Language lang) {
  return localManager_->getShared(lang);
}

Utf8Stemmer* ThreadSafeStemmerManager::get(Language lang) {
  return localManager_->get(lang);
}

}} // texty::stemming
