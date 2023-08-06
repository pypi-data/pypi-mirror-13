#pragma once
#include "html/Node.h"
#include "html/goose/util.h"
#include <vector>
#include <set>

namespace texty { namespace html { namespace goose {

template<typename TCleaner, typename TStopwordCounter>
class TextNodeCollector {
 protected:
  std::set<Tag> topTags_ {Tag::P, Tag::PRE, Tag::TD};
  TCleaner cleaner_;
  TStopwordCounter &counter_;

 public:
  TextNodeCollector(TStopwordCounter &counter)
    : counter_(counter) {}

  std::vector<Node> collect(const Node &target) {
    std::vector<Node> withText;
    target.dfs([this, &withText](const Node &node) {
      auto tag = node.getTag();
      if (tag != Tag::P && tag != Tag::PRE && tag != Tag::TD) {
        return;
      }
      auto nodeText = cleaner_.getText(node);
      bool highLinks = hasHighLinkDensity(node, nodeText);
      size_t counts = counter_.countStopwords(nodeText);
      if (!highLinks && counts > 2) {
        withText.push_back(node);
      }
    });
    return withText;
  }

};

}}} // texty::html::goose
