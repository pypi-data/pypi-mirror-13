# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import numpy as np
import scipy as sp
from numpy.random import RandomState
from functools import reduce


class DimReduction:
    X = []
    Z = []
    n = []
    p = []
    k = []
    # constructor
    def __init__(self,data,k):
#        assert(istype(data,np.is)
        [self.p,self.n] = data.shape
        self.k = k
        self.X = data
        
        
    # Single Factor Analysis
    def FactorAnalysis(self,nIterations):
        # process data to zero meann
        X = self.X - np.tile(self.X.mean(1),[self.n,1]).T
        
        # initial values for lambda (loading matrix) and psi
        lda = np.random.rand(self.p,self.k)
        psi = np.random.rand(self.p)
        
        # one time computations
        I = np.eye(self.k)

        # initialize array for LogLikelihood archiving in loop iterations
        LL = np.zeros([nIterations,1])
        
        # start loop        
        for i in range(nIterations):
            
            # E_Step()
            ipsi = sp.linalg.inv(np.diag(psi.T))
            fctr1 = sp.linalg.inv(I + reduce(np.dot,[lda.T, ipsi, lda]))
            fctr2 = ipsi - reduce(np.dot,[ipsi,lda,fctr1,lda.T,ipsi])
            beta = reduce(np.dot,[lda.T, fctr2])
            E_zx = reduce(np.dot,[beta,X])
            E_zzx = I - reduce(np.dot,[beta, lda]) + reduce(np.dot,[E_zx,E_zx.T])
                        
#            # log likelihood for iteration i
            # playing with loops
            fctr1 = 0.5 * self.n * self.p * np.log(2*np.pi)
            fctr2 = 0.5 * self.n * sum(np.log(abs(psi)))
            fctr3 = 0.5 * np.sum([reduce(np.dot,[x.T,ipsi,x]) for x in X.T])
            fctr4 = np.sum([reduce(np.dot,[z[0].T,ipsi,lda,z[1]]) for z in list(zip(X.T,E_zx.T))])
            fctr5 = 0.5 * np.sum([reduce(np.dot,[lda.T,ipsi,lda,z]) for z in E_zzx.T])
            LL[i] =  fctr1 - fctr2 - fctr3 + fctr4 - fctr5
            print(LL[i])

            # M_step()            
            fctr1 = reduce(np.dot,[X,E_zx.T])             
            lda = reduce(np.dot,[fctr1, sp.linalg.inv(E_zzx)])                       
            psi = 1/self.n * np.diag(reduce(np.dot,[X, X.T]) - reduce(np.dot,[lda, E_zx, X.T]))
          
        return lda,psi,LL
        

prng = RandomState(1234567890)
data = prng.rand(10,500)
dimReduction = DimReduction(data, 2)
[lmbda,psi,LL] = dimReduction.FactorAnalysis(50)