#pragma once

#include <string>
#include "language_detection/LanguageProfiles.h"
#include "language_detection/LanguageDetector.h"
#include "Language.h"

namespace texty { namespace language_detection {

class OwningLanguageDetector: public LanguageDetector<OwningLanguageDetector> {
 protected:
  LanguageProfiles profiles_;
 public:
  OwningLanguageDetector(LanguageProfiles profiles);
  LanguageProfiles* getProfiles();
};

}} // texty::language_detection