# http://www.inference.org.uk/mackay/python/compress/golomb/golomb.py
import math

def decode(bs):
    i = 0
    if bs[0] == '1':
        return 1 - 2
    blen = 0
    while bs[i] == '0':
        blen += 1
        i += 1
    i += 1
    n = 1
    while blen > 0:
        this_bit = ord(bs[i]) - ord('0')
        # print(n)
        n  = (n << 1) + this_bit
        blen -= 1
        i += 1
    return n - 2

def encode(n):
    n = n + 2
    if n == 1:
        return "1", 1
    blen = int(math.floor(math.log2(n)))
    bs = ['z'] * blen
    for i in range(blen):
        bs[i] = chr(ord('0') + n % 2)
        n = n >> 1
    bs.reverse()
    return ['0'] * blen + ['1'] + bs, 2 * blen + 1

if __name__ == "__main__":
    for i in range(-1, 20):
        enc = encode(i)
        print(enc)
        dec = decode(enc[0])
        print(dec)
