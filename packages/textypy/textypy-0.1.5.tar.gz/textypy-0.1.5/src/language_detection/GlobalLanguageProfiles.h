#pragma once
#include <string>
#include "NGram.h"
#include "Language.h"
#include "language_detection/LanguageProfiles.h"


namespace texty { namespace language_detection {

// this is a disgusting singleton class used to ease integration
// with Python.  In C++, it's a lot cleaner to use a `LanguageDetector`,
// which manages the lifetime of its own `LanguageProfiles` instance.
// (and `LanguageDetector` is thread-safe; you only need one.)

class GlobalLanguageProfiles {
 protected:
  static LanguageProfiles** getGlobalPtr();
  GlobalLanguageProfiles() = delete;
 public:
  static bool isInitialized();
  static LanguageProfiles* get();
  static void initFromFile(const std::string&);
  static void initFromJson(const std::string&);
  static void destroy();
};

}} // texty::language_detection
