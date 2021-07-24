# -*- coding: utf-8 -*-
"""
Created on Thu Feb 18 19:51:40 2021

@author: hl2nu
"""
import numpy as np
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
periods = [1, 2, 3]
n = 3
output_size = 11
filename = "train_toy_period[1,2,3]_del"

n_dist = 5000  # num of dists
n_sample = 10  # num of samples per dist
# n_dataset =  10# num of dataset being generated
datalength = np.array([100])
f_trainX = h5py.File("data/" + "X" + filename, "w")
f_trainY = h5py.File("data/" + "Y" + filename, "w")

print("filename:", filename)
print("data generation begins!")
for l in datalength:
    times = time.time()
    l = int(l)
    X = np.empty(shape=(n_sample * n_dist * len(periods), int(l), 4), dtype=float)
    Y = np.empty(shape=(n_sample * n_dist * len(periods), output_size),
                 dtype=float)
    print('datalength=', l)
    k = 0
    for i in range(n_dist):
        Plist = [
            randdist_period_size_del(period, n, output_size)
            for period in periods
        ]
        # P = randdist_period_size(2, n,10)
        for j in range(n_sample):
            for itrper in range(len(periods)):
                prd = periods[itrper]
                P = Plist[itrper]
                s = Sequence(np.random.randint(4, size=10), l, P[0:prd * n + 2])
                x = s.evolve()
                X[k] = seqto4rowmx(x)
                Y[k] = P
                k += 1
    f_trainX.create_dataset("X_" + str(l), data=X)
    f_trainY.create_dataset("Y_" + str(l), data=Y)
    print("dataset_length", l, "stored")
    timee = time.time()
    print(timee - times)
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
