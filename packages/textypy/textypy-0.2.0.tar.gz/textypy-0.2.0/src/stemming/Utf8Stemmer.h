#pragma once
#include <string>
#include "Language.h"
#include "stemming/SbStemmerWrapper.h"

namespace texty { namespace stemming {

class Utf8Stemmer {
protected:
  Language language_;
  SbStemmerWrapper stemmer_;
public:
  Utf8Stemmer(Language lang);
  size_t getStemPos(const char *toStem, size_t length);
  size_t getStemPos(const std::string&);
};

}} // texty::stemming
