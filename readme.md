# Introduction
## Compression Algorithms
Below is a list programs/libraries with their underlying algorithms.
In the following sections, program/library name will be used to represent the algorithms described in this section.
+ `zstd`: [Zstandard](https://facebook.github.io/zstd/)
+ `zlib`: [LZ77]() library
+ `gzip`: `zlib` program
+ `lzma`: [LZMA]() library
+ `xz`: `lzma` program
+ `zpaq`: [the ZPAQ algorithm](https://mattmahoney.net/dc/zpaq_compression.pdf)

## De-duplication Systems
Both of the following are block based dedup with file system level possible compression. Usually files are compressed first then dedupped according to block hash. 
+ `zfs`: each block is first optionally compressed by `zstd`/`lz4`. Then a hash table indexing all checksums of the blocks are kept in memory to discover potential duplicated blocks.
+ `sdfs` (opendedup): ?
+ `zpaq`: 
  + > When adding files, zpaq uses a rolling hash function to split files into fragments with an average size of 64 KB along content-dependent boundaries. Then it computes the SHA-1 hash of the fragment and compares it with saved hashes from the current and previous versions. If it finds a match then the fragment is not stored.
  + > Deduplication requires 1 MB of memory per GB of deduplicated but uncompressed archive data to update, and 0.5 MB per GB to list or extract. 

## Our Implementation
`lzf` algorithm in `dedup.py`:
First, a suffix array is constructed from the given string as `sa`. Then [KKP3](1) `decomp.pyx` or `decomp_navive.py` is used to construct Lempel-Ziv Factorization based on `sa`, which produce `prv` (the index of staring point of previous occurrence of the current string. When it is `-1`, it fetches next alphabet from the dictionary), `fl` (the number of characters to copy starting from where `prv` points to in order to recover the current factor). Finally, for the dictionary, since we interpret the data in Bytes(8 bits), the maximum is fixed and ignorable compared to the file being compressed. Just the occurrence of each word has to be ordered to match the `prv` array.

[1]: Linear Time Lempel-Ziv Factorization: Simple, Fast, Small, Juha K ̈arkk ̈ainen, Dominik Kempa, and Simon J. Puglisi

### Coding of `prv` and `fl`
By using a more efficient coding scheme, the storage space to save these two arrays can be further reduced.
We explore the Elias Gamma (EG) `src/main.rs` code as well as some universal compression libraries such as `lzma` `zlib.

# Analysis
## Data
All available bash version sources archived in `gnu.org` was downloaded on July 2021 to form the `bash` dataset. All files are first decompressed and concatenated into a large file for compression unless otherwise stated.

Human genome `GRHC38` is used as another benchmark. Due to its size and `lzf` is not that memory efficient it is broken down into two pieces `grch38.1` and `grch38.2` to be processed. (It seems that the `fasta` format is used).

`enwik9` is a popular text benchmark primarily used in [Large Text Compression Benchmark](https://www.mattmahoney.net/dc/text.html).

## Compression of `lzf`
For the `bash` dataset, 44MiB is need both for `prv` and `fl`, meanwhile
```
lzma can save prv 36.88MiB
lzma can save fl  3.37MiB
zlib can save prv 32.39MiB
zlib can save fl  1.35MiB
```
Using EG does not benefit the `prv` since those numbers can be compressed better when encoded in offset values.
```
prv| 44MiB -> EG 69MiB -> zlib 48MiB
fl | 44MiB -> EG 7MiB  -> zlib 5.2MiB
```

## Distribution of the Repeat Length
By using `lzf` one can chunk the string into multiple repeats, the following table lists the remaining bytes in the original string after the removal of repeated strings. In addition, another popular chunking algorithm called Rabin Window Fingerprint (`rab`) is also tested. However, due to its parametric nature, it is only possible to designate the expected repeat length.

Factor Length     | Residual Length
--- | ---
lzf >=     2,  | <=  76.41MiB
lzf >=     4,  | <=  89.84MiB
lzf >=     8,  | <=  98.37MiB
lzf >=    16,  | <=  112.03MiB
lzf >=    32,  | <=  128.20MiB
lzf >=    64,  | <=  149.65MiB
lzf >=   128,  | <=  176.59MiB
lzf >=   256,  | <=  197.07MiB
rab E 256 | >= 203.37
lzf >=   512,  | <=  228.90MiB
rab E 512 | >= 255.06 MiB
lzf >=  1024,  | <=  263.14MiB
rab E 1024 | >= 308.66 MiB
lzf >=  2048,  | <=  309.00MiB
rab E 2048 | >= 368.40 MiB
lzf >=  4096,  | <=  369.85MiB
rab E 4096 | >= 432.43 MiB
lzf >=  8192,  | <=  433.28MiB
lzf >= 16384,  | <=  499.05MiB
lzf >= 32768,  | <=  559.46MiB
lzf >= 65536,  | <=  630.49MiB
lzf >=131072,  | <=  718.99MiB


## Memory Consumption Analysis
### zpaq
avg 64KB
1K per 1M

### zfs
512B per 128K
512M per 128G
5M 1G (bash dataset)

### sdfs
256M per 1T
Note: it is unclear how to let fs to do single-file compression on sdfs
### lzf
9B per B

## Deduplication System Test
Using `bash` data, it is obvious that the files itself can be served as a way to chunk the data, since from time to time, it is possible that the same file would not change from old version to new version. However, when files are concatenated together, then if the files are chunked by methods that are not content-aware, then it is prone to suffer performance loss, which is demonstrated in the `zfs` case. While `zpaq` and `sdfs` both use content-aware chunking methods. Of course `lzf` is also content-aware, since it finds the repeat in brute force.

In the following table for the `bash` data, some rows are produced using `tarball` which means all files are concatenated. 

Method | Size | Compression | De-duplication | Concatenation
----: | ----: | ----: | ----: | ----:
original | 932M | no | no | tarball
xz | **161M** | no | no | tarball
zstd | 235M | zstd | no | tarball
gzip | 280M | zlib | no | tarball
zfs | 1.19G | no | no | no
zfs | **648M** | no | yes | no
zfs | 935M | no | yes | tarball
zfs | 474M | zstd | no | no
zfs | 237M | zstd | yes | no
zfs | 316M | zstd | yes | tarball
sdfs | **371M** | no | yes | no
sdfs | 554M | no | yes | tarball
zpaq | 72M | zpaq | no | tarball 
zpaq | 27M | zpaq | yes | no
lzf | 88M | lzf | yes | tarball

## Compression Test
### `grch38`
On `grch38.1` the performance is pretty bad considering the way we encode `prv` and `fl` is not optimal, while generic compression algorithms can adapt to this case better.

Method | Size |
 --- | --- 
original | 1.8G | no | 
lzf | 1.57G |
lzf + zstd | 688M
zstd | 587M
gzip | 561M

### `enwiki9`
`lzf` with `xz` savings: 226*2 - 170 = 282 MiB

Results of all other methods can be found on the 
[Benchmark website](https://www.mattmahoney.net/dc/text.html)

# Usage
Install a C++ compiler and Cython as well as other referenced python packages. Just install every package that it complaints missing.
Compile the Cython extension using:
```
python setup.py build_ext --inplace 
```
Run the example using `python dedup.py`.

To run the encode and decode of Elias Gamma, install `rustup` and use `cargo` to build and run.