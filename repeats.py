# %% https://arxiv.org/pdf/1304.0528.pdf
def findsmaxr(s, sa, lcp, ml=2):
    n = len(s)
    up = 0
    for i in range(1, n-1):
        if lcp[i] > lcp[i-1]:
            up = i
        elif lcp[i] != lcp[i-1] and lcp[i-1] >= ml:
            test = set()
            for j in range(up, i):
                if sa[j] > 1:
                    test.add(s[sa[j] - 2])
            print(test)
            if len(test) == i - up:
                rlen = lcp[up]
                noccur = i - up + 1
                print("len", rlen, "times:", noccur, "loc", sa[up:up+noccur])
                for k in range(noccur):
                    start = sa[up + k]
                    print(s[start:start+rlen])

# findsmaxr(tostr, sa, lcp)
# tt = time()
# rsa = [sa[0]] * len(sa)
# for idx, v in enumerate(sa):
#     rsa[v] = idx
# for i in range(len(sa)):
#     assert i == sa[rsa[i]]
# text = tostr
# maxlen = max(lcp)
# result = {}
# for i in range(1, len(text)):
#     if lcp[i] == maxlen:
#         j1, j2, h = sa[i - 1], sa[i], lcp[i]
#         assert text[j1:j1 + h] == text[j2:j2 + h]
#         substring = text[j1:j1 + h]
#         if not substring in result:
#             result[substring] = [j1]
#         result[substring].append(j2)
# print(dict((k, sorted(v)) for k, v in result.items()))
# print("aa", time() - tt)