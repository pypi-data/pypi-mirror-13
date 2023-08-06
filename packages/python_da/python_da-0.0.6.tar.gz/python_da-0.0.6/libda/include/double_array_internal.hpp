// Copyright (C) 2015 Masahiko Higashiyama
//
// Permission is hereby granted, free of charge, to any person obtaining a
// copy of this software and associated documentation files (the "Software"),
// to deal in the Software without restriction, including without limitation
// the rights to use, copy, modify, merge, publish, distribute, sublicense,
// and/or sell copies of the Software, and to permit persons to whom the
// Software is furnished to do so, subject to the following conditions:
//
// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.
//
// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.
#ifndef _DOUBLE_ARRAY_INTERNAL_H_
#define _DOUBLE_ARRAY_INTERNAL_H_
#include <vector>
#include <utility>
#include <algorithm>
#include <stdexcept>
#include <iostream>
#include <fstream>
#ifdef __GLIBCXX__
  #include <tr1/cstdint>
#else
  #include <cstdint>
#endif


class DoubleArrayInternal {
  struct node {
    int base;
    int check;
  };

  int& empty_head() {
    return array_[0].check;
  }

  int& entry_num() {
    return array_[0].base;
  }

  void set_check(int pos, int base, bool overwrite = false){
    if(overwrite && array_[pos].check > 0){
      array_[pos].check = base;
    }else if(pos == empty_head()){
      empty_head() = -array_[pos].check;
      array_[pos].check = base;
    }else{
      int i = empty_head();
      int n = static_cast<int>(array_.size());
      while(i < n){
        if(pos == -array_[i].check) break;
        i = -array_[i].check;
      }
      if(i >= n) throw std::runtime_error("failed set check");
      array_[i].check = array_[pos].check;
      array_[pos].check = base;
    }
  }

  void delete_check(int pos){
    if(pos < empty_head()){
      array_[pos].check = -empty_head();
      empty_head() = pos;
    }else{
      int i = empty_head();
      int n = static_cast<int>(array_.size());
      while(i < n){
        if(i < pos && pos < -array_[i].check) break;
        i = -array_[i].check;
      }
      if(i >= n) throw std::runtime_error("failed delete check");
      array_[pos].check = array_[i].check;
      array_[i].check = -pos;
    }
  }

  void expand(size_t pos){
    if(pos < array_.size()) return;
    int i = static_cast<int>(array_.size());
    size_t n = array_.capacity();
    while(pos > n) n <<= 1;
    array_.reserve(n);
    array_.resize(pos+1);
    for(; i <= static_cast<int>(pos); i++){
      array_[i].check = -(i+1);
    }
  }

  std::pair<int,const char *> fetch(const char *str) const {
    const char *p = str;
    int state = 1;
    while(1){
      unsigned char c = *p;
      int t = array_[state].base + c;
      //printf("%d %d %d %c %d\n",
      //state, t, array_[state].base, c, array_[t].check);
      if(t < static_cast<int>(array_.size()) && array_[t].check == state){
        if(c == 0) return std::make_pair(state, p);
        state = t;
        ++p;
      }else{
        return std::make_pair(-state, p);
      }
    }
  }

  void get_labels(int index, int base, std::vector<unsigned char> &labels) const {
    size_t maxlen = std::min(static_cast<int>(array_.size()), base + 256);
    for(size_t i = base; i < maxlen; i++){
      if(array_[i].check == index){
        labels.push_back(i - base);
      }
    }
  }

  int find_base(const std::vector<unsigned char> &codes, unsigned char c){
    int base_cand;
    int empty_index = empty_head();
    while(1){
      expand(empty_index);
      base_cand = empty_index - c;
      if(base_cand <= 1){
        empty_index = -array_[empty_index].check;
        continue;
      }
      bool found = true;
      for(size_t i = 0; i < codes.size(); i++){
        expand(base_cand + codes[i]);
        if(array_[base_cand + codes[i]].check > 0){
          found = false;
          break;
        }
      }
      if(found) break;
      empty_index = -array_[empty_index].check;
    }
    return base_cand;
  }

