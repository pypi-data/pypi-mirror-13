#pragma once
#include <type_traits>

namespace texty { namespace util { namespace enum_traits {

template<typename T>
struct enable_if_enum {
  using type = typename std::enable_if<std::is_enum<T>::value>::type;
};

template<typename TEnum,
  typename TIgnore = typename enable_if_enum<TEnum>::type>
auto enumVal(TEnum value) -> typename std::underlying_type<TEnum>::type {
  using underlying = typename std::underlying_type<TEnum>::type;
  return static_cast<underlying>(value);
}

template<typename TEnum,
  typename TIgnore = typename enable_if_enum<TEnum>::type>
size_t enumIndex(TEnum value) {
  size_t result = enumVal<TEnum>(value);
  return result;
}

template<typename T,
  typename TIgnore = typename enable_if_enum<T>::type>
struct max_enum_value;

template<typename T,
  typename TIgnore = typename enable_if_enum<T>::type>
struct enum_size {
  static const size_t value = max_enum_value<T>::value + 1;
};


}}} // texty::util::enum_traits

