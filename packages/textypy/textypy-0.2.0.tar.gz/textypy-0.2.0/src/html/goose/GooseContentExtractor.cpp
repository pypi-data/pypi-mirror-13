#include "html/goose/GooseContentExtractor.h"
#include "html/goose/BaseContentExtractor.h"
#include "html/goose/BoostChecker.h"
#include "html/goose/NodeScorer.h"
#include "html/goose/StupidStopwordCounter.h"
#include "html/goose/TextCleaner.h"
#include "html/goose/TextNodeCollector.h"
#include "html/goose/util.h"

using namespace std;

namespace texty { namespace html { namespace goose {

GooseContentExtractor::GooseContentExtractor(){}

GooseContentExtractor::GooseContentExtractor(GooseOptions options)
  : options_(options) {}

string GooseContentExtractor::extract(const HtmlDom &dom, Language lang) {

  using collector_type = TextNodeCollector<
    TextCleaner, StupidStopwordCounter
  >;
  using booster_type = BoostChecker<
    TextCleaner, StupidStopwordCounter
  >;
  using scorer_type = NodeScorer<
    StupidStopwordCounter, collector_type,
    TextCleaner, booster_type
  >;

  StupidStopwordCounter counter(lang, stemmers_.getShared(lang));
  BaseContentExtractor<
    scorer_type, TextCleaner, collector_type,
    StupidStopwordCounter, booster_type
  > baseExtractor;
  return baseExtractor.extract(options_, counter, dom.root());
}

string GooseContentExtractor::extract(const string &htmlStr, Language lang) {
  auto dom = HtmlDom::create(htmlStr);
  return extract(dom, lang);
}

}}} // texty::html::goose
