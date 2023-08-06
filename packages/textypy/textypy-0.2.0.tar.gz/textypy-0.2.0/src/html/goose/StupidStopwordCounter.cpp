#include "html/goose/StupidStopwordCounter.h"
#include "stopwords/StopwordFilter.h"
#include "string_views/TokenView.h"
#include "Language.h"
#include <string>

using namespace std;

namespace texty { namespace html { namespace goose {

using stemming::Utf8Stemmer;
using string_views::TokenView;

StupidStopwordCounter::StupidStopwordCounter(Language lang,
    shared_ptr<Utf8Stemmer> stemmer)
  : language_(lang), stopwordFilter_(lang), stemmer_(stemmer) {}

size_t StupidStopwordCounter::countStopwords(const string &text) {
  TokenView view(text);
  string currentToken = "";
  const char *beginning = text.c_str();
  size_t count = 0;
  for (auto toke: view) {
    const char *tokenStart = beginning + toke.first;
    if (toke.second <= toke.first) {
      break;
    }
    size_t diff = toke.second - toke.first;
    currentToken.clear();
    const char *it = tokenStart;
    for (size_t i = 0; i < diff; i++) {
      currentToken.push_back(*it);
      it++;
    }
    if (stopwordFilter_.isStopword(currentToken)) {
      count++;
    } else {
      currentToken.erase(stemmer_->getStemPos(currentToken));
      if (stopwordFilter_.isStopword(currentToken)) {
        count++;
      }
    }    

  }
  return count;
}

}}} // texty::html::goose
