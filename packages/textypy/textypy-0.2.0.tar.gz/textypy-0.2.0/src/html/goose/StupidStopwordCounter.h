#pragma once
#include "stopwords/StopwordFilter.h"
#include "stemming/Utf8Stemmer.h"
#include "Language.h"
#include <string>
#include <memory>

namespace texty { namespace html { namespace goose {

class StupidStopwordCounter {
 protected:
  Language language_;
  stopwords::StopwordFilter stopwordFilter_;
  std::shared_ptr<stemming::Utf8Stemmer> stemmer_;
 public:
  StupidStopwordCounter(Language lang, std::shared_ptr<stemming::Utf8Stemmer>);
  size_t countStopwords(const std::string&);
};

}}} // texty::html::goose
