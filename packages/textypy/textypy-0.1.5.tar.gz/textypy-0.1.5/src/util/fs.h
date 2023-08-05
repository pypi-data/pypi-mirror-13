#pragma once
#include <string>

namespace texty { namespace util { namespace fs {

bool readFileSync(const std::string &filePath, std::string &result);

}}} // texty::util::fs
