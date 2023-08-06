#include "string_views/RandomAccessNGramView.h"

using namespace std;

namespace texty { namespace string_views {

RandomAccessNGramView::RandomAccessNGramView(const string &text, RandomAccessUtf8View &&view)
  : text_(text), view_(std::move(view)){}

size_t RandomAccessNGramView::size() {
  return view_.size();
}

RandomAccessNGramView RandomAccessNGramView::create(const string &text) {
  auto view = RandomAccessUtf8View::create(text);
  return RandomAccessNGramView(text, std::move(view));
}


}} // texty::string_views
