## Usage
Install a C++ compiler and Cython as well as other reference python packages.
Compile the Cython extension using:
```
python setup.py build_ext --inplace 
```
Run the example using `python dedup.py`.

## Survey of existing dedup systems.
Both of the following are block based dedup with filesystem level possible compression. Usually files are compressed first then dedupped according to block hash. 
+ zfs
+ sdfs (opendedup)


### Quick summary of performance
The following result is from all bash version sources collected from `gnu.org` on July 2021.

Test name | final size | single file compression | block dedup | seperate files
----: | ----: | ----: | ----: | ----:
original downloaded gzipped | 296M |  | | no
uncompressed separate files | 1022MB | ext4 | | yes
plain | 932M | tar |  | tarball
xz (LZMA) | **161M** | | | tarball
zstd (Entropy) | 235M | | | tarball
gz (Entropy) | 280M | | | tarball
zfs | 1.19G | plain | no | yes
zfs | **648M** | plain | yes | yes
zfs | 935M | plain | yes | tarball
zfs | 474M | zstd | no | yes
zfs | 237M | zstd | yes | yes
zfs | 316M | zstd | yes | tarball
sdfs | **371M** | plain | yes | yes
sdfs | 554M | plain | yes | tarball

Note: it is unclear how to let fs to do single-file compression on sdfs

### Memory consumption
zfs
512B per 128K
512M per 128G
5M 1G (bash dataset)

sdfs
256M per 1T

## Reproducing the result
### Prepare the data
`wget -r https://ftp.gnu.org/....../bash/`

All bash version gzipped
```
➜ du -h bash
296M	bash
# cp -r to bash-gunzipped and gunzip all gz in bash dir
➜ du -h bash-gunzipped
1022M	bash-gunzipped
➜ tar cf bash-gunzipped.tar bash-gunzipped/
```

Used default compression level on the tarball for popular compression algos.
```
-rw-rw-r--  1 user user 932M Sep 29 15:59 bash-gunzipped.tar
-rw-rw-r--  1 user user 280M Sep 29 15:59 bash-gunzipped.tar.gz
-rw-rw-r--  1 user user 161M Sep 29 15:59 bash-gunzipped.tar.xz
-rw-rw-r--  1 user user 235M Sep 29 15:59 bash-gunzipped.tar.zst
```

### Test on ZFS
create zpools
```
➜  zpool create -m /t/plain tplain /plain.zfs
➜  zpool create -m /t/plaindedup tplaindedup /plaindedup.zfs
➜  zpool create -m /t/zstd tzstd /zstd.zfs
➜  zpool create -m /t/zstddeup tzstddedup /zstddedup.zfs
➜  zfs set dedup=on tplaindedup
➜  zfs set dedup=on tzstddedup
➜  zfs set compression=off tplain
➜  zfs set compression=off tplaindedup
➜  zfs set compression=zstd tzstd
➜  zfs set compression=zstd tzstddedup
```

copy separate files into several zfs datasets
```
➜ for i in `ls /t`; do echo $i; time cp -r bash-gunzipped /t/$i; done
plain
cp -r bash-gunzipped /t/$i  0.06s user 1.74s system 58% cpu 3.082 total
plaindedup
cp -r bash-gunzipped /t/$i  0.06s user 1.69s system 65% cpu 2.673 total
zstd
cp -r bash-gunzipped /t/$i  0.05s user 1.66s system 73% cpu 2.333 total
zstddeup
cp -r bash-gunzipped /t/$i  0.07s user 1.66s system 69% cpu 2.468 total
```

look at the statistics, `ALLOC` is actual physical disk space consumption. Need to figure out why the `FREE` and `AVAIL` is not the same for zfs and pool. Also note that `USED` is for size before dedup and after compression.

