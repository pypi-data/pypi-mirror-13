#pragma once
#include "stemming/Utf8Stemmer.h"
#include "Language.h"
#include <memory>
#include <string>
#include <map>

namespace texty { namespace stemming {

class StemmerManagerIf {
 public:
  virtual std::shared_ptr<Utf8Stemmer> getShared(Language lang) = 0;
  virtual Utf8Stemmer* get(Language lang) = 0;
  virtual ~StemmerManagerIf() = default;
};

}} // texty::stemming
