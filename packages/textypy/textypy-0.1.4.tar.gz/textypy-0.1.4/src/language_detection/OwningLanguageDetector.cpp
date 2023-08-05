#include <string>
#include "language_detection/OwningLanguageDetector.h"
#include "Language.h"

namespace texty { namespace language_detection {

OwningLanguageDetector::OwningLanguageDetector(LanguageProfiles profiles)
  : profiles_(std::move(profiles)) {}

LanguageProfiles* OwningLanguageDetector::getProfiles() {
  return &profiles_;
}

}} // texty::language_detection