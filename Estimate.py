# -*- coding: utf-8 -*-
"""
Created on Sat Mar 13 11:55:59 2021

@author: hl2nu
"""
from predict import predict

Filenamex = "Xtest_L=3_1"
Filenamey = "Ytest_L=3_1"
modelname = "model_conv_L=3"

res = predict(Filenamex, Filenamey, modelname)
print(res)
