#pragma once
#include <string>
#include <vector>

#include "util/misc.h"

namespace texty {

enum class Language {
  AF,
  AR,
  BG,
  BN,
  CA,
  CS,
  CY,
  DA,
  DE,
  EL,
  EN,
  ES,
  ET,
  FA,
  FI,
  FR,
  GU,
  HE,
  HI,
  HR,
  HU,
  ID,
  IT,
  JA,
  KN,
  KO,
  LT,
  LV,
  MK,
  ML,
  MR,
  NE,
  NL,
  NO,
  PA,
  PL,
  PT,
  RO,
  RU,
  SK,
  SL,
  SO,
  SQ,
  SV,
  SW,
  TA,
  TE,
  TH,
  TL,
  TR,
  UK,
  UNKNOWN,
  UR,
  VI,
  ZH_CN,
  ZH_TW
};

std::string stringOfLanguage(Language lang);

std::string englishNameOfLanguage(Language lang);

Language languageFromCode(const std::string&);

const std::vector<Language>& getAllLanguages();

} // texty


namespace std {
  template<>
  struct hash<texty::Language> {
    size_t operator()(const texty::Language &val) const {
      return texty::util::hashEnum<texty::Language>(val);
    }
  };
}
