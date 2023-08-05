#include <string>
#include <cstring>
#include <libstemmer.h>
#include "stemming/Utf8Stemmer.h"
#include "Language.h"

namespace texty { namespace stemming {

Utf8Stemmer::Utf8Stemmer(Language lang): language_(lang) {
  auto cCode = stringOfLanguage(language_);
  const char *countryCode = cCode.c_str();
  if (strcmp(countryCode, "UNKNOWN")) {
    countryCode = "en";
  }
  stemmer_ = sb_stemmer_new(countryCode, "UTF_8");
}

size_t Utf8Stemmer::getStemPos(const char *toStem, size_t length) {
  sb_stemmer_stem(stemmer_, (const sb_symbol*) toStem, length);
  return sb_stemmer_length(stemmer_);
}

Utf8Stemmer::~Utf8Stemmer() {
  sb_stemmer_delete(stemmer_);
}

}} // texty::stemming
