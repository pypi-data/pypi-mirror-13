#pragma once
#include "stemming/Utf8Stemmer.h"
#include "stemming/StemmerManagerIf.h"
#include "stemming/StemmerManager.h"
#include "Language.h"
#include "util/ThreadLocalPointer.h"
#include <memory>
#include <string>
#include <map>

namespace texty { namespace stemming {

class ThreadSafeStemmerManager: public StemmerManagerIf {
 protected:
  util::ThreadLocalPointer<StemmerManager> localManager_;
 public:
  std::shared_ptr<Utf8Stemmer> getShared(Language) override;
  Utf8Stemmer* get(Language) override;
};

}} // texty::stemming
