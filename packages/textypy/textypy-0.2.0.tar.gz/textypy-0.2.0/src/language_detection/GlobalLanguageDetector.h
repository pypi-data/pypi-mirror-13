#pragma once

#include <string>
#include "language_detection/LanguageDetector.h"
#include "language_detection/LanguageProfiles.h"
#include "Language.h"

namespace texty { namespace language_detection {

class GlobalLanguageDetector: public LanguageDetector<GlobalLanguageDetector> {
 public:
  LanguageProfiles* getProfiles();
};

}} // texty::language_detection
