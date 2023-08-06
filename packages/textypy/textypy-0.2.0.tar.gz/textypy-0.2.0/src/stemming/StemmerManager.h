#pragma once
#include "stemming/Utf8Stemmer.h"
#include "stemming/StemmerManagerIf.h"

#include "Language.h"
#include <memory>
#include <string>
#include <map>

namespace texty { namespace stemming {

class StemmerManager: public StemmerManagerIf {
 protected:
  std::map<Language, std::shared_ptr<Utf8Stemmer>> stemmers_;
  std::shared_ptr<Utf8Stemmer>& getOrCreate(Language lang);
 public:
  std::shared_ptr<Utf8Stemmer> getShared(Language lang) override;
  Utf8Stemmer* get(Language lang) override;
};

}} // texty::stemming
