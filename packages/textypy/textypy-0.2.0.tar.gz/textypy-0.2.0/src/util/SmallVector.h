#pragma once
#include <array>
#include <vector>
#include <initializer_list>
#include <iterator>
#include "util/macros.h"
#include "util/UniqueNullablePtr.h"

namespace texty { namespace util {

template<typename T, size_t SmallSize = 32>
class SmallVector {
 public:
  static const size_t N = SmallSize;
  using array_type = std::array<T, SmallSize>;
  using vector_type = std::vector<T>;
  using value_type = T;
 protected:
  array_type arrayItems_;
  UniqueNullablePtr<vector_type> vectorItems_;
  size_t lastIndex_ = 0;

  static size_t vectorIndex(size_t index) {
    DEBUG_CHECK(index >= SmallSize);
    return index - SmallSize;
  }
  static bool isArrayIndex(size_t index) {
    return index < SmallSize;
  }
  static bool isVectorIndex(size_t index) {
    return ! isArrayIndex(index);
  }

 public:
  SmallVector(){}
  SmallVector(std::initializer_list<T> items) {
    for (auto item: items) {
      push_back(item);
    }
  }
  SmallVector(const SmallVector &other) {
    arrayItems_ = other.arrayItems_;
    lastIndex_ = other.lastIndex_;
    if (other.isOverflown()) {
      vectorItems_ = other.vectorItems_.deepCopy();
    }
  }
  SmallVector(SmallVector &&other) {
    arrayItems_ = other.arrayItems_;
    lastIndex_ = other.lastIndex_;
    vectorItems_ = std::move(other.vectorItems_);
    other.lastIndex_ = 0;
  }
  SmallVector& operator=(const SmallVector &other) {
    arrayItems_ = other.arrayItems_;
    lastIndex_ = other.lastIndex_;
    if (other.isOverflown()) {
      vectorItems_ = other.vectorItems_.deepCopy();
    }
    return *this;
  }
  SmallVector& operator=(SmallVector &&other) {
    arrayItems_ = other.arrayItems_;
    lastIndex_ = other.lastIndex_;
    vectorItems_ = std::move(other.vectorItems_);
    other.lastIndex_ = 0;
    return *this;
  }

  bool isOverflown() const {
    if (lastIndex_ == 0) {
      return false;
    }
    return SmallVector::isVectorIndex(lastIndex_ - 1);
  }

 protected:
  template<typename T2>
  void doPushBack(T2 elem) {
    if (SmallVector::isArrayIndex(lastIndex_)) {
      arrayItems_[lastIndex_] = elem;
    } else {
      if (!vectorItems_) {
        vectorItems_ = new vector_type; 
      }
      vectorItems_->push_back(elem);
    }
    lastIndex_++;    
  }
 public:

  void push_back(const T& elem) {
    doPushBack(elem);
  }

  void push_back(T&& elem) {
    doPushBack(elem);
  }

  void pop_back() {
    if (isOverflown()) {
      vectorItems_->pop_back();
    }
    lastIndex_--;
  }

  size_t size() const {
    return lastIndex_;
  }

  T& at(size_t idx) {
    if (SmallVector::isArrayIndex(idx)) {
      return arrayItems_[idx];
    }
    DEBUG_CHECK(vectorItems_.good());
    return vectorItems_->at(SmallVector::vectorIndex(idx));
  }

  const T& at(size_t idx) const {
    if (SmallVector::isArrayIndex(idx)) {
      return arrayItems_[idx];
    }
    DEBUG_CHECK(vectorItems_.good());
    return vectorItems_->at(SmallVector::vectorIndex(idx));
  }

  T& operator[](size_t idx) {
    return at(idx);
  }

  const T& operator[](size_t idx) const {
    return at(idx);
  }

  class Iterator;
  class ConstIterator;

  class Iterator: std::iterator<std::forward_iterator_tag, T> {
   public:
    using iterator_category = std::forward_iterator_tag;
    using parent_iter = std::iterator<std::forward_iterator_tag, T>;
    using value_type = typename parent_iter::value_type;
    using difference_type = typename parent_iter::difference_type;
    using pointer = typename parent_iter::pointer;
    using reference = typename parent_iter::reference;


