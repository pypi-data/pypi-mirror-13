#include "Language.h"
#include <string>

namespace texty {

std::string stringOfLanguage(Language lang) {
  switch(lang) {
    case Language::AF : return "af";
    case Language::AR : return "ar";
    case Language::BG : return "bg";
    case Language::BN : return "bn";
    case Language::CA : return "ca";
    case Language::CS : return "cs";
    case Language::CY : return "cy";
    case Language::DA : return "da";
    case Language::DE : return "de";
    case Language::EL : return "el";
    case Language::EN : return "en";
    case Language::ES : return "es";
    case Language::ET : return "et";
    case Language::FA : return "fa";
    case Language::FI : return "fi";
    case Language::FR : return "fr";
    case Language::GU : return "gu";
    case Language::HE : return "he";
    case Language::HI : return "hi";
    case Language::HR : return "hr";
    case Language::HU : return "hu";
    case Language::ID : return "id";
    case Language::IT : return "it";
    case Language::JA : return "ja";
    case Language::KN : return "kn";
    case Language::KO : return "ko";
    case Language::LT : return "lt";
    case Language::LV : return "lv";
    case Language::MK : return "mk";
    case Language::ML : return "ml";
    case Language::MR : return "mr";
    case Language::NE : return "ne";
    case Language::NL : return "nl";
    case Language::NO : return "no";
    case Language::PA : return "pa";
    case Language::PL : return "pl";
    case Language::PT : return "pt";
    case Language::RO : return "ro";
    case Language::RU : return "ru";
    case Language::SK : return "sk";
    case Language::SL : return "sl";
    case Language::SO : return "so";
    case Language::SQ : return "sq";
    case Language::SV : return "sv";
    case Language::SW : return "sw";
    case Language::TA : return "ta";
    case Language::TE : return "te";
    case Language::TH : return "th";
    case Language::TL : return "tl";
    case Language::TR : return "tr";
    case Language::UK : return "uk";
    case Language::UNKNOWN : return "UNKNOWN";
    case Language::UR : return "ur";
    case Language::VI : return "vi";
    case Language::ZH_CN : return "zh_cn";
    case Language::ZH_TW : return "zh_tw";
    default : return "NOT_RECOGNIZED";
  }
}

std::string englishNameOfLanguage(Language lang) {
  switch (lang) {
    case Language::AR : return "Arabic";
    case Language::DE : return "German";
    case Language::EN : return "English";
    case Language::ES : return "Spanish";
    case Language::FR : return "French";
    case Language::IT : return "Italian";
    case Language::RU : return "Russian";
    default           : return "UNKNOWN";
  }
}

} // texty