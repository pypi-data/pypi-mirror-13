#pragma once
#include <cassert>

#ifndef NDEBUG
  #define DEBUG_CHECK(x) assert(x)
#else
  #define DEBUG_CHECK(x)
#endif