   protected:
    SmallVector *parent_ {nullptr};
    size_t index_ {0};
   public:
    friend class SmallVector;
    friend class ConstIterator;
    Iterator(SmallVector *parent, size_t index)
      : parent_(parent), index_(index) {}
    bool operator!=(const Iterator &other) const {
      return index_ != other.index_;
    }
    bool operator<(const Iterator &other) const {
      return index_ < other.index_;
    }
    T& operator*() const {
      return parent_->at(index_);
    }
    T* operator->() const {
      return &(parent_->at(index_));
    }
    Iterator& operator++() {
      index_++;
      return *this;
    }
    Iterator operator++(int) {
      Iterator result(parent_, index_);
      ++result;
      return result;
    }
  };

  using iterator = Iterator;

  iterator begin() {
    return iterator(this, 0);
  }
  iterator end() {
    return iterator(this, size());
  }

  class ConstIterator: std::iterator<std::forward_iterator_tag, T> {
   public:
    using iterator_category = std::forward_iterator_tag;
    using parent_iter = std::iterator<std::forward_iterator_tag, T>;
    using value_type = typename parent_iter::value_type;
    using difference_type = typename parent_iter::difference_type;
    using pointer = typename parent_iter::pointer;
    using reference = typename parent_iter::reference;

   protected:
    const SmallVector *parent_ {nullptr};
    size_t index_ {0};
   public:
    friend class SmallVector;
    friend class Iterator;
    ConstIterator(const Iterator &iter)
      : parent_(iter.parent_), index_(iter.index_){}
    ConstIterator(const SmallVector *parent, size_t index)
      : parent_(parent), index_(index) {}
    bool operator!=(const ConstIterator &other) const {
      return index_ != other.index_;
    }
    bool operator<(const ConstIterator &other) const {
      return index_ < other.index_;
    }
    const T& operator*() const {
      return parent_->at(index_);
    }
    const T* operator->() const {
      return &(parent_->at(index_));
    }
    ConstIterator& operator++() {
      index_++;
      return *this;
    }
    ConstIterator operator++(int) {
      ConstIterator result(parent_, index_);
      ++result;
      return result;
    }
  };

  using const_iterator = ConstIterator;

  const_iterator begin() const {
    return const_iterator(this, 0);
  }

  const_iterator end() const {
    return const_iterator(this, size());
  }

  const_iterator cbegin() const {
    return const_iterator(this, 0);
  }

  const_iterator cend() const {
    return const_iterator(this, size());
  }

  bool empty() const {
    return size() == 0;
  }

  T& front() {
    return arrayItems_[0];
  }

  const T& front() const {
    return arrayItems_[0];
  }

  T& back() {
    if (isArrayIndex(lastIndex_)) {
      return arrayItems_[SmallSize - 1];
    }
    return vectorItems_->back();
  }

  const T& back() const {
    if (isArrayIndex(lastIndex_)) {
      return arrayItems_[SmallSize - 1];
    }
    return vectorItems_->back();
  }

  iterator insert(const_iterator pos, const T& value) {
    if (pos.index_ >= size()) {
      push_back(value);
      return Iterator(this, size());
    }
    at(pos.index_) = value;
    return Iterator(this, pos.index_ + 1);
  }

  iterator insert(const_iterator pos, size_t count, const T& value) {
    for (size_t i = 0; i < count; i++) {
      pos = insert(pos, value);
    }
    return Iterator(this, pos.index_ + 1);
  }

  template<typename TContainer>
  iterator insert(const_iterator pos,
      typename TContainer::iterator start,
      typename TContainer::iterator end) {
    using container_iter = typename TContainer::iterator;
    for (container_iter it = start; it != end; it++) {
      pos = insert(pos, *it);
    }
    return Iterator(this, pos.index_ + 1);
  }

  template<typename TContainer>
  iterator insert(const_iterator pos,
      typename TContainer::const_iterator start,
      typename TContainer::const_iterator end) {
    using container_iter = typename TContainer::const_iterator;
    for (container_iter it = start; it != end; it++) {
      pos = insert(pos, *it);
    }
    return Iterator(this, pos.index_ + 1);
  }

  std::vector<T> copyToVector() const {
    std::vector<T> result;
    result.reserve(size());
    result.insert(result.begin(), begin(), end());
    return result;
  }

};

}} // texty::util