```
➜ zpool list
NAME          SIZE  ALLOC   FREE  CKPOINT  EXPANDSZ   FRAG    CAP  DEDUP    HEALTH  ALTROOT
test              9.50G  2.74G  6.76G        -         -     0%    28%  2.47x    ONLINE  -
tplain            1.38G  1.19G   187M        -         -    28%    86%  1.00x    ONLINE  -
tplaindedup       1.38G   648M   760M        -         -     7%    46%  1.96x    ONLINE  -
tplaindedupwhole  1.38G   935M   473M        -         -     8%    66%  1.00x    ONLINE  -
tzstd             1.38G   474M   934M        -         -     4%    33%  1.00x    ONLINE  -
tzstddedup        1.38G   237M  1.14G        -         -     5%    16%  2.38x    ONLINE  -
tzstddedupwhole   1.38G   316M  1.07G        -         -     1%    22%  1.00x    ONLINE  -


➜ zfs list
NAME             USED  AVAIL     REFER  MOUNTPOINT
test              3.34G  6.45G      128K  /test
test/lz4           602M  6.45G      602M  /test/lz4
test/lz4dedup      620M  6.45G      620M  /test/lz4dedup
test/plain        1.19G  6.45G     1.19G  /test/plain
test/zstd          473M  6.45G      473M  /test/zstd
test/zstddedup     492M  6.45G      492M  /test/zstddedup
tplain            1.19G  59.4M     1.19G  /t/plain
tplaindedup       1.20G   632M     1.19G  /t/plaindedup
tplaindedupwhole   937M   345M      933M  /t/plaindeupwhole
tzstd              474M   806M      473M  /t/zstd
tzstddedup         499M  1.02G      492M  /t/zstddeup
tzstddedupwhole    317M   964M      313M  /t/zstddeupwhole
```

memory consumption
```
➜ sudo zpool status -Dv tplaindedup
  pool: tplaindedup
 state: ONLINE
config:

	NAME                    STATE     READ WRITE CKSUM
	tplaindedup             ONLINE       0     0     0
	       /plaindedup.zfs  ONLINE       0     0     0

errors: No known data errors

 dedup: DDT entries 12426, size 526B on disk, 169B in core

bucket              allocated                       referenced
______   ______________________________   ______________________________
refcnt   blocks   LSIZE   PSIZE   DSIZE   blocks   LSIZE   PSIZE   DSIZE
------   ------   -----   -----   -----   ------   -----   -----   -----
     1    5.67K    359M    359M    366M    5.67K    359M    359M    366M
     2    3.05K    176M    176M    180M    6.96K    391M    391M    400M
     4    1.98K   38.5M   38.5M   42.2M    11.3K    182M    182M    204M
     8      729   4.97M   4.97M   6.60M    7.95K   54.9M   54.9M   73.3M
    16      620   3.57M   3.57M   5.12M    13.1K   78.9M   78.9M    112M
    32      121    228K    228K    600K    4.56K   9.43M   9.43M   23.3M
    64        1    512B    512B      4K       82     41K     41K    328K
 Total    12.1K    583M    583M    601M    49.6K   1.05G   1.05G   1.15G


 ➜ sudo zpool status -Dv tzstddedup
  pool: tzstddedup
 state: ONLINE
config:

	NAME                   STATE     READ WRITE CKSUM
	tzstddedup             ONLINE       0     0     0
	       /zstddedup.zfs  ONLINE       0     0     0

errors: No known data errors

 dedup: DDT entries 12426, size 527B on disk, 169B in core

bucket              allocated                       referenced
______   ______________________________   ______________________________
refcnt   blocks   LSIZE   PSIZE   DSIZE   blocks   LSIZE   PSIZE   DSIZE
------   ------   -----   -----   -----   ------   -----   -----   -----
     1    5.67K    359M    109M    112M    5.67K    359M    109M    112M
     2    3.05K    176M   53.1M   54.3M    6.96K    391M    119M    122M
     4    1.98K   38.5M   13.3M   15.7M    11.3K    182M   65.5M   79.9M
     8      729   4.97M   2.63M   3.91M    7.95K   54.9M   29.8M   44.4M
    16      620   3.57M   1.97M   3.36M    13.1K   78.9M   43.4M   73.2M
    32      121    228K    166K    516K    4.56K   9.43M   6.69M   19.7M
    64        1    512B    512B      4K       82     41K     41K    328K
 Total    12.1K    583M    180M    190M    49.6K   1.05G    373M    451M

dedup = 2.38, compress = 2.88, copies = 1.21, dedup * compress / copies = 5.68

➜ sudo zpool status -D tzstddedupwhole
  pool: tzstddedupwhole
 state: ONLINE
config:

	NAME                        STATE     READ WRITE CKSUM
	tzstddedupwhole             ONLINE       0     0     0
	        zstddedupwhole.zfs  ONLINE       0     0     0

errors: No known data errors

 dedup: DDT entries 7445, size 450B on disk, 145B in core

bucket              allocated                       referenced
______   ______________________________   ______________________________
refcnt   blocks   LSIZE   PSIZE   DSIZE   blocks   LSIZE   PSIZE   DSIZE
------   ------   -----   -----   -----   ------   -----   -----   -----
     1    7.26K    929M    310M    310M    7.26K    929M    310M    310M
     2       11   1.38M    852K    852K       22   2.75M   1.66M   1.66M
 Total    7.27K    931M    311M    311M    7.28K    932M    312M    312M

 ➜        sudo zpool status -D tplaindedupwhole
  pool: tplaindedupwhole
 state: ONLINE
config:

	NAME                         STATE     READ WRITE CKSUM
	tplaindedupwhole             ONLINE       0     0     0
	        plaindedupwhole.zfs  ONLINE       0     0     0

errors: No known data errors

 dedup: DDT entries 7445, size 455B on disk, 146B in core

bucket              allocated                       referenced
______   ______________________________   ______________________________
refcnt   blocks   LSIZE   PSIZE   DSIZE   blocks   LSIZE   PSIZE   DSIZE
------   ------   -----   -----   -----   ------   -----   -----   -----
     1    7.26K    929M    929M    929M    7.26K    929M    929M    929M
     2       11   1.38M   1.38M   1.38M       22   2.75M   2.75M   2.75M
 Total    7.27K    931M    931M    931M    7.28K    932M    932M    932M
```

