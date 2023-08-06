#include <unordered_map>
#include <map>
#include <string>

#include "NGram.h"
#include "Language.h"
#include "language_detection/GlobalLanguageProfiles.h"
#include "language_detection/LanguageProfiles.h"


namespace texty { namespace language_detection {

LanguageProfiles** GlobalLanguageProfiles::getGlobalPtr() {
  static LanguageProfiles *globalPtr {nullptr};
  return &globalPtr; 
}

LanguageProfiles* GlobalLanguageProfiles::get() {
  return *(getGlobalPtr());
}

bool GlobalLanguageProfiles::isInitialized() {
  return !!GlobalLanguageProfiles::get();
}

void GlobalLanguageProfiles::initFromFile(const std::string& fpath) {
  if (isInitialized()) {
    return;
  }
  LanguageProfiles **ptrPtr = GlobalLanguageProfiles::getGlobalPtr();
  *ptrPtr = new LanguageProfiles;
  LanguageProfiles::initFromFile(*ptrPtr, fpath);
}

void GlobalLanguageProfiles::initFromJson(const std::string& jsonData) {
  if (isInitialized()) {
    return;
  }
  LanguageProfiles **ptrPtr = GlobalLanguageProfiles::getGlobalPtr();
  *ptrPtr = new LanguageProfiles;
  LanguageProfiles::initFromJson(*ptrPtr, jsonData);
}

void GlobalLanguageProfiles::destroy() {
  auto ptrPtr = getGlobalPtr();
  if ((*ptrPtr) == nullptr) return;
  delete *ptrPtr;
  *ptrPtr = nullptr;
}

}} // texty::language_detection
