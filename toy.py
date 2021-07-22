# -*- coding: utf-8 -*-
"""
Created on Tue Feb 23 19:59:44 2021

@author: hl2nu
"""
import numpy as np
from evolution_fixedroot import generate_root_nodel, seqto4rowmx, strto4rowmx
from tensorflow import keras

model = keras.models.load_model('trainedmodel/model_conv_nodel_L=5')
print('model loaded')

#%% input an ACGT sequence and run the prediction
s = 'CGTTGTTTTCGTTGTTTTTCTCGTTTTTCTCGTTTTTCTCGTTTTTCTCGTTTTTCTCGTTTTTCTCGTTTTTCTCGTTTTTCTCGTTCTTCTCGTTCTCGTTCTCCTCGTTCTCGTTTTTCTTGTTTTTTTTCTTGTTTTTCTTGTTCTTGTTTTTCTTCTTTTTCTTCATTTTCTTCATTTTCTTCATTTTCTTCATTTTCTTCATTTTCATTTTCTTCATTTCCATTTCCTCCATTTCCTCCATTTCCTCCATTTCCATTTCCTTTTCCTCCGCCGTTTTCTACTTTTTCTACTTTTTTTACTACTTTTTTTTCTACTACTACGTCTACTACGACTACGTTTACTACGTTTACTACGTTTACTACGTTTACTACGTTTACTACGTTTACTACGACGTTTACTACGTTTACTACGTTTACTACGTTTACTACGTTTACTACGTTTACTACTACTACTACTACGTCTACTACGTTTACTACGTTTACTACGTTTTTTACGACGATTTCGACGTTTTCTACGTTTTCTACGTTTTCTACGTTTTCTACGTTTTCTACGTCGTCTACTACTACTACGACTACGACGTCTACGTCTACTACGTCGTCGTCGTCGTCGTCGTCGTCGTCGTCGTCGTCGTTTTCGTCGTTTTCGTCGTTTTCGTCGTTTTCTACGTCTTCTACTTCTACGTCGTCTTCTACGTCTTCTTCTACGTCTTGTACGTCTTCTACGTCTTCGTCTTCTACGTCGTCTTCTACGTCTTCTACGTCTTCTACGTCTTCTACGTCTTCTACGTCTTCTACGTCTTCTACGTCTTCTACTTCTACTTCTTCTACTACGTCTACTACGTCTATTACGTCTATTACGTCTACTACGTCTACTACTACTACTACTACTACTACTACTACTACTACTACTACTACTACTACTACTACTACTACTACTACTACTACTACTACTACTACTACTACTACTACTACTACTACTACTGCGTCTACTACGT'
X_test = strto4rowmx(s)
X_test = np.transpose(X_test)
X_test = X_test[np.newaxis,:]
pred = model.predict(X_test)[0]
print(pred/sum(pred))


#%% take a close look at the model
from tensorflow import keras
model = keras.models.load_model(modelname)
model.summary()

#%% take a close look at the dataset
import h5py
fY = h5py.File('Ytest_L=3_1','r')
Y_index = list(fY.keys())
print(fY[Y_index[0]])

#%% train a simple LSTM model
from tensorflow import keras
from tensorflow.keras import layers
import h5py
import numpy as np
from evolution_fixedroot import randdist, seqto4rowmx, generate_root_nodel

#%% define an LSTM network
L = 3

inputs = keras.Input(shape = (None,4))
x = layers.Bidirectional(layers.LSTM(4, return_sequences=True) )(inputs)
x = layers.Bidirectional(layers.LSTM(4))(x)
outputs = layers.Dense(4)(x)
model = keras.Model(inputs = inputs,outputs = outputs)
model.summary()

p_td1 = 0.5 #lower bound of td of 1 period
p_td2 =0.25 #lower bound of td of 2 periods

period = 1

#%%
model.compile(optimizer ="SGD",loss="mean_squared_error")
print('model compiled')

#%% import h5py file and train 
fx = h5py.File("data/Xtrain_toy","r")
fy = h5py.File("data/Ytrain_toy","r")

for datasetx, datasety in zip(list(fx.keys()) , list(fy.keys())):
    print("dataset:\n")
    print(datasetx)
    print(datasety)
    X = np.array(fx[datasetx], dtype = "int8")
    Y = np.array(fy[datasety], dtype = "float16")
    model.fit(X,Y,  epochs = 2)
fx.close()
fy.close()
#%%
fx = h5py.File("data/Xtrain_toy","r")
fy = h5py.File("data/Ytrain_toy","r")

X = np.array(fx["X_1000"], dtype = "float16")
Y = np.array(fy["Y_1000"])
model.fit(X,Y,epochs = 2)
#%%
Ndist = 5000 # num of dists 
Nsample = 5 # num of samples per dist
slen = [ 200,400,600,800,1000] # num of mutations
print("training begins!")
for length in slen:
    print(length)
    X_len = []
    Y_len = []
    for dist in range(Ndist):
        P = randdist(L+1)
        X_len_dist = []
        Y_len_dist = []
        if dist % 1000 == 0:
            print(dist)
        for j in range(Nsample):
            x_root = np.random.randint(4,size = 10)
            x = generate_root_nodel(x_root,length,P)
            x = seqto4rowmx(x)
            X_len_dist.append(x)
            Y_len_dist.append(P)
        X_len = X_len + X_len_dist
        Y_len = Y_len + Y_len_dist
    model.fit(np.array(X_len), np.array(Y_len), epochs=2,verbose = 1)  
#%% run a small toy test
from evolution_fixedroot import randdist_period, generate_root_nodel, seqto4rowmx, randdist_period_size,generate_root
from tensorflow import keras
import numpy as np
from numpy import linalg as LA
modelname = "trainedmodel/model_LSTM_toy"
model = keras.models.load_model(modelname)
#%%
period = 2
outputsize = 10
n = 3
l = 1000

P = randdist_period_size(period, n, outputsize)
x_root = np.random.randint(4,size = 10) # define a random root
x = generate_root(x_root,l,P)
x= seqto4rowmx(x)
x = x[np.newaxis,:]

pred = model.predict(x)[0]
pred = pred/sum(pred)
print(np.round(pred,3))
print(np.round(P,3))
#print(LA.norm( pred[0:len(P+1)]-P))


