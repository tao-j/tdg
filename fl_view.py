# %%
import numpy as np
from pydivsufsort import divsufsort, kasai
import os
from tqdm import tqdm
from decomp import lpf_simple, lzf, kkp3
import plotly.express as px

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
fl  = np.fromfile(open(filename_pafl, "rb"), dtype=np.int32)
# %% 
p = np.histogram(fl, bins=1000, range=(0, 1e5))
fig = px.bar(x=p[1][1:], y=np.log2(p[0] + 1))
fig.show()

# %% 
exit()