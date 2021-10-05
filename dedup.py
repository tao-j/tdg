# %%
import numpy as np
from pydivsufsort import divsufsort, kasai
from decomp import lpf_simple, lzf, kkp3

from time import time

# filename = "data/openwrt-all"
# filename = "data/mats.img"
# filename = "data/bash-2.0.txt"
tt = time()
# s = np.fromfile(filename, dtype=np.byte)
print("in ", time() - tt)
# s = "A" * 10 + "B" + "A" * 10
s = "How many wood would a woodchuck chuck.".encode("ascii")
# s = "ABCDAABCF"

tt = time()
sa = divsufsort(s)
n = len(s)
print("sa ", time() - tt)

if n < 50:
    tt = time()
    # the last element of lcp is invalid
    lcp = kasai(s, sa)
    print("lcp", time() - tt)
    lcp[1:] = lcp[0:-1]
    lcp[0] = 0

    tt = time()
    isa = np.empty(sa.shape, sa.dtype)
    isa[sa] = np.arange(len(sa), dtype=sa.dtype)
    print("isa", time() - tt)

# tt = time()
# lpf = lpf_simple(lcp, isa)
# print("lpf", time() - tt)
tt = time()
prv, lz, fl = kkp3(s, sa)
print("kkp", time() - tt)

# tt = time()
# lz, fl, nf = lzf(lpf, n)
# print("lzf", time() - tt)


# %%
def prt_spc(arr, fl):
    print(" ", end="")
    for i in range(len(arr)):
        fll = fl[i]
        print("{:3d}".format(arr[i]) + "   " * (max(fll, 1) - 1), end="")
    print(" ", arr.dtype)

print("n =", n)
if n < 50:
    print(">   ", end=" ")
    for c in s:
        print(" {}".format(chr(c)), end=" ")
    if hasattr(s, "dtype"):
        print(s.dtype)
    else:
        print(type(s))
    fmt = {"int": lambda x: "{:3d}".format(x)}
    prt = lambda x : print(
        np.array2string(x, separator="", formatter=fmt, max_line_width=n*3+2), x.dtype)
    
    print("i  ", end=""), prt(np.arange(n))
    print("sa ", end=""), prt(sa)
    print("isa", end=""), prt(isa)
    print("lcp", end=""), prt(lcp)
    # print("lpf", end=""), prt(lpf)
    print("prv", end=""), prt_spc(prv, fl)
    print("lz ", end=""), prt_spc(lz, fl)
    print("fl ", end=""), prt_spc(fl, fl)
    print("nbl ", end=""), print(len(fl))
