# lempel-ziv decomp size
import copy
import numpy as np
def lpf_simple(s, sa, lcp, isa):
    n = len(sa)
    lccp = np.zeros(n + 1)
    lccp[:n] = lcp[:]
    lcp = lccp
    pre = [0] * n
    nxt = [0] * n
    lpf = [0] * n
    for r in range(n):
        pre[r] = r - 1
        nxt[r] = r + 1
    for i in range(n-1, -1, -1):
        # print(i)
        r = isa[i]
        # print(lcp[r])
        # print('a ', lcp[nxt[r]])
        lpf[i] = max(lcp[r], lcp[nxt[r]])
        lcp[nxt[r]] = min(lcp[r], lcp[nxt[r]])
        if pre[r] >= 0:
            nxt[pre[r]] = nxt[r]
        if nxt[r] < n:
            pre[nxt[r]] = pre[r]
    return lpf

def lzf(lpf, n):
    lz = np.zeros(n, dtype=np.int64)
    bl = np.zeros(n, dtype=np.int64)
    i = 0
    while lz[i] < n:
        bl[i] = max(1, lpf[lz[i]])
        lz[i + 1] = lz[i] + bl[i]
        i += 1
    return lz, bl, i

# lz, bl, fin = lzf(lpf, n)
# print(lz[:fin])
# print(bl[:fin])