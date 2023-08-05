# -*- coding: utf-8 -*-
"""
Created on Fri Nov 06 13:02:19 2015

@author: konkle
"""
import numpy as np
import scipy.linalg as spl
import matplotlib.pyplot as plt
import time

#k = 128*128  # Windows 7: 460 s, Ubuntu15.10: 
k = 128*64  # Windows 7: 65 s, Ubuntu15.10: 514 s
rank = 256


def get_matrices():
    start0 = time.time()
    cC = np.zeros((k, rank), dtype=np.complex)
    cE = np.zeros((k, k), dtype=np.complex)
    for r in range(rank):
        if rank > 1:
            if r % 10 == 0:
                print(r)
        ccr = np.random.random(k) - 0.5
        cci = np.random.random(k) - 0.5
        cc = ccr + 1j*cci
        cC[:, r] = cc
        cE += cc[:, np.newaxis] * np.conj(cc)
    cE /= np.diag(cE).sum()
    stop = time.time()
    print("matrices are ready after {0} s".format(stop-start0))
    return cC, cE


def solve(cE):
    start1 = time.time()
#    kwargs = dict()
    kwargs = dict(eigvals=(k-10, k-1))
    w, v = spl.eigh(cE, **kwargs)
    stop = time.time()
    print("k={0}; eigenvalue problem has taken {1} s".format(k, stop-start1))
    print('max w={0}, w.sum()={1}'.format(w.max(), w.sum()))
    print("shapes: w={0}, v={1}".format(w.shape, v.shape))
    print(w)

#    rE = np.zeros((k, k), dtype=np.complex)
#    for i in range(k):
#        vi = v[:, i]
#        rE += w[i] * vi[:, np.newaxis] * np.conj(vi)
    rE = np.dot(np.dot(v, np.diag(w)), np.conj(v.T))
    print("diff source--decomposed = {0}".format(np.abs(cE - rE).sum()))

    return w, v


def vplot(w, v, cC, cE):
    fig1 = plt.figure(1, figsize=(8, 6))
    rect2d = [0.1, 0.1, 0.8, 0.8]
    ax = fig1.add_axes(rect2d, aspect='auto')
    vi = v[:, -1]
    ax.plot(np.arange(k), vi.real**2+vi.imag**2, 'r-', lw=0.5)
    norm = (cC[:, 0].real**2 + cC[:, 0].imag**2).sum()**0.5
    cC /= norm
    ax.plot(np.arange(k), (cC[:, 0].real**2 + cC[:, 0].imag**2), 'b-', lw=0.5)

#    fig1.savefig('emittance-{0}{1}.png'.format(aname, fname))
    plt.show()


def vplot2(w, v):
    fig1 = plt.figure(1, figsize=(8, 6))
    rect2d = [0.1, 0.1, 0.8, 0.8]
    ax = fig1.add_axes(rect2d, aspect='auto')
    ax.plot(np.arange(k), np.abs(v[:, -1]))
    ax.plot(np.arange(k), np.abs(v[:, -2]))
#    fig1.savefig('emittance-{0}{1}.png'.format(aname, fname))
    plt.show()

if __name__ == '__main__':
    cC, cE = get_matrices()
    w, v = solve(cE)
    vplot(w, v, cC, cE)
#    vplot2(w, v)

#example:  k = 128*64,  rank = 256
#w[-10:0] =\
#[ 0.00128648  0.0012916   0.00129448  0.00130442  0.0013062   0.00131361
#  0.0013232   0.00132994  0.0013398   0.7509792 ]
