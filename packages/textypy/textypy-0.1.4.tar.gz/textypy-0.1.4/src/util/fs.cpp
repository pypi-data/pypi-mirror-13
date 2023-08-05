#include "util/fs.h"
#include <fstream>
#include <streambuf>

using namespace std;

namespace texty { namespace util { namespace fs {

bool readFileSync(const string &filePath, string &result) {
  ifstream ifs {filePath.c_str()};
  ifs.seekg(0, ifs.end);
  result.reserve(ifs.tellg());
  ifs.seekg(0, ifs.beg);
  result.assign(istreambuf_iterator<char>(ifs),
    istreambuf_iterator<char>()
  );
  return true;
}

}}} // texty::util::fs