```
➜ sudo zpool status -D test
  pool: test
 state: ONLINE
config:

	NAME              STATE     READ WRITE CKSUM
	test              ONLINE       0     0     0
	  /test.zfs  ONLINE       0     0     0

errors: No known data errors

 dedup: DDT entries 20387, size 502B on disk, 161B in core

bucket              allocated                       referenced
______   ______________________________   ______________________________
refcnt   blocks   LSIZE   PSIZE   DSIZE   blocks   LSIZE   PSIZE   DSIZE
------   ------   -----   -----   -----   ------   -----   -----   -----
     1    8.57K    690M    234M    234M    8.57K    690M    234M    234M
     2    6.08K    355M    130M    133M    13.3K    783M    287M    293M
     4    2.43K   78.2M   32.4M   33.7M    12.4K    365M    153M    159M
     8    1.48K   9.99M   5.72M   8.11M    17.4K    110M   63.7M   92.4M
    16      727   6.41M   3.55M   4.84M    15.9K    144M   79.8M    109M
    32      548   1.21M   1.10M   2.50M    23.0K   53.6M   48.8M    108M
    64      111   98.5K   98.5K    448K    8.31K   7.42M   7.42M   33.5M
   128        1    512B    512B      4K      164     82K     82K    656K
 Total    19.9K   1.11G    407M    417M    99.1K   2.10G    874M   1.01G


    Dnode slots:
	Total used:         48458
	Max used:           48510
	Percent empty:   0.107194
```

