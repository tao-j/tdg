# cython: language_level=3, wraparound=False, boundscheck=False
# distutils: language=c++

# lempel-ziv decomp
cimport numpy as np
import numpy as np

ctypedef fused idx_t:
    np.int32_t
    np.int64_t

ctypedef fused dat_t:
    np.uint8_t
    # np.uint16_t
    # np.uint32_t
    # np.uint64_t
    np.int8_t
    # np.int16_t
    # np.int32_t
    # np.int64_t

def lpf_simple(idx_t[::1] lcq not None, idx_t[::1] isa not None):
    cdef idx_t n = len(isa)
    cdef np.ndarray[idx_t, ndim=1] lcp = np.empty_like(isa)
    cdef np.ndarray[idx_t, ndim=1] lpf = np.empty_like(isa)
    cdef np.ndarray[idx_t, ndim=1] pre = np.empty_like(isa)
    cdef np.ndarray[idx_t, ndim=1] nxt = np.empty_like(isa)
    lcp[:] = lcq
    pre[:] = np.arange(-1, n - 1)
    nxt[:] = np.arange(1, n + 1)
    for i in range(n - 1, -1, -1):
        r = isa[i]
        if nxt[r] < n:
            lpf[i] = max(lcp[r], lcp[nxt[r]])
            lcp[nxt[r]] = min(lcp[r], lcp[nxt[r]])
        else:
            lpf[i] = max(lcp[r], 0)
        if pre[r] >= 0:
            nxt[pre[r]] = nxt[r]
        if nxt[r] < n:
            pre[nxt[r]] = pre[r]
    return lpf

def lzf(idx_t[::1] lpf, idx_t n):
    cdef idx_t[:] lz = np.empty_like(lpf)
    cdef idx_t[:] bl = np.empty_like(lpf)
    cdef idx_t i = 0
    while lz[i] < n:
        bl[i] = max(1, lpf[lz[i]])
        lz[i + 1] = lz[i] + bl[i]
        i += 1
    return lz[1:i+1], bl[:i], i
