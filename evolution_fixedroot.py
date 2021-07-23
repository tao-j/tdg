# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 21:17:01 2021

@author: hl2nu

data generation_fixed root
"""
from scipy.stats import multinomial
import numpy as np
from mutations import substitute, tandemdup, delete
from random import uniform

def sample_multinomial(P):
    rnd = np.random.rand()
    return np.sum(rnd >= np.cumsum(P))


def generate_root(s, n, P):
    while len(s) < n:
        k = sample_multinomial(P)
        if k == 0:
            s = delete(s)
        elif k == 1:
            s = substitute(s)
        else:
            s = tandemdup(s, k - 1)
    return s[0:n]


def generate_root_Nmut(x, n, P):
    s = x
    dist = multinomial(1, P)  # mutation dist
    for mut in range(n):
        k = np.argmax(dist.rvs())
        if k == 0:
            s = delete(s)
        elif k == 1:
            s = substitute(s)
        else:
            s = tandemdup(s, k - 1)
    return s


def generate_root_nodel(x, n, P):
    s = x
    dist = multinomial(1, P)  # mutation dist
    while len(s) < n:
        k = np.argmax(dist.rvs())
        if k == 0:
            s = substitute(s)
        else:
            s = tandemdup(s, k)
    return s[0:n]


def generate_root_nosub(x, n, P):
    s = x
    dist = multinomial(1, P)  # mutation dist
    while len(s) < n:
        k = np.argmax(dist.rvs())
        if k == 0:
            s = delete(s)
        else:
            s = tandemdup(s, k)
    return s[0:n]


def seqto4rowmx(s):
    m = np.zeros((4, len(s)))
    for i in range(len(s)):
        m[s[i], i] = 1
    return np.transpose(m)


def strto4rowmx(s):
    alphabet = ['A', 'C', 'G', 'T']
    m = np.zeros((4, len(s)))
    for i in range(len(s)):
        symbol = s[i]
        vec = [int(symbol == alphabet[i]) for i in range(4)]
        m[:, i] = vec
    return m


def randdist(n):
    P = np.random.random_sample(size=n)
    return P / sum(P)


def randdist_del(n, alpha):
    P = np.random.random_sample(size=n)
    P[0] = alpha * P[0]
    P[1:len(P)] = (1 - P[0]) * P[1:len(P)] / sum(P[1:len(P)])
    return P


def randdist_period(period, n):
    P_sub = uniform(0, 0.5)
    P_dup = np.zeros(n)
    for i in range(n):
        P_dup[i] = uniform(2**-(i + 1), 2**-i)
    P_dup = (1 - P_sub) * P_dup / sum(P_dup)
    P = np.zeros(1 + n * period)
    P[0] = P_sub
    for i in range(n):
        P[(i + 1) * period] = P_dup[i]
    return P


def randdist_period_size(period, n, outputsize):
    P_sub = uniform(0, 0.5)
    P_dup = np.zeros(n)
    for i in range(n):
        P_dup[i] = uniform(2**-(i + 1), 2**-i)
    P_dup = (1 - P_sub) * P_dup / sum(P_dup)
    P = np.zeros(outputsize)
    P[0] = P_sub
    for i in range(n):
        P[(i + 1) * period] = P_dup[i]
    return P / sum(P)


def randdist_period_size_del(period, n, outputsize):
    P_del = uniform(0, 0.1)
    P_sub = uniform(0, 0.5 - P_del)
    P_ind = P_del + P_sub
    P_dup = np.zeros(n)
    for i in range(n):
        P_dup[i] = uniform(2**-(i + 1), 2**-i)
    P_dup = (1 - P_ind) * P_dup / sum(P_dup)
    P = np.zeros(outputsize)
    P[0] = P_del
    P[1] = P_sub
    for i in range(n):
        P[(i + 1) * period + 1] = P_dup[i]
    return P / sum(P)
