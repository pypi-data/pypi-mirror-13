#pragma once
#include <string>
#include "Language.h"

namespace texty { namespace stopwords {

class MultiLanguageStopwordFilterIf {
 public:
  virtual bool isStopword(
    const std::string &stemmedWord,
    Language language
  ) = 0;
  virtual ~MultiLanguageStopwordFilterIf() = default;
};

class MultiLanguageStopwordFilter : public MultiLanguageStopwordFilterIf {
 public:
  bool isStopword(
    const std::string &stemmedWord,
    Language language
  ) override;
};


}} // texty::stopwords
