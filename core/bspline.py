"""
Implements Basis splines (B splines)
"""

"""
Calculate Bi,k(x) for knot sequence t
    - 0 <= i < len(t), B0, B1, B2, .., B(len(t)-1)
    - endpoint support (Bi,k = 1 for i >= len(t)-1-k)
    - k >= 1
"""

import numpy as np 
import core.linalg as linalg 
from datetime import timedelta

def bsplev_single(x, i, k, t, org_k = None):
    # Endpoint support 
    org_k = org_k or k # number of times the last knot point is repeated

    # B0,k(t[0]) = 1
    if i == 0 and x == t[0]: 
        return 1
    # Bu,k(t[-1]) = 1, for u >= len(t)-1-org_k
    elif i >= (len(t) - 1 - org_k) and x == t[-1]:
        return 1
    

    ## Use recursion to build kth spline from k-1th splines
    if k == 1:
        #        {1, t[i] <= x < t[i+1]}
        # Bi,1 = {0, otherwise         }
        return 1 if (t[i] <= x < t[i+1]) else 0
    else:
        left, right = 0, 0
        if t[i] != t[i+k-1]:
            left = ((x - t[i]) / (t[i+k-1] - t[i])) * bsplev_single(x, i, k-1, t)
        if t[i+1] != t[i+k]:
            right = ((t[i+k] - x) / (t[i+k] - t[i+1])) * bsplev_single(x, i+1, k-1, t)
        return left + right

"""
Calculate n'th derivative of Bi,k at x for given knot seq t

d(Bi,k,t)/dx = (k-1) *  [P - Q]
where,
    P = Bi,k-1,t(x) / (t[i+k-1] - t[i])
    Q = Bi+1,k-1,t(x) / (t[i+k] - t[i+1]) 
"""
def bspldnev_single(x, i, k, t, n, org_k = None):
    if n == 0:
        return bsplev_single(x, i, k, t)
    elif k == 1 or n >= k:
        return 0

    org_k = org_k or k 
    res, div1, div2 = 0, t[i+k-1]-t[i], t[i+k]-t[i+1]    

    if isinstance(div1, timedelta):
        div1 = div1 / timedelta(days=1)
    if isinstance(div2, timedelta):
        div2 = div2 / timedelta(days=1)

    if n == 1:
        if div1 != 0:
            res += bsplev_single(x, i, k-1, t, org_k) / div1 
        if div2 != 0:
            res -= bsplev_single(x, i+1, k-1, t, org_k) / div2
        res *= (k-1)
    else:
        if div1 != 0:
            res += bspldnev_single(x, i, k-1, t, n-1, org_k) / div1 
        if div2 != 0:
            res -= bspldnev_single(x, i+1, k-1, t, n-1, org_k) / div2 
        res *= (k-1) 
    return res

class BSpline: 
    def __init__(self, k, t):
        self.t, self.k, self.n = t, k, len(t) - k

    # Evaluate Bi,k,t(x) for an array of x
    def bsplev(self, x, i, otypes=['float64']):
        func = np.vectorize(bsplev_single, excluded=['k', 't'], otypes=otypes) 
        return func(x, i=i, k=self.k, t=self.t)
    
    # Evaluate dn/dx (Bi,k,t(x)) for an array of x
    def bspldnev(self, x, i, n, otypes=['float64']):
        func = np.vectorize(bspldnev_single, excluded=['k', 't'], otypes=otypes)
        return func(x, i=i, k=self.k, t=self.t, n=n)
    
    """
    build splien colocation matrix and solve 
    
    tau = T = observed market data inputs

            [B0,k(T0)       B1,k(T0)    ...     Bz,k(T0)]
    B_ji =  [B0,k(T1)       B1,k(T1)    ...     Bz,k(T1)]
            [B0,k(T2)       B1,k(T2)    ...     Bz,k(T2)]

    Except, at boundary conditions, 1st row and last row 
    we want to be able to specify nth derivative of spline equals 
    some expected value and solve for coefficients using that
    """
    def bsplmatrix(self, tau, left_n=0, right_n=0):
        B_ji = np.zeros(shape=(len(tau), self.n))

        for i in range(self.n):
            B_ji[0,i] = bspldnev_single(tau[0], i, self.k, self.t, left_n)
            B_ji[1:-1, i] = self.bsplev(tau[1:-1], i=i)
            B_ji[-1,i] = bspldnev_single(tau[-1], i, self.k, self.t, right_n)
        return B_ji
    
    def bsplsolve(self, tau, y, left_n, right_n):
        """Evaluate the B-Spline coeffs `c` that parametrise the pp."""
        if len(tau) != self.n:
            raise ValueError(f"`tau` must have length equal to pp dimension, "
                             f"`tau`: {len(tau)}, `n`: {self.n}")
        if len(tau) != len(y):
            raise ValueError(
                f"`tau` and `y` must have the same length, "
                f"`tau`: {len(tau)}, `y`: {len(y)}"
            )
        B_ji = self.bsplmatrix(tau, left_n, right_n)

        alpha = linalg.solve(B_ji, y[:, np.newaxis])
        self.alpha = alpha[:, 0]
    
    # Evaluate the piecewise polynomial spline value for given x value
    def ppev_single(self, x):
        sum = 0
        for i, alpha_ in enumerate(self.alpha):
            sum += alpha_ * bsplev_single(x, i, self.k, self.t)
        return sum
