#include <string>
#include "language_detection/GlobalLanguageDetector.h"
#include "language_detection/LanguageDetector.h"
#include "language_detection/LanguageProfiles.h"
#include "language_detection/GlobalLanguageProfiles.h"
#include "Language.h"

namespace texty { namespace language_detection {

LanguageProfiles* GlobalLanguageDetector::getProfiles() {
  return GlobalLanguageProfiles::get();
}

}} // texty::language_detection
