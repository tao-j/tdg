# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 21:15:19 2021

@author: hl2nu

mutation functions
"""
import random 
import numpy as np

def substitute(s):
    if len(s)>0:
        i = random.randint(0,len(s)-1)
        p = random.randint(1,3)
        s[i] = s[i] + p
        s[i] = s[i]%4
    return s


def tandemdup(s,l):
    if len(s)>=l:
        i = random.randint(0,len(s)-l)
        s = np.insert(s,i+l,s[i:i+l])
    return s   

def delete(s):
    if len(s)>1:
        i = random.randint(0,len(s)-1)
        s = np.delete(s,i)
    return s