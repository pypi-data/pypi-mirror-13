#include <string>
#include "stemming/Utf8Stemmer.h"
#include "Language.h"

using namespace std;

namespace texty { namespace stemming {

Utf8Stemmer::Utf8Stemmer(Language lang)
  : language_(lang),
    stemmer_(SbStemmerWrapper::create(stringOfLanguage(lang))) {}

size_t Utf8Stemmer::getStemPos(const char *toStem, size_t length) {
  return stemmer_.getStemPos(toStem, length);
}

size_t Utf8Stemmer::getStemPos(const string &text) {
  return stemmer_.getStemPos(text);
}

}} // texty::stemming
