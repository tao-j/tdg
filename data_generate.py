# -*- coding: utf-8 -*-
"""
Created on Thu Feb 18 19:51:40 2021

@author: hl2nu
"""
import numpy as np
from tqdm import tqdm
from evolve import *
import h5py
import time
'''
#parameters input
L = 3 # length of mutation dist
deletion = False
alpha = 0.1 #upper bound of prob of del
beta = 0.5 #lower bound of td of period
datatype = "train"
period = 1
#
if deletion:
    L1=L+2
    filename = datatype + "_L="+str(L)+"_"+str(alpha)
else:
    L1=L+1
    filename = datatype + "_L="+str(L)+"_nodel"
start = time.time()
n = 1000 # string length 
'''
deletion = False
periods = [3]
n_period = 3
root_len = 10
filename = "train_toy_period[3]"

n_dist = 5000  # num of dists
n_sample = 10  # num of samples per dist
# n_dataset =  10# num of dataset being generated
datalength = range(128, 1024, 32)
f_trainX = h5py.File("data/" + "xX" + filename, "w")
f_trainY = h5py.File("data/" + "xY" + filename, "w")

print("filename:", filename)
for target_len in datalength:
    print(f"n_dist {n_dist} len: {target_len} {n_period}")
    print('datalength=', target_len)
    X = np.empty(shape=(n_sample * n_dist * len(periods), target_len, 4), dtype=float)
    Y = np.empty(shape=(n_sample * n_dist * len(periods), max(periods) * n_period + 2),
                 dtype=float)

    for pi, period in enumerate(periods):
        output_size = period * n_period + 2
        for di in tqdm(range(n_dist)):
            P = SequenceDup.gen_dist(period, n_period, output_size)
            # P = randdist_period_size_del(period, n_period, output_size)
            for si in range(n_sample):
                s = SequenceDup(np.random.randint(4, size=root_len), target_len, P[0:output_size])
                x = s.evolve()
                k = di * n_sample + si
                X[k] = seqto4rowmx(x)
                Y[k] = P

    f_trainX.create_dataset("X_" + str(target_len), data=X)
    f_trainY.create_dataset("Y_" + str(target_len), data=Y)
    print("dataset_length", target_len, "stored")
f_trainX.close()
f_trainY.close()

#%%
log = open("data/read_me.txt", "a")
log.write("\n")
log.write("Dataset Name: " + filename + "\n")
log.write("Deletion = " + str(deletion) + "\n")
#if deletion == True:
#    log.write(" del prob = " + str(alpha) + " ")
log.write("Ndist = " + str(n_dist) + "\n")
log.write("Nsample = " + str(n_sample) + "\n")
log.write("dataset length=" + str(datalength) + "\n")
log.write("period=" + str(periods) + "\n")
log.write("\n")
log.close()
