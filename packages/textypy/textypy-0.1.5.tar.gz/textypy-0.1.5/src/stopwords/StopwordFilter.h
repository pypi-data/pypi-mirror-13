#pragma once
#include <string>
#include "Language.h"

namespace texty { namespace stopwords {

class StopwordFilterIf {
 public:
  virtual bool isStopword(
    const std::string &stemmedWord,
    Language language
  ) = 0;
};

class StopwordFilter : public StopwordFilterIf {
 public:
  bool isStopword(
    const std::string &stemmedWord,
    Language language
  ) override;
};


}} // texty::stopwords
