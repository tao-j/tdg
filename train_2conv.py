# -*- coding: utf-8 -*-
"""
Created on Thu Feb 18 19:45:24 2021

@author: hl2nu
"""

from tensorflow import keras
from tensorflow.keras import layers
import h5py
import numpy as np

n = 1000
L = 5

inputs = keras.Input(shape = (n,4))
x = layers.Conv1D(filters = 500,kernel_size = 10, activation = "relu")(inputs)
x = layers.AveragePooling1D(pool_size=10,strides = 10)(x)
#x = layers.GlobalAveragePooling1D()(x)
x = layers.Conv1D(filters =100 ,kernel_size = 10, activation = "relu")(x)
x = layers.AveragePooling1D(pool_size=3,strides = 3)(x)
#x = layers.Bidirectional(layers.LSTM(150,return_sequences=True))(x)
#x = layers.Bidirectional(layers.LSTM(150))(x)
x = layers.Flatten()(x)
#print(x.shape)
outputs = layers.Dense(units = L+1, activation = "relu")(x)
model_1 = keras.Model(inputs = inputs,outputs = outputs)
model_1.summary()

#%%
model_1.compile(optimizer ="SGD",loss="mean_squared_error")
print('model compiled')

fX = h5py.File('X_train_nodel_L=5','r')
X_index = list(fX.keys())

fY = h5py.File('Y_train_nodel_L=5','r')
Y_index = list(fY.keys())

print('training start')

for i in range(len(X_index)):
    xindex = X_index[i]
    print(xindex)
    yindex = Y_index[i]
    trainX = np.array(fX[xindex])
    trainY = np.array(fY[yindex])
    model_1.fit(trainX, trainY, batch_size = 1, epochs=2)
    

model_1.save('model_conv_nodel_L=5')
