#pragma once
#include <string>
#include <sstream>
#include <glog/logging.h>

namespace texty { namespace util { namespace pretty_print {

template<typename T>
struct PrettyPrinter {
  static void pprint(std::ostringstream &oss, const T& ref) {
    oss << ref;
  }
};

template<typename T>
void prettyPrint(std::ostringstream &oss, const T& ref) {
  PrettyPrinter<T>::pprint(oss, ref);
}

template<typename T>
std::string prettyPrint(const T& ref) {
  std::ostringstream oss;
  prettyPrint(oss, ref);
  return oss.str();
}

}}} // texty::util::pretty_print
