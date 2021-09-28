# lempel-ziv decomp size
import copy
import numpy as np
def lpf_simple(s, sa, lcp, isa):
    n = len(sa)
    lccp = np.zeros(n + 1)
    lccp[:n] = lcp[:]
    lcp = lccp
    lpf = np.empty_like(sa)
    pre = np.arange(-1, n - 1, like=sa)
    nxt = np.arange(1, n + 1, like=sa)
    for i in range(n - 1, -1, -1):
        r = isa[i]
        lpf[i] = max(lcp[r], lcp[nxt[r]])
        lcp[nxt[r]] = min(lcp[r], lcp[nxt[r]])
        if pre[r] >= 0:
            nxt[pre[r]] = nxt[r]
        if nxt[r] < n:
            pre[nxt[r]] = pre[r]
    return lpf

def lzf(lpf, n):
    lz = np.empty_like(lpf)
    bl = np.empty_like(lpf)
    i = 0
    while lz[i] < n:
        bl[i] = max(1, lpf[lz[i]])
        lz[i + 1] = lz[i] + bl[i]
        i += 1
    return lz[1:i+1], bl[:i], i
