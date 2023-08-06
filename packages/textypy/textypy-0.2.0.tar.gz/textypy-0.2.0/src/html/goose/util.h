#pragma once
#include <string>
#include "html/Node.h"

namespace texty { namespace html { namespace goose {

bool hasHighLinkDensity(const Node&, const std::string&);
bool hasHighLinkDensity(const Node&);

}}} // texty::html::goose
