#pragma once
#include <tuple>
#include <vector>
#include <string>

namespace texty { namespace hashing {

uint64_t city_hash_64(const char* ptr, size_t textLen, uint64_t seed);
uint64_t city_hash_64(const char* ptr, size_t textLen);
uint64_t city_hash_64(const std::string&, uint64_t seed);
uint64_t city_hash_64(const std::string&);
std::pair<uint64_t, uint64_t> city_hash_128(const char *ptr, size_t textLen);
std::pair<uint64_t, uint64_t> city_hash_128(const char *ptr, size_t textLen, std::pair<uint64_t, uint64_t> seed);
std::pair<uint64_t, uint64_t> city_hash_128(const std::string&);
std::pair<uint64_t, uint64_t> city_hash_128(const std::string&, std::pair<uint64_t, uint64_t> seed);
uint64_t city_128_to_64(std::pair<uint64_t, uint64_t>);
uint64_t city_128_to_64(uint64_t, uint64_t);

uint32_t murmur3_32(const char *ptr, size_t textLen);
uint32_t murmur3_32(const char *ptr, size_t textLen, uint32_t seed);
uint32_t murmur3_32(const std::string&);
uint32_t murmur3_32(const std::string&, uint32_t seed);
std::pair<uint64_t, uint64_t> murmur3_128(const char *ptr, size_t textLen);
std::pair<uint64_t, uint64_t> murmur3_128(const char *ptr, size_t textLen, uint32_t seed);
std::pair<uint64_t, uint64_t> murmur3_128(const std::string&);
std::pair<uint64_t, uint64_t> murmur3_128(const std::string&, uint32_t seed);

// stolen from boost::hash
size_t hashCombine(size_t seed, size_t hashedVal);

}} // texty::hashing
