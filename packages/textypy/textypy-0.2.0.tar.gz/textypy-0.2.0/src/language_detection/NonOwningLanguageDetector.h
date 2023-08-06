#pragma once

#include <string>
#include "language_detection/LanguageDetector.h"
#include "language_detection/LanguageProfiles.h"
#include "Language.h"

namespace texty { namespace language_detection {

class NonOwningLanguageDetector: public LanguageDetector<NonOwningLanguageDetector> {
 protected:
  LanguageProfiles *profiles_;
 public:
  NonOwningLanguageDetector(LanguageProfiles *profiles);
  LanguageProfiles* getProfiles();
};

}} // texty::language_detection