import os
os.environ["CUDA_DEVICE_ORDER"]="PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"]="3"
import tensorflow as tf
physical_devices = tf.config.experimental.list_physical_devices('GPU')
assert len(physical_devices) > 0, "Not enough GPU hardware devices available"
config = tf.config.experimental.set_memory_growth(physical_devices[0], True)

from tensorflow import keras
from tensorflow.keras import layers
import h5py
import numpy as np

n = 1024
L = 5

inputs = keras.Input(shape=(n, 4))
x = inputs

x = layers.Conv1D(filters=32, kernel_size=7, strides=4, padding="same")(x)
x = layers.BatchNormalization(axis=2)(x)
x = layers.Activation('relu')(x)
x = layers.MaxPooling1D(pool_size=4, strides=4)(x)

x = layers.Conv1D(filters=64, kernel_size=3, strides=2, padding="same")(x)
x = layers.BatchNormalization(axis=2)(x)
x = layers.Activation('relu')(x)

x = layers.Conv1D(filters=128, kernel_size=3, strides=2, padding="same")(x)
x = layers.BatchNormalization(axis=2)(x)
x = layers.Activation('relu')(x)
# x = layers.AveragePooling1D(pool_size=4, strides=4)(x)
x = layers.GlobalAvgPool1D()(x)

x = layers.Flatten()(x)
outputs = layers.Dense(units=L, activation=None)(x)

model = keras.Model(inputs=inputs, outputs=outputs)
model.summary()

model.compile(optimizer="SGD", loss="mean_squared_error")
print('model compiled')
# exit()
sq = 1
datafile_name = f"up{sq}SequenceDupDel"
model_name = f'trainedmodel/m{sq}'
fX = h5py.File(f'data/{datafile_name}.trainX', 'r')
fY = h5py.File(f'data/{datafile_name}.trainY', 'r')
ftX = h5py.File(f'data/{datafile_name}.testX', 'r')
ftY = h5py.File(f'data/{datafile_name}.testY', 'r')
X_index = list(fX.keys())
Y_index = list(fY.keys())
Xt_index = list(ftX.keys())
Yt_index = list(ftY.keys())

print(f'training start {datafile_name}')
lr_boost = 100
for i in range(len(X_index)):
    xindex = X_index[i]
    yindex = Y_index[i]
    print(xindex)
    trainX = np.array(fX[xindex])
    trainY = lr_boost * np.array(fY[yindex])
    trainY[:, 0] *= 10
    reduce_lr = keras.callbacks.ReduceLROnPlateau(monitor='val_loss', factor=0.2, mode="min",
                                                  patience=3, min_lr=0.00001, min_delta=0.01)
    model.fit(trainX, trainY, batch_size=1024, epochs=10, validation_split=0.2,
              callbacks=[reduce_lr])

    testX = np.array(ftX[xindex])
    testY = lr_boost * np.array(ftY[yindex])
    # model = keras.models.load_model(model_name)
    predY = model.predict(testX)
    predY[:, 0] /= 10
    with np.printoptions(precision=4, suppress=True):
        for i in range(5):
            print("ground truth", testY[i])
            print("prediction  ", predY[i] * lr_boost / np.sum(predY[i]))
            print('----------------')
    mse = np.mean(np.mean((predY - testY) ** 2, axis=1))
    print(f"mse {mse}")
    break

model.save(model_name)
