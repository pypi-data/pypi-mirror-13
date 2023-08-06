#include "cleaning/basic.h"
#include "string_views/Utf8View.h"
#include <map>
#include <array>
#include <utf8/unchecked.h>
using namespace std;

static const map<uint32_t, uint32_t> singleUnicodeReplacements {
  {8220, 34}, // unicode lquote to quote
  {8221, 34}, // unicode rquote to quote
  {8216, 39}, // unicode l singlequote to singlequote
  {8217, 39}, // unicode r singlequote to singlequote
  {8291, 32}, // a space-like thing with a real space
  {8229, 32}, // a space-like thing with a real space
  {160,  32}, // a space-like thing with a real space
  {8226, 45}, // bullet with dash
  {9679, 45}, // large bullet with dash
  {8210, 45}, // long dash with dash
  {8211, 45}, // long dash with dash
  {8212, 45}, // long dash with dash
  {8213, 45}, // long dash with dash
  {8275, 45}, // long dash with dash
  {11834, 45}, // long dash with dash
  {11835, 45} // long dash with dash
};

namespace texty { namespace cleaning {

static const uint32_t SPACE = 32;
static const uint32_t CARRIAGE_RETURN = 13;
static const uint32_t NEW_LINE = 10;

string basicClean(const string &text) {
  string result;
  result.reserve(text.size());
  auto iter = std::back_inserter(result);
  string_views::Utf8View view(text);
  array<uint32_t, 2> prevPoints;
  for (size_t i = 0; i < 2; i++) {
    prevPoints[i] = 0;
  }
  for (auto cp: view) {
    if (cp == 160 || (cp > 8000 && cp < 12000)) {
      auto replacement = singleUnicodeReplacements.find(cp);
      if (replacement != singleUnicodeReplacements.end()) {
        cp = replacement->second;
      }
    }
    if (prevPoints[1] == CARRIAGE_RETURN && cp != NEW_LINE) {
      iter = utf8::unchecked::append(NEW_LINE, iter);
      prevPoints[0] = prevPoints[1];
      prevPoints[1] = NEW_LINE;
    }
    if (cp == SPACE) {
      if (prevPoints[1] != SPACE) {
        iter = utf8::unchecked::append(cp, iter);
      }
    } else if (cp == NEW_LINE) {
      if (prevPoints[0] != NEW_LINE) {
        iter = utf8::unchecked::append(cp, iter);
      }
    } else {
      iter = utf8::unchecked::append(cp, iter);
    }
    prevPoints[0] = prevPoints[1];
    prevPoints[1] = cp;
  }
  return result;
}

}} // texty::cleaning
