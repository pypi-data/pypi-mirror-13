#include "util/misc.h"
#include <set>

using namespace std;

namespace texty { namespace util {

static const set<char> punctuation {
  '.', '"', '!', '/', '\\', ':', '?', '@', '[', ']', '(', ')', '{', '}', '#', '$', '%', '^', '&',
  ';', ','
};

bool isAsciiPunctuation(char c) {
  return punctuation.count(c) > 0;
}

}} // texty::util
 