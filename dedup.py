# %%
import numpy as np
from pydivsufsort import divsufsort, kasai
from decomp import lpf_simple

from time import time

# filename = "data/openwrt-all"
filename = "data/bash-2.0.txt"
tt = time()
s = np.fromfile(filename, dtype=np.byte)
print("in ", time() - tt)
# s = "A" * 10 + "B" + "A" * 10
# s = "How many wood would a woodchuck chuck."
# s = "ABCDAABCF"

tt = time()
sa = divsufsort(s)
n = len(s)
print("sa ", time() - tt)

tt = time()
# the last element of lcp in invalid
lcp = kasai(s, sa)
print("lcp", time() - tt)
lcp[1:] = lcp[0:-1]
lcp[0] = 0

tt = time()
isa = np.empty(sa.shape, sa.dtype)
isa[sa] = np.arange(len(sa), dtype=sa.dtype)
print("isa", time() - tt)

lpf = lpf_simple(s, sa, lcp, isa)

