# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 17:35:17 2021

@author: hl2nu
"""
import numpy as np
from tensorflow import keras
#from evolution_fixedroot import strto4rowmx
import h5py
from numpy import linalg as LA


#%%
def predict(filenamex, filenamey, modelname):
    model = keras.models.load_model(modelname)
    print('model loaded')
    #%%
    fX = h5py.File(filenamex, 'r')
    X_index = list(fX.keys())
    print("X datasets:", X_index)
    fY = h5py.File(filenamey, 'r')
    Y_index = list(fY.keys())
    print("Y datasets:", Y_index)

    #%%
    Numdataset = len(X_index)
    Resnorm = 0
    print("predict begins!")
    for i in range(Numdataset):
        print("dataset:", X_index[i])
        xindex = X_index[i]
        yindex = Y_index[i]
        testX = np.array(fX[xindex])
        testY = np.array(fY[yindex])
        pred = model.predict(testX)
        res = np.subtract(testY, pred)
        resnorm = [LA.norm(v) for v in res]
        rdataset = sum(resnorm) / len(resnorm)
        print("MSRE:", rdataset)
        Resnorm = Resnorm + rdataset
    return Resnorm / Numdataset


#%%
"""
s = 'AAATTGTCAGTCGTTGTCAGTTAATGAATGTCATGTCGCCTGCCCGGCGGGGCGGGGCGGCTGGCTGTGCGTGCGTGATGCGGAACGCAGCAGCGCGCGCAAGCAGCCGCCCGCCGCGCCGTGCCGCGCCGCCTGGCGGCTGTTGCTGGCTGCTTACTAAAGGGACGGGGGGTGGGCCTGGGCGGCCAGTGCCAACCAGTCTTCTTTTCTTTCTTCGTTCCATTCTTGCGTTTGTTGTGGCGGCGCAGCGGAGAGGAGAGGCTGCGTGCGTGCGGCGGGACGGGGCGGGGGGGGGGATTATCAGTCAGTCCAAAGCCCGCACAGCGGCAGAAAAGGAAAGGAAAAAAAAAACAAAGCAAAAAAAATATAATAAAAAAAAAAAAAACAACAAACAGACCAAAAAACAAAACAACAAACAAAAAAAAAAACACAACAAAACAAACCAATACATAACAAATCCAAACCAACACCACCAACCAAACAAACCAAACCAAAGATAGAAAGAAAAGGAAGGAAGAAGAAAAGAAAAACAAATCAAAACACAACAAAACAATCGAAGTAATAATAGGATAAGATGATAATAAAATAAATAAATAAATAGTAGGAAAAACGATGAAACGAAACGACACACACCACCACGACAGGACAGGGACGGAAGGAGCGACGAAACACGAGGACACAAAGCAAAGCAGAAAAAAAGAAACCAACCCCACAACACAACACTAACCCCCAAAAAAATTAAAACACTGAAAAAAAAGAGGAAAAAATAAAAACTACTAAAATTAATTAAATATAGTAGATAGATAGTTTAATAGAAAAAAAAAAAAAATCAAGCAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACAAAAAAAGGAAAAAAAAAAATAAAAAAACAAACATAAAAAAAAAAACCAACAATATTAAAAAAGAAAAAAATATAAAATAAACAAAAAAAACCATTAACACAACAAAACAAAAAAATAACAAC'

X_test = strto4rowmx(s)
X_test = np.transpose(X_test)
X_test = X_test[np.newaxis,:]
pred = model.predict(X_test)[0]
print(pred/sum(pred))
#%%
with open('testx_L=5.txt') as f: 
    for seq in f:
        s = strto4rowmx(seq)
        pred = model.predict(s)[0]
        
#%%
resnorm = 0
fx = open('testx_L=5.txt')
fy = open('testy_L=5.txt')
i = 0
for linex,liney in zip(fx,fy):
        y = [float(x) for x in liney.split()]
        s = linex.split()[0]
        s = strto4rowmx(s)
        s = np.transpose(s)
        s = s[np.newaxis,:]
        pred = model.predict(s)[0]
        r = LA.norm(np.subtract(pred,y))
        resnorm = resnorm + r
        i = i+1
        if i%2000 == 0:
            print(i)
resnorm = resnorm/i
"""
