#pragma once
#include <string>
#include <memory>
#include "html/GumboOutputWrapper.h"
#include "html/Node.h"

namespace texty { namespace html {

class HtmlDom {
 protected:
  const std::string &text_;
  std::shared_ptr<GumboOutputWrapper> gumboOutput_ {nullptr};
 public:
  HtmlDom(const std::string&, std::shared_ptr<GumboOutputWrapper>);
  static HtmlDom create(const std::string&);
  Node root() const;
};

}} // texty::html
