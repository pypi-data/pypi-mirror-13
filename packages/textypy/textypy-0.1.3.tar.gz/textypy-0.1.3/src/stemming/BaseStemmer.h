#pragma once
#include <string>

namespace texty { namespace stemming {

class BaseStemmer {
 public:
  virtual size_t getStemPos(const char *base, size_t length) = 0;
  virtual size_t getStemPos(const std::string &text);
  virtual ~BaseStemmer() = default;
};

}} // texty::stemming
