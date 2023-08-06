#pragma once
#include <cstddef>

namespace texty { namespace html { namespace goose {

class GooseOptions {
 protected:
  size_t minBoostStopwords_ {5};
  size_t maxBoostDistance_ {3};
 public:
  size_t minBoostStopwords() const;
  void minBoostStopwords(size_t);
  size_t maxBoostDistance() const;
  void maxBoostDistance(size_t);
};

}}} // texty::html::goose
