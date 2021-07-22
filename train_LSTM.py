# -*- coding: utf-8 -*-
"""
Created on Wed Feb 24 10:51:13 2021

@author: hl2nu
"""
from tensorflow import keras
from tensorflow.keras import layers
import h5py
import numpy as np
import tensorflow as tf

outputsize = 11

inputs = keras.Input(shape=(None, 4))
x = layers.Conv1D(filters=512, kernel_size=10, activation="relu")(inputs)
#x = layers.AveragePooling1D(pool_size=10,strides = 10)(x)
print(x.shape)
x = layers.AveragePooling1D(pool_size=3, strides=3)(x)
print(x.shape)
x = layers.Conv1D(filters=128, kernel_size=5, activation="relu")(x)
print(x.shape)
x = layers.GlobalAveragePooling1D()(x)
x = layers.Flatten()(x)
#print(x.shape)
x = layers.Dense(units=outputsize, activation="relu")(x)

#outputs = layers.LSTM(L+1)(inputs)
#x = layers.Bidirectional(layers.LSTM(outputsize, return_sequences=True), merge_mode = "ave" )(x)
#print(x.shape)
outputs = layers.Softmax()(x)
#x = layers.Bidirectional(layers.LSTM(50))(x)
#x = layers.Flatten()(x)
#print(x.shape)
#outputs = layers.Dense(units = L+2, activation = "relu")(x)
model = keras.Model(inputs=inputs, outputs=outputs)
model.summary()

#%%
model.compile(optimizer="SGD", loss="mean_squared_error")
print('model compiled')

#%%

fX = h5py.File('data/Xtrain_toy_period[1,2,3]_del', 'r')
X_index = list(fX.keys())

fY = h5py.File('data/Ytrain_toy_period[1,2,3]_del', 'r')
Y_index = list(fY.keys())

print('training start')

#%%
for i in range(len(X_index)):
    xindex = X_index[i]
    print(xindex)
    yindex = Y_index[i]
    print(yindex)
    trainX = np.array(fX[xindex], dtype="int8")
    trainY = np.array(fY[yindex], dtype="float16")
    #trainY = np.pad(trainY, ((0,0),(0,6)))
    model.fit(trainX, trainY, batch_size=5, epochs=2)

model.save('trainedmodel/model_LSTM_del_toy')
fX.close()
fY.close()

#%% retrain
modelname = "trainedmodel/model_LSTM_toy"
model = keras.models.load_model(modelname)

fX = h5py.File('data/Xtrain_toy_period2', 'r')
X_index = list(fX.keys())

fY = h5py.File('data/Ytrain_toy_period2', 'r')
Y_index = list(fY.keys())

print('training start')

for i in range(1, len(X_index)):
    xindex = X_index[i]
    print(xindex)
    yindex = Y_index[i]
    print(yindex)
    trainX = np.array(fX[xindex], dtype="int8")
    trainY = np.array(fY[yindex], dtype="float16")
    trainY = np.pad(trainY, ((0, 0), (0, 3)))
    model.fit(trainX, trainY, batch_size=5, epochs=2)

model.save('trainedmodel/model_LSTM_toy')
