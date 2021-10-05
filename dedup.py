# %%
import numpy as np
from pydivsufsort import divsufsort, kasai
import os
from tqdm import tqdm
from decomp import lpf_simple, lzf, kkp3

from time import time
# filename = "data/woodchuck.txt"
# filename = "data/openwrt-all"
# filename = "data/mats.img"
# filename = "data/bash-2.0.txt"
filename = "data/bash-gunzipped.tar"
filename_npz = filename + ".npz"
tt = time()
s = np.fromfile(filename, dtype=np.byte)
print("in ", time() - tt)
# s = "A" * 10 + "B" + "A" * 10
# s = "How many wood would a woodchuck chuck.".encode("ascii")
# s = "ABCDAABCF"
n = len(s)

if os.path.isfile(filename_npz):
    tt = time()
    loaded = np.load(filename_npz)
    sa = loaded["sa"]
    prv= loaded["prv"]
    lz = loaded["lz"]
    fl = loaded["fl"]
    print("npz ", time() - tt)
else:
    tt = time()
    sa = divsufsort(s)

    print("sa ", time() - tt)

    # tt = time()
    # lpf = lpf_simple(lcp, isa)
    # print("lpf", time() - tt)
    tt = time()
    prv, lz, fl = kkp3(s, sa)
    print("kkp", time() - tt)

    np.savez(filename_npz, sa=sa, prv=prv, lz=lz, fl=fl)

# tt = time()
# lz, fl, nf = lzf(lpf, n)
# print("lzf", time() - tt)
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

# %%
nfa = len(fl)
print("nfa = ", nfa)
print("n =", n)

if n < 50:
    def prt_spc(arr, fl):
        print(" ", end="")
        for i in range(len(arr)):
            fll = fl[i]
            print("{:3d}".format(arr[i]) + "   " * (max(fll, 1) - 1), end="")
        print(" ", arr.dtype)

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

if __name__ == "__main__":
    snew = bytearray(s)
    encode_len = 0
    ir = 0
    L = 4
    def GetHumanReadable(size,precision=2):
        suffixes=['B','KB','MB','GB','TB']
        suffixIndex = 0
        while size > 1024 and suffixIndex < 4:
            suffixIndex += 1 #increment the index of the suffix
            size = size/1024.0 #apply the division
        return "%.*f%s"%(precision,size,suffixes[suffixIndex])

    print("4 bytes encoded offset, offset not compressed")
    for i in range(2, 18):
        idx = fl >= 2 ** i
        sz = (n - np.sum(fl[idx]) + np.sum(idx) * 4) 
        print("lzf >={:6d}, ".format(2 ** i),
        sz / n, "|", GetHumanReadable(sz))


    print("4 bytes encoded offset, offset also compressed")
    for i in tqdm(range(nfa)):
        ll = max(1, fl[i])
        snew[encode_len:encode_len+ll] = snew[ir:ir+ll]
        
        if ll < L:
            encode_len += ll
        else:
            # use 4 bytes to denote an offset
            snew[encode_len:encode_len + 4] = int(prv[i]).to_bytes(4, "little")
            encode_len += 4
        ir += ll

    import zlib 
    snew = snew[:encode_len]
    zlib_str = zlib.compress(snew)
    compressed_len = len(zlib_str)
    print(f"lzf >={L:4d} ", (encode_len)/n, "|", GetHumanReadable(encode_len))
    print(f"lzf >={L:4d} + zlib default", (compressed_len)/n, "|", GetHumanReadable(compressed_len))
    
