#include "language_detection/NonOwningLanguageDetector.h"
#include "language_detection/DetectionRunner.h"
#include "string_views/RandomAccessNGramView.h"
#include "string_views/NGramSampler.h"
#include "randomness/RandomDistribution.h"
#include "Language.h"

using namespace std;

namespace texty { namespace language_detection {

NonOwningLanguageDetector::NonOwningLanguageDetector(LanguageProfiles *profiles)
  : profiles_(profiles) {}

LanguageProfiles* NonOwningLanguageDetector::getProfiles() {
  return profiles_;
}

}} // texty::language_detection