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
#ifndef _DOUBLE_ARRAY_H_
#define _DOUBLE_ARRAY_H_

#include <algorithm>
#include "double_array_internal.hpp"
#include "utf8.hpp"


class DoubleArray {


public:

  int exact_match(const char *str) const {
    return da_.exact_match(str);
  }

  void enumerate(const char *str, std::vector<std::pair<std::string, int> >  &result) const {
    da_.enumerate(str, result);
  }

  void common_prefix_search(const char *str,
                          std::vector<int> &res_len,
                          std::vector<int> &res_id) const {
    da_.common_prefix_search(str, res_len, res_id);
  }

  void common_prefix_search(const char *str, std::vector<std::string> &res) const {
    std::vector<int> res_len, res_id;
    common_prefix_search(str, res_len, res_id);
    for(size_t i = 0; i < res_len.size(); i++){
      res.push_back(std::string(str, res_len[i]));
    }
  }

  bool contains(const char *str) const {
    std::vector<int> res_len;
    std::vector<int> res_id;
    int current_idx = 0;
    int str_len = static_cast<int>(strlen(str));
    while(current_idx < str_len){
      const char *current_ptr = str + current_idx;
      if(*current_ptr == '\0') return false;
      common_prefix_search(current_ptr, res_len, res_id);
      if(res_id.size() > 0) return true;
      current_idx += utf8charlen(*current_ptr);
    }
    return false;
  }

  void extract_all_matched(const char *str,
                           std::vector<int> &res_offset,
                           std::vector<int> &res_len,
                           std::vector<int> &res_id) const {
    std::vector<int> buf_res_len;
    std::vector<int> buf_res_id;
    int current_idx = 0;
    int str_len = static_cast<int>(strlen(str));
    while(current_idx < str_len){
      buf_res_len.clear();
      buf_res_id.clear();

      const char *current_ptr = str + current_idx;
      if(*current_ptr == '\0') break;
      common_prefix_search(current_ptr, buf_res_len, buf_res_id);
      for(size_t i = 0; i < buf_res_len.size(); i++){
        res_offset.push_back(current_idx);
        res_len.push_back(buf_res_len[i]); 
        res_id.push_back(buf_res_id[i]); 
      }
      current_idx += utf8charlen(*current_ptr);
    }
  }

  void extract_all_matched(const char *str, std::vector<std::string> &res) const {
    std::vector<int> res_offset, res_len, res_id;
    extract_all_matched(str, res_offset, res_len, res_id);
    for(size_t i = 0; i < res_offset.size(); i++){
      res.push_back(std::string(str + res_offset[i], res_len[i]));
    }
  }

  bool insert(const char *str, int id = -1) {
    return da_.insert(str, id);
  }

  bool build(std::vector<std::string> words) {
    std::stable_sort(words.begin(), words.end());
    for(std::vector<std::string>::iterator itr = words.begin();
        itr != words.end(); ++itr){
      bool result = da_.insert(itr->c_str());
      if(!result){
        return result;
      }
    }
    return true;
  }

  bool erase(const char *str) {
    return da_.erase(str);
  }

  DoubleArray() : da_() {
  }

  bool save(const char *filename) const {
    return da_.save(filename);
  }

  bool load(const char *filename) {
    return da_.load(filename);
  }


private:
  DoubleArrayInternal da_;
};

#endif /* _DOUBLE_ARRAY_H_ */