  void move_to(int from, int from_base, int to){
    //printf("copy base[%d] = from %d\n", to, from_base);
    array_[to].base = from_base;
    if(from_base > 0){
      std::vector<unsigned char> trans;
      get_labels(from, from_base, trans);
      for(size_t j = 0; j < trans.size(); j++){
        //printf("move from check[%d](%c) = %d\n",
        //from_base + trans[j], trans[j], to);
        set_check(from_base + trans[j], to, true);
      }
    }
    //printf("init from address %d %d %d\n",
    //from, array_[from].base, from_base);
    array_[from].base = 0;
    delete_check(from);
  }

  void _insert(const char *str, int base, int id){
    int pos = array_[base].base + static_cast<unsigned char>(*str);
    expand(std::max(base,pos));
    if(array_[base].base == 0 || array_[pos].check >= 0){ //conflict
      int oldbase = array_[base].base;
      std::vector<unsigned char> codes;
      if(oldbase > 0) get_labels(base, oldbase, codes);
      int base_cand = find_base(codes, *str);
      //printf("set base base[%d] = %d\n", base, base_cand);
      array_[base].base = base_cand;
      std::vector<int> from,from_base;
      for(size_t i = 0; i < codes.size(); i++){
        int old_t = oldbase + codes[i];
        from.push_back(old_t);
        from_base.push_back(array_[old_t].base);
        //printf("move check check[%d](%c) = %d\n",
        //base_cand + codes[i], codes[i], base);
        set_check(base_cand + codes[i], base);
      }
      for(size_t i = 0; i < from.size(); i++){
        move_to(from[i], from_base[i], base_cand + codes[i]);
      }
      pos = base_cand + static_cast<unsigned char>(*str);
    }
    //printf("set check check[%d](%c) = %d\n", pos, *str, base);
    set_check(pos, base);
    if(*str != '\0'){
      _insert(str+1, pos, id);
    }else{
      if(id < 1){
        array_[pos].base = -(entry_num() + 1);
      }else{
        array_[pos].base = -id;
      }
      entry_num() += 1;
    }
  }

  void _erase(const char *str, int index, const char *p){
    int newbase = array_[index].check;
    delete_check(array_[index].base+*p);
    std::vector<unsigned char> labels;
    get_labels(index, array_[index].base, labels);
    if(labels.size() == 0 && str != p)
      _erase(str, newbase, --p);
  }

  /* For DEBUG */
  void print_array() const {
    std::cout << "[";
    for(size_t i = 0; i < array_.size(); i++){
      std::cout << "element " << i << ":" << array_[i].base << ":" << array_[i].check << std::endl;
    }
    std::cout << "]" << std::endl;
  }

  void _enumerate(int current_idx,
                  std::vector<unsigned char> &path,
                  std::vector<std::pair<std::string, int> >  &result) const {
    std::vector<unsigned char> labels;
    get_labels(current_idx, array_[current_idx].base, labels);
    for(std::vector<unsigned char>::iterator itr = labels.begin(); itr != labels.end(); ++itr){
       int new_idx = array_[current_idx].base + *itr;
       if(*itr == '\0'){
         std::string res;
         res.reserve(path.size());
         for(std::vector<unsigned char>::iterator jtr = path.begin(); jtr != path.end(); ++jtr){
           res += static_cast<char>(*jtr);
         }
         result.push_back(std::make_pair(res, -array_[new_idx].base));
       }else{
         path.push_back(*itr);
         _enumerate(new_idx, path, result);
         path.pop_back();
       } 
    }
  }

public:

  int exact_match(const char *str) const {
    std::pair<int, const char*> state = fetch(str);
    if(state.first > 0){
      int t = array_[state.first].base + static_cast<unsigned char>(*state.second);
      return -array_[t].base;
    }
    return -1;
  }

