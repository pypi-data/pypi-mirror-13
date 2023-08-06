#include "string_views/Utf8Iterator.h"
#include <utf8/unchecked.h>

using namespace std;

namespace texty { namespace string_views {

uint32_t Utf8Iterator::dereference() const {
  return utf8::unchecked::peek_next(position_);
}

}} // texty::string_views
