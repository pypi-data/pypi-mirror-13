#include "stemming/BaseStemmer.h"
#include <string>


namespace texty { namespace stemming {

size_t BaseStemmer::getStemPos(const std::string &text) {
  return getStemPos(text.data(), text.size());
}

}} // texty::stemming