#### zdb -S
```
Dataset test [ZPL], ID 54, cr_txg 1, 128K, 11 objects

    Object  lvl   iblk   dblk  dsize  dnsize  lsize   %full  type
         0    6   128K    16K    88K     512   272K    2.02  DMU dnode
        -1    1   128K    512      0     512    512  100.00  ZFS user/group/project used
        -2    1   128K    512      0     512    512  100.00  ZFS user/group/project used
        -3    1   128K    512      0     512    512  100.00  ZFS user/group/project used
         1    1   128K    512     8K     512    512  100.00  ZFS master node
         2    1   128K    512      0     512    512  100.00  ZFS directory
        32    1   128K    512      0     512    512  100.00  SA master node
        33    1   128K    512      0     512    512  100.00  ZFS delete queue
        34    1   128K    512      0     512    512  100.00  ZFS directory
        35    1   128K  1.50K     8K     512  1.50K  100.00  SA attr registration
        36    1   128K    16K    16K     512    32K  100.00  SA attr layouts
       128    1   128K    512      0     512    512  100.00  ZFS directory
       256    1   128K    512      0     512    512  100.00  ZFS directory
       384    1   128K    512      0     512    512  100.00  ZFS directory
       512    1   128K    512      0     512    512  100.00  ZFS directory

    Dnode slots:
	Total used:            11
	Max used:             512
	Percent empty:  97.851562

Verified large_blocks feature refcount of 0 is correct
Verified large_dnode feature refcount of 0 is correct
Verified sha512 feature refcount of 0 is correct
Verified skein feature refcount of 0 is correct
Verified edonr feature refcount of 0 is correct
Verified userobj_accounting feature refcount of 6 is correct
Verified encryption feature refcount of 0 is correct
Verified project_quota feature refcount of 6 is correct
Verified redaction_bookmarks feature refcount of 0 is correct
Verified redacted_datasets feature refcount of 0 is correct
Verified bookmark_written feature refcount of 0 is correct
Verified livelist feature refcount of 0 is correct
Verified zstd_compress feature refcount of 2 is correct
Verified device_removal feature refcount of 0 is correct
Verified indirect_refcount feature refcount of 0 is correct

Traversing all blocks to verify checksums and verify nothing leaked ...

loading concrete vdev 0, metaslab 18 of 19 ...
3.30G completed (  64MB/s) estimated time remaining: 4294850966hr 4294967240min 4294967266sec
	No leaks (block sum matches space maps exactly)

	bp count:                281486
	ganged count:                 0
	bp logical:          7345100288      avg:  26094
	bp physical:         3052996608      avg:  10845     compression:   2.41
	bp allocated:        3583172608      avg:  12729     compression:   2.05
	bp deduped:           643551232    ref>1:  11607   deduplication:   1.18
	Normal class:        2601512960     used: 25.50%
	Embedded log class              0     used:  -nan%

	additional, non-pointer bps of type 0:      10537
	Dittoed blocks on same vdev: 26576

Blocks	LSIZE	PSIZE	ASIZE	  avg	 comp	%Total	Type
     -	    -	    -	    -	    -	    -	     -	unallocated
     2	  32K	   8K	  24K	  12K	 4.00	  0.00	object directory
     -	    -	    -	    -	    -	    -	     -	object array
     1	  16K	   4K	  12K	  12K	 4.00	  0.00	packed nvlist
     -	    -	    -	    -	    -	    -	     -	packed nvlist size
     -	    -	    -	    -	    -	    -	     -	bpobj
     -	    -	    -	    -	    -	    -	     -	bpobj header
     -	    -	    -	    -	    -	    -	     -	SPA space map header
    38	4.75M	 152K	 456K	  12K	32.00	  0.01	SPA space map
     -	    -	    -	    -	    -	    -	     -	ZIL intent log
 7.47K	 123M	30.2M	60.4M	8.10K	 4.09	  1.77	DMU dnode
     7	  28K	  28K	  60K	8.57K	 1.00	  0.00	DMU objset
     -	    -	    -	    -	    -	    -	     -	DSL directory
     9	   5K	   1K	  12K	1.33K	 5.00	  0.00	DSL directory child map
     -	    -	    -	    -	    -	    -	     -	DSL dataset snap map
     -	    -	    -	    -	    -	    -	     -	DSL props
     -	    -	    -	    -	    -	    -	     -	DSL dataset
     -	    -	    -	    -	    -	    -	     -	ZFS znode
     -	    -	    -	    -	    -	    -	     -	ZFS V0 ACL
  259K	6.70G	2.80G	3.22G	12.7K	 2.39	 96.47	ZFS plain file
 7.16K	16.7M	11.1M	49.4M	6.90K	 1.51	  1.45	ZFS directory
     6	   3K	   3K	  48K	   8K	 1.00	  0.00	ZFS master node
     -	    -	    -	    -	    -	    -	     -	ZFS delete queue
     -	    -	    -	    -	    -	    -	     -	zvol object
     -	    -	    -	    -	    -	    -	     -	zvol prop
     -	    -	    -	    -	    -	    -	     -	other uint8[]
     -	    -	    -	    -	    -	    -	     -	other uint64[]
     -	    -	    -	    -	    -	    -	     -	other ZAP
     -	    -	    -	    -	    -	    -	     -	persistent error log
     1	 128K	   4K	  12K	  12K	32.00	  0.00	SPA history
     -	    -	    -	    -	    -	    -	     -	SPA history offsets
     -	    -	    -	    -	    -	    -	     -	Pool properties
     -	    -	    -	    -	    -	    -	     -	DSL permissions
     -	    -	    -	    -	    -	    -	     -	ZFS ACL
     -	    -	    -	    -	    -	    -	     -	ZFS SYSACL
     -	    -	    -	    -	    -	    -	     -	FUID table
     -	    -	    -	    -	    -	    -	     -	FUID table size
     -	    -	    -	    -	    -	    -	     -	DSL dataset next clones
     -	    -	    -	    -	    -	    -	     -	scan work queue
     -	    -	    -	    -	    -	    -	     -	ZFS user/group/project used
     -	    -	    -	    -	    -	    -	     -	ZFS user/group/project quota
     -	    -	    -	    -	    -	    -	     -	snapshot refcount tags
   852	3.33M	3.33M	9.98M	  12K	 1.00	  0.29	DDT ZAP algorithm
     2	  32K	   8K	  24K	  12K	 4.00	  0.00	DDT statistics
     -	    -	    -	    -	    -	    -	     -	System attributes
     -	    -	    -	    -	    -	    -	     -	SA master node
     6	   9K	   9K	  48K	   8K	 1.00	  0.00	SA attr registration
    12	 192K	  48K	  96K	   8K	 4.00	  0.00	SA attr layouts
     -	    -	    -	    -	    -	    -	     -	scan translations
     -	    -	    -	    -	    -	    -	     -	deduplicated block
     -	    -	    -	    -	    -	    -	     -	DSL deadlist map
     -	    -	    -	    -	    -	    -	     -	DSL deadlist map hdr
     -	    -	    -	    -	    -	    -	     -	DSL dir clones
     -	    -	    -	    -	    -	    -	     -	bpobj subobj
     -	    -	    -	    -	    -	    -	     -	deferred free
     -	    -	    -	    -	    -	    -	     -	dedup ditto
    16	 171K	23.5K	 120K	7.50K	 7.28	  0.00	other
  275K	6.84G	2.84G	3.34G	12.4K	 2.41	100.00	Total

Block Size Histogram

  block   psize                lsize                asize
   size   Count   Size   Cum.  Count   Size   Cum.  Count   Size   Cum.
    512:  47.8K  23.9M  23.9M  47.8K  23.9M  23.9M      0      0      0
     1K:  49.2K  62.4M  86.3M  49.2K  62.4M  86.3M      0      0      0
     2K:  47.8K   122M   208M  47.8K   122M   208M      0      0      0
     4K:  56.2K   236M   444M  30.2K   161M   369M   170K   678M   678M
     8K:  23.7K   225M   668M  18.4K   205M   575M  53.8K   466M  1.12G
    16K:  11.4K   237M   906M  17.8K   344M   919M  12.5K   255M  1.37G
    32K:  16.7K   729M  1.60G  7.02K   293M  1.18G  16.9K   737M  2.09G
    64K:  4.46K   340M  1.93G  4.71K   446M  1.62G  4.43K   337M  2.41G
   128K:  7.32K   937M  2.84G  41.7K  5.22G  6.84G  7.38K   944M  3.34G
   256K:      0      0  2.84G      0      0  6.84G      0      0  3.34G
   512K:      0      0  2.84G      0      0  6.84G      0      0  3.34G
     1M:      0      0  2.84G      0      0  6.84G      0      0  3.34G
     2M:      0      0  2.84G      0      0  6.84G      0      0  3.34G
     4M:      0      0  2.84G      0      0  6.84G      0      0  3.34G
     8M:      0      0  2.84G      0      0  6.84G      0      0  3.34G
    16M:      0      0  2.84G      0      0  6.84G      0      0  3.34G

                            capacity   operations   bandwidth  ---- errors ----
description                used avail  read write  read write  read write cksum
test                      2.42G 7.08G 8.68K     0  110M     0     0     0     0
       /test.zfs          2.42G 7.08G 8.68K     0  110M     0     0     0     0

ZFS_DBGMSG(zdb) START:
spa.c:5155:spa_open_common(): spa_open_common: opening test
spa_misc.c:418:spa_load_note(): spa_load(test, config trusted): LOADING
vdev.c:152:vdev_dbgmsg(): file vdev '/test.zfs': best uberblock found for spa test. txg 402
spa_misc.c:418:spa_load_note(): spa_load(test, config untrusted): using uberblock with txg=402
spa.c:8336:spa_async_request(): spa=test async request task=2048
spa_misc.c:418:spa_load_note(): spa_load(test, config trusted): LOADED
ZFS_DBGMSG(zdb) END
```


