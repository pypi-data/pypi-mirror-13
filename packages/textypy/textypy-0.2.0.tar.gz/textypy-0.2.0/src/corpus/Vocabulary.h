#include <unordered_map>
#include <initializer_list>

#include <eigen3/Eigen/SparseCore>
#include <eigen3/Eigen/Dense>

namespace texty { namespace corpus {

template<typename TDocument, typename TTerm>
class Vocabulary {
 public:
  using document_type = TDocument;
  using term_type = TTerm;
  using term_map = std::unordered_map<term_type, std::pair<size_t, size_t>>;
  using dense_float_vector = Eigen::VectorXf;
  using dense_double_vector = Eigen::VectorXd;
  using sparse_float_vector = Eigen::SparseVector<float>;
  using sparse_double_vector = Eigen::SparseVector<double>;
  using init_list = std::initializer_list<typename term_map::value_type>;
 protected:
  term_map terms_;
 public:
  Vocabulary(init_list init)
    : terms_(init) {}
  Vocabulary(const term_map &terms): terms_(terms) {}
  Vocabulary(term_map &&terms): terms_(std::move(terms)) {}
  Vocabulary(const Vocabulary &other): terms_(other.terms_) {}
  Vocabulary(Vocabulary &&other): terms_(std::move(other.terms_)) {}

  bool has(const term_type &term) const {
    return (terms_.count(term) > 0);
  }

  size_t size() const {
    return terms_.size();
  }

  size_t termIndex(const term_type &term) const {
    return terms_[term].first;
  }

  size_t termDf(const term_type &term) const {
    auto found = terms_.find(term);
    if (found == terms_.end()) {
      return 0;
    }
    return found->second;
  }

 protected:
  template<typename TVec, typename TElem>
  TVec vectorizeDenseImpl(const document_type &doc, bool tfidf) const {
    TVec vec = TVec::Zero(size());
    for (auto termScore: doc) {
      auto vocabTerm = terms_.find(termScore.first);
      if (vocabTerm != terms_.end()) {
        TElem score = 0.0;
        if (tfidf) {
          auto df = vocabTerm->second.second;
          score = (TElem) (((double) termScore.second) / ((double) df));
        } else {
          score = (TElem) termScore.second;
        }
        auto idx = vocabTerm->second.first;
        vec(idx) = score;
      }
    }
    return vec;
  }

 public:
  dense_float_vector vectorizeDenseFloat(const document_type &doc) const {
    bool tfidf = false;
    return vectorizeDenseImpl<dense_float_vector, float>(doc, tfidf);
  }

  dense_float_vector vectorizeDenseFloatTfidf(
      const document_type &doc) const {
    bool tfidf = true;
    return vectorizeDenseImpl<dense_float_vector, float>(doc, tfidf);
  }

  dense_double_vector vectorizeDenseDouble(const document_type &doc) const {
    bool tfidf = false;
    return vectorizeDenseImpl<dense_double_vector, double>(doc, tfidf);
  }

  dense_double_vector vectorizeDenseDoubleTfidf(
      const document_type &doc) const {
    bool tfidf = true;
    return vectorizeDenseImpl<dense_double_vector, double>(doc, tfidf);
  }

};

}} // texty::corpus

