#pragma once

#include "Language.h"
#include "util/pretty_print_predef.h"

namespace texty { namespace util { namespace pretty_print {

template<>
struct PrettyPrinter<Language> {
  static void pprint(std::ostringstream &oss, const Language &lang) {
    oss << "Language::" << stringOfLanguage(lang);
  }
};

}}} // texty::util::pretty_print
