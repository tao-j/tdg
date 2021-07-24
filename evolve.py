# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 21:17:01 2021

@author: hl2nu

data generation_fixed root
"""
import numpy as np
from random import uniform
import random


def sample_multinomial(cumsum_p):
    rnd = random.random()
    return np.sum(rnd >= cumsum_p)


class Mutable():
    def substitute(self):
        i = random.randint(0, self.len - 1)
        p = random.randint(1, 3)
        # print(f"sub {i} + {p}")
        # print(self.x[:self.len])
        self.x[i] = (self.x[i] + p) % 4
        # print(self.x[:self.len])

    def tandemdup(self, l):
        i = random.randint(0, self.len - l)
        # print(f"ins {i} {l}")
        # print(self.x[:self.len])
        self.x[i + l:self.len + l] = self.x[i:self.len]
        self.len += l
        # print(self.x[:self.len])

    def delete(self):
        i = random.randint(0, self.len - 1)
        # print(f"del {i}")
        # print(self.x[:self.len])
        if i != self.len - 1:
            self.x[i:self.len-1] = self.x[i+1:self.len]
        self.len -= 1
        # print(self.x[:self.len])


class Sequence(Mutable):
    def __init__(self, root, target_len, P):
        self.target_len = target_len
        self.len = len(root)
        self.x = np.empty(target_len + len(P), dtype=np.int64)
        self.x[:self.len] = root
        self.P = P
        self.cumsum_p = np.cumsum(P)


class SequenceDupDel(Sequence):
    def evolve(self):
        while self.len < self.target_len:
            k = sample_multinomial(self.cumsum_p)
            if k == 0:
                if self.len > 1:
                    self.delete()
            elif k == 1:
                self.substitute()
            elif self.len >= k - 1:
                self.tandemdup(k - 1)
        return self.x[:self.target_len]

    @staticmethod
    def gen_dist(period, n_period, outputsize):
        P_del = uniform(0, 0.1)
        P_sub = uniform(0, 0.5 - P_del)
        P_ind = P_del + P_sub
        P_dup = np.zeros(n_period)
        for i in range(n_period):
            P_dup[i] = uniform(2 ** -(i + 1), 2 ** -i)
        P_dup = (1 - P_ind) * P_dup / sum(P_dup)
        P = np.zeros(outputsize)
        P[0] = P_del
        P[1] = P_sub
        for i in range(n_period):
            P[(i + 1) * period + 1] = P_dup[i]
        return P / sum(P)


class SequenceDup(Sequence):
    def evolve(self):
        while self.len < self.target_len:
            k = sample_multinomial(self.cumsum_p)
            if k == 0:
                self.substitute()
            elif self.len >= k:
                self.tandemdup(k)
        return self.x[:self.target_len]

    @staticmethod
    def gen_dist(period, n, outputsize):
        P_sub = uniform(0, 0.5)
        P_dup = np.zeros(n)
        for i in range(n):
            P_dup[i] = uniform(2 ** -(i + 1), 2 ** -i)
        P_dup = (1 - P_sub) * P_dup / sum(P_dup)
        P = np.zeros(outputsize)
        P[0] = P_sub
        for i in range(n):
            P[(i + 1) * period] = P_dup[i]
        return P / sum(P)


def generate_root_Nmut(s, n, P):
    for mut in range(n):
        k = sample_multinomial(P)
        if k == 0:
            s = delete(s)
        elif k == 1:
            s = substitute(s)
        else:
            s = tandemdup(s, k - 1)
    return s


def generate_root_nosub(s, n, P):
    while len(s) < n:
        k = sample_multinomial(P)
        if k == 0:
            s = delete(s)
        else:
            s = tandemdup(s, k)
    return s[0:n]


def seqto4rowmx(s):
    m = np.zeros((len(s), 4))
    for i in range(len(s)):
        m[i, s[i]] = 1
    return m


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
        P_dup[i] = uniform(2 ** -(i + 1), 2 ** -i)
    P_dup = (1 - P_sub) * P_dup / sum(P_dup)
    P = np.zeros(1 + n * period)
    P[0] = P_sub
    for i in range(n):
        P[(i + 1) * period] = P_dup[i]
    return P
