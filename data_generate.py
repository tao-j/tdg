# -*- coding: utf-8 -*-
"""
Created on Thu Feb 18 19:51:40 2021

@author: hl2nu
"""
import numpy as np
from evolution_fixedroot import generate_root_nodel, seqto4rowmx, randdist_del,randdist,randdist_period,randdist_period_size,randdist_period_size_del,generate_root
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
period = [1,2,3]
n = 3
outputsize = 11
filename = "train_toy_period[1,2,3]_del"

Ndist = 5000 # num of dists 
Nsample = 10 # num of samples per dist
#Ndataset =  10# num of dataset being generated
datalength = np.linspace(100,1000,46)
f_trainX = h5py.File("data/"+"X"+filename,"w")
f_trainY = h5py.File("data/"+"Y"+filename,"w")  

print("filename:",filename)
print("data generation begins!")
for l in datalength:
    times = time.time()
    s = int(l)
    X = np.empty(shape = (Nsample*Ndist*len(period), int(s),4), dtype = float)
    Y = np.empty(shape = (Nsample*Ndist*len(period),outputsize), dtype = float)
    print('datalength=',s)
    k = 0
    for i in range(Ndist):
        Plist = [randdist_period_size_del(periodx, n, outputsize) for periodx in period]
        #P = randdist_period_size(2, n,10)
        for j in range(Nsample):
            for itrper in range(len(period)):
                prd = period[itrper]
                P = Plist[itrper]
                x_root = np.random.randint(4,size = 10) # define a random root
                x = generate_root(x_root,s,P[0:prd*n+2])
                X[k] = seqto4rowmx(x)
                Y[k] = P
                k+=1
    f_trainX.create_dataset("X_"+str(s), data = X)
    f_trainY.create_dataset("Y_"+str(s), data = Y)
    print("dataset_length", s,"stored")
    timee = time.time()
    print(timee - times)
f_trainX.close()
f_trainY.close()


#%%
log = open("data/read_me.txt","a")
log.write("\n")
log.write("Dataset Name: "+filename+"\n")
log.write("Deletion = " + str(deletion) + "\n")
#if deletion == True:
#    log.write(" del prob = " + str(alpha) + " ")
log.write("Ndist = " + str(Ndist) + "\n")
log.write("Nsample = " + str(Nsample) + "\n")
log.write("dataset length=" + str(datalength) + "\n" )
log.write("period=" + str(period) + "\n" )
log.write("\n")
log.close()
