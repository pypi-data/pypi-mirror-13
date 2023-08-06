#pragma once

#include <regex>
#include <string>
#include "html/Node.h"

namespace texty { namespace html { namespace goose {

class TextCleaner {
 protected:
  std::regex badClasses_;
  bool isBadTextNode(const Node &node);
 public:
  TextCleaner();
  std::string getText(const Node &node);
  size_t getText(const Node &node, std::ostringstream&);
};

}}} // texty::html::goose
