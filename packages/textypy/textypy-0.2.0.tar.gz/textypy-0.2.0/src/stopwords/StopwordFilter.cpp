#include <string>
#include "stopwords/StopwordFilter.h"
#include "Language.h"

using namespace std;

namespace texty { namespace stopwords {

StopwordFilter::StopwordFilter(Language lang): language_(lang){}

bool StopwordFilter::isStopword(const string &stemmedWord) {
  return underlyingFilter_.isStopword(stemmedWord, language_);
}

}} // texty::stopwords
