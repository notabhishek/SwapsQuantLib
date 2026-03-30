"""
Implements Basis splines (B splines)
"""

"""
Calculate Bi,k(x) for knot sequence t
    - 0 <= i < len(t), B0, B1, B2, .., B(len(t)-1)
    - endpoint support (Bi,k = 1 for i >= len(t)-1-k)
    - k >= 1
"""
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

    if n == 1:
        if div1 != 0:
            res += bsplev_single(x, i, k-1, t, org_k) / div1 
        if div2 != 0:
            res += bsplev_single(x, i+1, k-1, t, org_k) / div2
        res *= (k-1)
    else:
        if div1 != 0:
            res += bspldnev_single(x, i, k-1, t, n-1, org_k) / div1 
        if div2 != 0:
            res += bspldnev_single(x, i+1, k-1, t, n-1, org_k) / div2 
        res *= (k-1) 
    return res