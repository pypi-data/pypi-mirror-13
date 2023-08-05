#include <string>
#include "unicode/UnicodeBlock.h"

namespace texty { namespace unicode {

uint32_t normalizeCodePoint(uint32_t codePoint, UnicodeBlock block);
uint32_t normalizeCodePoint(uint32_t codePoint);
bool isLetterPoint(uint32_t cp, UnicodeBlock uBlock);
bool isLetterPoint(uint32_t cp);

}} // texty::unicode
