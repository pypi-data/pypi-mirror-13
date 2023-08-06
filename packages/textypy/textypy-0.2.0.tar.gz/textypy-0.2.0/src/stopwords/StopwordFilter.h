#pragma once
#include <string>
#include "stopwords/MultiLanguageStopwordFilter.h"
#include "Language.h"

namespace texty { namespace stopwords {

class StopwordFilterIf {
 public:
  virtual bool isStopword(const std::string &stemmedWord) = 0;
  virtual ~StopwordFilterIf() = default;
};

class StopwordFilter : public StopwordFilterIf {
 protected:
  Language language_;
  MultiLanguageStopwordFilter underlyingFilter_;
 public:
  StopwordFilter(Language lang);
  bool isStopword(const std::string &stemmedWord) override;
};


}} // texty::stopwords
