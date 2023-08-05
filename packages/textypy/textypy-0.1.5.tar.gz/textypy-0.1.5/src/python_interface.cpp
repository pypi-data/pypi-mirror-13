#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <vector>
#include "hashing/ConstantSpaceSimHasher.h"
#include "hashing/hash_funcs.h"
#include "util/misc.h"
#include "Language.h"
#include "language_detection/GlobalLanguageDetector.h"
#include "language_detection/GlobalLanguageProfiles.h"

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

void init_global_language_profiles_from_file(std::string fileName) {
  language_detection::GlobalLanguageProfiles::initFromFile(fileName);
}

void init_global_language_profiles_from_json(std::string jsonData) {
  language_detection::GlobalLanguageProfiles::initFromFile(jsonData);
}

void destroy_global_language_profiles() {
  language_detection::GlobalLanguageProfiles::destroy();
}

std::string detect_language(std::string text) {
  language_detection::GlobalLanguageDetector detector;
  auto lang = detector.detect(text, 7);
  return stringOfLanguage(lang);
}

}} // texty::python_interface



namespace py = pybind11;

PYBIND11_PLUGIN(textypy_libtexty) {
    py::module m("textypy_libtexty", "libtexty python interface");

    m.def("simhash", &texty::python_interface::simhash, "Compute simhash score of 2-shingles for given text");
    m.def("rotate_bits", &texty::python_interface::rotate_bits, "Get a vector of rotations of a 64-bit value");
    m.def("hamming_distance", &texty::python_interface::hamming_distance, "Get hamming distance of two 64-bit values");
    m.def("init_global_language_profiles_from_file",
        &texty::python_interface::init_global_language_profiles_from_file,
        "initialize global language detection from a file path, which should contain valid JSON");
    m.def("init_global_language_profiles_from_json",
        &texty::python_interface::init_global_language_profiles_from_json,
        "initialize global language detection profiles from a raw JSON string");
    m.def("destroy_global_language_profiles",
        &texty::python_interface::destroy_global_language_profiles,
        "free memory used by the global language detection profiles");
    m.def("detect_language",
        &texty::python_interface::detect_language,
        "Detect most likely language of UTF-8 or ASCII text.");
    return m.ptr();
}
