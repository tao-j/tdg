# %%
import numpy as np
from pydivsufsort import divsufsort, kasai
from decomp import lpf_simple, lzf

from time import time

# filename = "data/openwrt-all"
filename = "data/bash-2.0.txt"
tt = time()
s = np.fromfile(filename, dtype=np.byte)
print("in ", time() - tt)
# s = "A" * 10 + "B" + "A" * 10
s = "How many wood would a woodchuck chuck."
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

tt = time()
lpf = lpf_simple(s, sa, lcp, isa)
print("lpf", time() - tt)

tt = time()
lz, bl, nbl = lzf(lpf, n)
print("lzf", time() - tt)


# %%
print("n =", n)
if n < 50:
    
    print(">", end="")
    for c in s:
        print("  {}".format(c), end="")
    print("")
    fmt = {"int": lambda x: "{:3d}".format(x)}
    prt = lambda x : print(
        np.array2string(x, separator="", formatter=fmt, max_line_width=n*3+2))
    prt(sa)
    prt(isa)
    prt(lcp)
    prt(lpf)
    prt(lz)
    prt(bl)
    print(nbl)

# %%
