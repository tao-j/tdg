# %%
import numpy as np
import os
import math
from tqdm import tqdm
from decomp import lpf_simple, lzf, kkp3
from pydivsufsort import divsufsort, kasai
from time import time

# filename = "data/woodchuck.txt"
# filename = "data/test.txt"
# filename = "data/openwrt.img"
# filename = "data/mats.img"
# filename = "data/bash-2.0.txt"
filename = "data/bash-gunzipped.tar"
# filename = "data/grch38.1"
# filename = "openwrt-all.bmp"
# filename = "data/enwik9"
# filename = "data/GRCh38_latest_genomic.fna"
filename_npz = filename + ".npz"
filename_dict = filename + ".dict"
filename_papr = filename + ".papr"
filename_pafl = filename + ".pafl"
tt = time()
s = np.fromfile(filename, dtype=np.uint8)
print("in ", time() - tt)
# s = "A" * 10 + "B" + "A" * 10
# s = "How many wood would a woodchuck chuck.".encode("ascii")
# s = "ABCDAABCF"
n = len(s)

if False and os.path.isfile(filename_npz):
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
    # tt = time()
    # lz, fl, nfa = lzf(lpf, n)
    # print("lzf", time() - tt)

    tt = time()
    prv, lz, fl = kkp3(s, sa) # previous occurence index, -1 for none, lz, fl is the factor length
    print("kkp", time() - tt)

    np.savez(filename_npz, sa=sa, prv=prv, lz=lz, fl=fl)


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
    # copied from stackoverflow
    def GetHumanReadable(size, precision=2):
        suffixes=['B','KiB','MiB','GiB','TiB']
        suffixIndex = 0
        while size > 1024 and suffixIndex < 4:
            suffixIndex += 1 # increment the index of the suffix
            size = size / 1024.0 # apply the division
        return "%.*f%s" % (precision,size,suffixes[suffixIndex])

    tmp = np.floor(np.log2(np.maximum(1, prv + 1))) * 2 + 1
    prv_b = np.sum(tmp) / 8.
    tmp = np.floor(np.log2(np.maximum(1, fl + 1))) * 2 + 1
    fl_b  = np.sum(tmp) / 8.
    for i in range(1, 17):
        idx = fl >= 2 ** i
        sz = n - np.sum(fl[idx])

        print("lzf >={:6d}, ".format(2 ** i), #sz / n,
         "| <= ", GetHumanReadable(sz + prv_b + fl_b))

    prv.tofile(open(filename_papr, "wb"))
    fl.tofile(open(filename_pafl, "wb"))
    print("saved papr papl")

    last_char_fn = np.argmax(np.cumsum(prv == -1)) # argmax returns the first occurence
    ii = 0
    od = []
    odi = 0
    od = np.empty(dtype=np.byte, shape=(256, ))
    for i in range(last_char_fn + 1):
        if prv[i] == -1:
            od[odi] = s[ii]
            odi += 1
        ii += max(1, fl[i])

    od = od[:odi]
    # print(od)
    print(odi, " od size. aka size of alphabet")
    with open(filename_dict, "wb") as out_d:
        od.tofile(out_d)
        out_d.close()


    import lzma, zlib
    for cmpr in [zlib]:
        print("compressing pointers and factor/chuck/block length info")
        len_pr = len(cmpr.compress(prv))
        len_fl = len(cmpr.compress(fl))
        print(cmpr.__name__, "can save prv", GetHumanReadable(prv_b - len_pr))
        print(cmpr.__name__, "can save fl ", GetHumanReadable(fl_b  - len_fl))

    # %%
    od = np.fromfile(open(filename_dict, "rb"), dtype=np.uint8)
    prv = np.fromfile(open(filename_papr, "rb"), dtype=np.int32)
    fl  = np.fromfile(open(filename_pafl, "rb"), dtype=np.int32)
    ss = np.empty_like(s)
    odi = 0
    ll = 0
    for i in tqdm(range(len(prv))):
        if prv[i] == -1:
            ss[ll] = od[odi]
            ll += 1
            odi += 1
        else:
            # if there are repeated content readches the end of the recovered string, copy one byte at a time
            # for example consider the case that s = "llllllllll"
            if prv[i] + fl[i] > ll:
                for fli in range(fl[i]):
                    ss[ll + fli] = ss[prv[i] + fli]
            else:
                ss[ll:ll+fl[i]] = ss[prv[i]:prv[i]+fl[i]]
            ll += fl[i]

    print("hash of orig and recovered string")
    import hashlib
    for st in [s, ss]:
        m = hashlib.sha256()
        m.update(st.data)
        print(m.hexdigest())
        # print(st)
