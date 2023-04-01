Previous occurence array is not always pointing to the first occurence of the pattern.
```
nfa =  12
n = 21
>     a  b  c  d  Z  a  b  c  d  B  a  b  c  d  Y  a  b  c  d  A  
 int8
i  [  0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20] int64
sa [ 20 19  9 14  4 15  5 10  0 16  6 11  1 17  7 12  2 18  8 13  3] int32
isa[  8 12 16 20  4  6 10 14 18  2  7 11 15 19  3  5  9 13 17  1  0] int32
lcp[  0  0  0  0  0  0  4  4  4  0  3  3  3  0  2  2  2  0  1  1  1] int32
prv  -1 -1 -1 -1 -1  0          -1  0          -1  5          -1 -1  int32
lz    0  1  2  3  4  5           9 10          14 15          19 20  int32
fl    0  0  0  0  0  4           0  4           0  4           0  0  int32

nfa =  12
n = 21
>     a  b  c  d  Z  a  b  c  d  Y  a  b  c  d  X  a  b  c  d  A  
 int8
i  [  0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20] int64
sa [ 20 19 14  9  4 15 10  5  0 16 11  6  1 17 12  7  2 18 13  8  3] int32
isa[  8 12 16 20  4  7 11 15 19  3  6 10 14 18  2  5  9 13 17  1  0] int32
lcp[  0  0  0  0  0  0  4  4  4  0  3  3  3  0  2  2  2  0  1  1  1] int32
prv  -1 -1 -1 -1 -1  0          -1  5          -1 10          -1 -1  int32
lz    0  1  2  3  4  5           9 10          14 15          19 20  int32
fl    0  0  0  0  0  4           0  4           0  4           0  0  int32

nfa =  12
n = 21
>     a  b  c  d  A  a  b  c  d  B  a  b  c  d  C  a  b  c  d  D  
 int8
i  [  0  1  2  3  4  5  6  7  8  9 10 11 12 13 14 15 16 17 18 19 20] int64
sa [ 20  4  9 14 19  0  5 10 15  1  6 11 16  2  7 12 17  3  8 13 18] int32
isa[  5  9 13 17  1  6 10 14 18  2  7 11 15 19  3  8 12 16 20  4  0] int32
lcp[  0  0  0  0  0  0  4  4  4  0  3  3  3  0  2  2  2  0  1  1  1] int32
prv  -1 -1 -1 -1 -1  0          -1  5          -1 10          -1 -1  int32
lz    0  1  2  3  4  5           9 10          14 15          19 20  int32
fl    0  0  0  0  0  4           0  4           0  4           0  0  int32

```

nfa =  11010137
n = 977172480
Last time
lzf >=     4,  0.05368871394126859 | 50.03MiB
lzf >=     8,  0.06284158734187847 | 58.56MiB
lzf >=    16,  0.07749514778598758 | 72.22MiB
lzf >=    32,  0.09485259117203138 | 88.39MiB
lzf >=    64,  0.11786517335199616 | 109.84MiB
lzf >=   128,  0.14677102219456692 | 136.78MiB
lzf >=   256,  0.16875651343558098 | 157.26MiB

Now....
lzf >=     2,  0.08133471060810063 | 75.80MiB
lzf >=     4,  0.09574397129460707 | 89.22MiB

## TODO

1. How their source model works
2. Run their algo on bash-all and grch38
3. Visualiztion [fv mentioned in ](http://mattmahoney.net/dc/dce.html) to build our own model, hard to compare nissen's a.t.m.



### Universal compression
[Large Text Compression Benchmark](http://mattmahoney.net/dc/text.html)
nncp
[cmix](http://www.byronknoll.com/cmix.html)
[zpaq](http://mattmahoney.net/dc/text.html#1422)
[mcm](https://github.com/mathieuchartier/mcm)

sharnd_challenge.dat

[Lossless Photo Compression Benchmark](http://qlic.altervista.org/)


LZMA uses a dictionary compression algorithm (a variant of LZ77 with huge dictionary sizes and special support for repeatedly used match distances), whose output is then encoded with a range encoder, using a complex model to make a probability prediction of each bit. The dictionary compressor finds matches using sophisticated dictionary data structures, and produces a stream of literal symbols and phrase references, which is encoded one bit at a time by the range encoder: many encodings are possible, and a dynamic programming algorithm is used to select an optimal one under certain approximations.