### Test on SDFS

each record has the following data structure

| dup (1 byte) | hash (hash algo length) | reserverd 1(byte) | hash location 8 bytes |
https://131002.net/siphash/
To calculate memory requirements keep in mind that each stored chunk takes up approximately 256 MB of RAM per 1 TB of unique storage.
Fixed and Variable Block Deduplication
SDFS Can perform both fixed and variable block deduplication. Fixed block deduplication takes fixed blocks of data and hashes those blocks. Variable block deduplication attempts to find natural breaks within stream of data an creates variable blocks at those break points.

**Fixed block deduplication** is performed at volume defined fixed byte buffers within SDFS. These fixed blocks are defined when the volume is created and is set at 4k by default but can be set to a maximum value of 128k. Fixed block deduplication is very useful for active structured data such as running VMDKs or Databases. Fixed block deduplication is simple to perform and can therefore be very fast for most applications.

**Variable block deduplication** is performed using Rabin Window Borders (http://en.wikipedia.org/wiki/Rabin_fingerprint). SDFS uses fixed buffers of 256K and then runs a rolling hash across that buffer to find natural breaks. The minimum size of a variable block is 4k and the maximum size is 32k. Variable block deduplication is very good at finding duplicated blocks in unstructured data such as uncompressed tar files and documents. Variable Block deduplication typically will create blocks of 10k-16k. This makes Variable block deduplication more salable than fixed block deduplication when it is performed at 4k block sizes. The downside of Variable block deduplication is that it can be computationally intensive and sometimes slower for write processing.

```
$ sudo mount.sdfs plain /t/plain
Running Program SDFS Version 3.7.8 build date 2018-09-28 17:20
reading config file = /etc/sdfs/plain-volume-cfg.xml
multiplier=32 size=8
mem=270144 memperDB=33768 bufferSize=1073741824 bufferSizePerDB=134217728
Loading Existing Hash Tables |))))))))))))))))))))))))))))))))))))))))))))))))))| 100%

Mounted Filesystem
$ df -h
Filesystem                                     Size  Used Avail Use% Mounted on
sdfs:/etc/sdfs/plain-volume-cfg.xml:6442       2.1G  371M  1.7G  18% /t/plain
sdfs:/etc/sdfs/plainwhole-volume-cfg.xml:6443  2.1G  554M  1.6G  27% /t/plainwhole
```

```
$ sdfscli --volume-info plainwhole --port 6442
Files : 47006
Volume Capacity : 2 GB
Volume Current Logical Size : 896.17 MB
Volume Max Percentage Full : 95.0%
Volume Duplicate Data Written : 11.33 GB
Unique Blocks Stored: 370.07 MB
Unique Blocks Stored after Compression : 371.08 MB
Cluster Block Copies : 2
Volume Virtual Dedup Rate (Unique Blocks Stored/Current Size) : 58.71%
Volume Actual Storage Savings (Compressed Unique Blocks Stored/Current Size) : 58.59%
Compression Rate: -0.27%

$ sdfscli --dse-info --port 6442
DSE Max Size : 2.06 GB
DSE Current Size : 370.07 MB
DSE Compressed Size : 371.08 MB
DSE Percent Full : 17.53%
DSE Page Size : 262144
DSE Blocks Available for Reuse : 0
Total DSE Blocks : 119952
Average DSE Block Size : 3235
DSE Current Cache Size : 9.99 GB
DSE Max Cache Size : 10 GB
Trottled Read Speed : 0 B/s
Trottled Write Speed : 0 B/s

$ sdfscli --volume-info plainwhole --port 6443
Files : 1
Volume Capacity : 2 GB
Volume Current Logical Size : 931.9 MB
Volume Max Percentage Full : 95.0%
Volume Duplicate Data Written : 379.95 MB
Unique Blocks Stored: 552.05 MB
Unique Blocks Stored after Compression : 553.66 MB
Cluster Block Copies : 2
Volume Virtual Dedup Rate (Unique Blocks Stored/Current Size) : 40.76%
Volume Actual Storage Savings (Compressed Unique Blocks Stored/Current Size) : 40.59%
Compression Rate: -0.29%

$ sdfscli --dse-info --port 6443
DSE Max Size : 2.06 GB
DSE Current Size : 552.05 MB
DSE Compressed Size : 553.66 MB
DSE Percent Full : 26.16%
DSE Page Size : 262144
DSE Blocks Available for Reuse : 0
Total DSE Blocks : 92592
Average DSE Block Size : 6251
DSE Current Cache Size : 563.43 MB
DSE Max Cache Size : 10 GB
Trottled Read Speed : 0 B/s
Trottled Write Speed : 0 B/s
```

## TODO
https://btrfs.wiki.kernel.org/index.php/Deduplication

https://github.com/bup/bup

