import sys
sys.path.append("./build/lib.macosx-10.10-intel-2.7/")
import python_da
trie = python_da.Trie()
trie.build(["aaa", "ccdded"])
#trie.build("aaa")
print trie.common_prefix_search("aaabbcd")
print trie.exact_match("aaa")

