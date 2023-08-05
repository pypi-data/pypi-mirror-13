#pragma once
#include "stemming/BaseStemmer.h"
#include "Language.h"

struct sb_stemmer;

namespace texty { namespace stemming {

class Utf8Stemmer: public BaseStemmer {
protected:
  struct sb_stemmer *stemmer_;
  Language language_;
public:
  Utf8Stemmer(Language lang);
  size_t getStemPos(const char *toStem, size_t length) override;
  ~Utf8Stemmer();
};

}} // texty::stemming
