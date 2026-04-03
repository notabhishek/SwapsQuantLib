import numpy as np 
from scipy.stats import norm 

class Covar_:

    """
    Covariance calculation:
        Q[qij] = observed covariance from historical data 
        S = column vector of portfolio Risk using par-rates as fixed rate
            [d npv / ds] 

        Standard deviation of portfolio PNL 
        c = sqrt(S_T . Q . S)
    """
    def covar(self, curve, Q, alpha: float = None):
        S = self.risk(curve=curve)
        S_T = S.transpose()
        c  = np.sqrt(np.matmul(S_T, np.matmul(Q, S)))[0][0]

        if alpha is not None: 
            # find the point X that has P(x <= X) >= alpha
            return norm.ppf(1-alpha) * c

        return c