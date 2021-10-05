# cython: language_level=3, wraparound=True, boundscheck=True
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

ctypedef fused bytea_t:
    const unsigned char
    # np.uint16_t
    # np.uint32_t
    # np.uint64_t
    const signed char
    # np.int16_t
    # np.int32_t
    # np.int64_t

# Maxime Crochemore, Lucian Ilie, Costas S. Iliopoulos, Marcin Kubica, Wojciech Rytter, et al.. LPF computation revisited. IWOCA, 2009, Czech Republic. pp.158-169. hal-00741881
def lpf_simple(idx_t[::1] lcq not None, idx_t[::1] isa not None):
    cdef idx_t n = len(isa)
    cdef np.ndarray[idx_t, ndim=1] lcp = np.empty_like(isa)
    cdef np.ndarray[idx_t, ndim=1] lpf = np.empty_like(isa)
    cdef np.ndarray[idx_t, ndim=1] pre = np.empty_like(isa)
    cdef np.ndarray[idx_t, ndim=1] nxt = np.empty_like(isa)
    # cdef idx_t[:] pre = np.arange(-1, n - 1, dtype=isa.dtype)
    # cdef idx_t[:] nxt = np.arange(1, n + 1, dtype=isa.dtype)
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
    return lz[:i], bl[:i], i

# Linear Time Lempel-Ziv Factorization: Simple, Fast, Small, Juha K ̈arkk ̈ainen, Dominik Kempa, and Simon J. Puglisi
def kkp3(bytea_t[::1] X not None, idx_t[::1] sa not None):
    cdef idx_t n = len(sa)
    cdef np.ndarray[idx_t, ndim=1] lz = np.empty_like(sa)
    cdef np.ndarray[idx_t, ndim=1] fl = np.empty_like(sa)
    cdef np.ndarray[idx_t, ndim=1] prv = np.empty_like(sa)
    cdef np.ndarray[idx_t, ndim=1] SA = np.empty_like(sa, shape=(len(sa) + 2, ))

    cdef idx_t i, psv, nsv, nfactors
    cdef idx_t pos, ll

    if n == 0:
        return np.array([]), np.array([]), np.array([])
    # cdef idx_t *CPSS = new idx_t[2 * n + 5]
    cdef np.ndarray[idx_t, ndim=1] CPSS = np.empty_like(sa, shape=(2 * len(sa) + 5, ))
    
    for i in range(n, -1, -1):
        SA[i] = sa[i - 1]
    SA[0] = SA[n + 1] = -1

    cdef idx_t top = 0
    cdef idx_t addr
    for i in range(1, n + 2):
        while SA[top] > SA[i]:
            addr = (SA[top] << 1)
            CPSS[addr] = SA[top - 1]
            CPSS[addr + 1] = SA[i]
            top -= 1
        top += 1
        SA[top] = SA[i]

    prv[0] = -1
    lz[0] = 0
    fl[0] = 0
    i = 1
    nfactors = 1
    while i < n:
        addr = (i << 1)
        psv = CPSS[addr]
        nsv = CPSS[addr + 1]

        # inline of parse_phrase
        pos = ll = 0
        if nsv == -1:
            while X[psv + ll] == X[i + ll]:
                ll += 1
            pos = psv
        elif psv == -1:
            while i + ll < n and X[nsv + ll] == X[i + ll]:
                ll += 1
            pos = nsv
        else:
            while X[psv + ll] == X[nsv + ll]:
                ll += 1
            if X[i + ll] == X[psv + ll]:
                ll += 1
                while X[i + ll] == X[psv + ll]:
                    ll += 1
                pos = psv
            else:
                while i + ll < n and X[i + ll] == X[nsv + ll]:
                    ll += 1
                pos = nsv
    
        if ll == 0:
            pos = -1
        prv[nfactors] = pos
        fl[nfactors] = ll
        lz[nfactors] = i
        i = i + max(1, ll)
        # end of inline
        nfactors += 1
    
    return np.array(prv[:nfactors]), np.array(lz[:nfactors]), np.array(fl[:nfactors])
