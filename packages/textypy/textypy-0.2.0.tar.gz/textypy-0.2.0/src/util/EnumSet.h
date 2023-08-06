#pragma once

#include <bitset>
#include <initializer_list>
#include <type_traits>
#include "util/enum_traits.h"

namespace texty { namespace util {

template<typename TEnum,
  size_t NumBits = enum_traits::enum_size<TEnum>::value,
  typename TIgnore = typename enum_traits::enable_if_enum<TEnum>::type>
class EnumSet {
 public:
  using underlying = typename std::underlying_type<TEnum>::type;
  using type = TEnum;
  static const size_t N = NumBits; 
 protected:
  std::bitset<N> bits_;
 public:
  EnumSet(){}
  EnumSet(std::initializer_list<TEnum> init) {
    for (auto item: init) {
      bits_.set(enum_traits::enumIndex(item));
    }
  }
  template<typename TCollection>
  EnumSet(const TCollection &collection) {
    for (TEnum item: collection) {
      bits_.set(enum_traits::enumIndex(item));
    }
  }
  void insert(TEnum val) {
    bits_.set(enum_traits::enumIndex(val));
  }
  bool has(TEnum val) const {
    return bits_.test(enum_traits::enumIndex(val));
  }
  bool hasAny(std::initializer_list<TEnum> vals) const {
    for (auto item: vals) {
      if (has(item)) {
        return true;
      }
    }
    return false;
  }
  template<typename TCollection>
  bool hasAny(const TCollection &collection) const {
    for (TEnum item: collection) {
      if (has(item)) {
        return true;
      }
    }
    return false;
  }
  bool hasAll(std::initializer_list<TEnum> vals) const {
    for (auto item: vals) {
      if (!has(item)) {
        return false;
      }
    }
    return true;
  }
  template<typename TCollection>
  bool hasAll(const TCollection &collection) const {
    for (TEnum item: collection) {
      if (!has(item)) {
        return false;
      }
    }
    return true;
  }
  size_t size() const {
    return bits_.count();
  }
  size_t maxSize() const {
    return NumBits;
  }
};

}} // texty::util