  void enumerate(const char *str, std::vector<std::pair<std::string, int> >  &result) const {
    int index = 1;
    if(str[0] != '\0'){
      std::pair<int, const char*> state = fetch(str);
      if(state.first > 0){
        index = state.first;
      }else{
        index = -state.first;
      }
    }
    std::vector<unsigned char> path;
    for(const char *p = str; *p != '\0'; p++){
      path.push_back(static_cast<unsigned int>(*p));
    }
    _enumerate(index, path, result);
  }

  void common_prefix_search(const char *str,
                          std::vector<int> &res_len,
                          std::vector<int> &res_id) const {
    const char *p = str;
    int state = 1;
    while(1){
      int t = array_[state].base;
      if(state != 1 && t < static_cast<int>(array_.size()) && array_[t].check == state){
        res_len.push_back(static_cast<int>(std::distance(str,p)));
        res_id.push_back(-array_[t].base);
      }
      unsigned char c = *p;
      if(t+c < static_cast<int>(array_.size()) && array_[t+c].check == state){
        if(c == 0) return;
        state = t+c;
        ++p;
      }else{
        return;
      }
    }
  }

  bool insert(const char *str, int id = -1){
    std::pair<int,const char*> state = fetch(str);
    if(state.first > 0){
      //printf("insert failed %s, Found.", str);
      return false;
    }
    //printf("insert %s", str);
    _insert(state.second, -state.first, id);
    return true;
  }


  bool erase(const char *str){
    std::pair<int,const char*> state = fetch(str);
    if(state.first < 0){
      //printf("erase failed %s, Not Found.", str);
      return false;
    }
    //printf("erase %s", str);
    _erase(str, state.first, state.second);

    return true;
  }

  DoubleArrayInternal() : array_(2) {
    entry_num() = 0;
    empty_head() = 1;
    array_[1].check = -2;
    expand(8192);
  }

  bool save(const char *filename) const {
    std::ofstream ofs(filename, std::ios::binary);
    if(!ofs){
      return false;
    }
    bool result = save(ofs);
    ofs.close();
    if(ofs.fail()) return false;
    return result;
  }

  bool save(std::ostream &os) const {
    int32_t *buffer = new int32_t[array_.size() * 2];
    for(size_t i = 0; i < array_.size(); i++){
      buffer[i * 2] = static_cast<int32_t>(array_[i].base);
      buffer[i * 2 + 1] = static_cast<int32_t>(array_[i].check);
    }
    os.write(reinterpret_cast<const char *>(buffer),
             2 * array_.size() * sizeof(int32_t));
    delete[] buffer;
    if(os.fail()) return false;
    return true;
  }

  bool load(const char *filename) {
    std::ifstream ifs(filename, std::ios::binary);
    if(!ifs){
      return false;
    }
    bool result = load(ifs);
    if(ifs.fail()) return false;
    return result;
  }

  bool load(std::istream &is){
    size_t siz_ = static_cast<size_t>(is.seekg(0,std::ios::end).tellg());
    if(is.fail()) return false;
    array_.resize(siz_ / (sizeof(int32_t) * 2));
    is.seekg(0, std::ios::beg);
    if(is.fail()) return false;
    int32_t *buffer = new int32_t[array_.size() * 2];
    is.read(reinterpret_cast<char *>(buffer), 2 * array_.size() * sizeof(int32_t));
    for(size_t i = 0; i < array_.size(); i++){
      array_[i].base = static_cast<int>(buffer[i * 2]);
      array_[i].check = static_cast<int>(buffer[i * 2 + 1]);
    }
    delete buffer;
    if(is.fail() && !is.eof()) return false;
    return true;
  }

private:
  std::vector<node> array_;
};

#endif /* _DOUBLE_ARRAY_INTERNAL_H_ */
