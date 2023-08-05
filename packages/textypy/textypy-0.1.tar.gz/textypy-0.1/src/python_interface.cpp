#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <vector>
#include "hashing/ConstantSpaceSimHasher.h"
#include "hashing/hash_funcs.h"
#include "util/misc.h"

using namespace std;

namespace texty { namespace python_interface {

uint64_t simhash(const std::string &text, uint64_t seed) {
  hashing::ConstantSpaceSimHasher<1024, 10> hasher([](const std::string &arg, uint64_t sd) {
    return hashing::city_hash_64(arg, sd);
  }, seed);
  return hasher.hash(text);
}

std::vector<uint64_t> rotate_bits(uint64_t value, size_t rotateBy, size_t rotations) {
  std::vector<uint64_t> result;
  result.reserve(1 + rotations);
  for (size_t i = 0; i < rotations; i++) {
    size_t offset = rotateBy * i;
    result.push_back((value << offset) | (value >> offset));
  }
  return result;
}

uint64_t hamming_distance(uint64_t x, uint64_t y) {
  return util::hammingDistance(x, y);
}

}} // texty::python_interface



namespace py = pybind11;

PYBIND11_PLUGIN(textypy) {
    py::module m("textypy", "libtexty python interface");

    m.def("simhash", &texty::python_interface::simhash, "Compute simhash score of 2-shingles for given text");
    m.def("rotate_bits", &texty::python_interface::rotate_bits, "Get a vector of rotations of a 64-bit value");
    m.def("hamming_distance", &texty::python_interface::hamming_distance, "Get hamming distance of two 64-bit values");

    return m.ptr();
}
