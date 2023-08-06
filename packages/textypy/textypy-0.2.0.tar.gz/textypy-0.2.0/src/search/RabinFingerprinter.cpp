#include "search/RabinFingerprinter.h"
#include "string_views/ByteStringWindow.h"

namespace texty { namespace search {

using string_views::ByteStringWindow;

RabinFingerprinter::RabinFingerprinter(uint32_t alpha, uint64_t modN)
  : alpha_(alpha), modN_(modN) {}

uint32_t RabinFingerprinter::alpha() const {
  return alpha_;
}

uint64_t RabinFingerprinter::hash(const char *start, const char *end) const {
  return hash(ByteStringWindow(start, end));
}

uint64_t RabinFingerprinter::hash(const char *start, size_t count) const {
  return hash(ByteStringWindow(start, count));
}

}} // texty::search
