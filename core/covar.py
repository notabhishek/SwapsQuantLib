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
    

    """
    Single instrument trade that minimizes variance keeping all other risk positions unchanged
    """
    def covar_smt(self, curve, Q):
        S = self.risk(curve=curve)
        Q_inv = np.diag(-1 / np.diagonal(Q)) # -1/qij
        return np.matmul(Q_inv, np.matmul(Q, S))

    """
    the change in portfolio standard deviation, delta_c if the i'th covar_smt was executed
        i.e. The impact on c by ith VaR minimising trade 

    delta_ci = c_i_min - c 
    """
    def covar_smt_impact(self, curve, Q):
        S, c = self.risk(curve), self.covar(curve, Q)
        S_trade = self.covar_smt(curve, Q)

        S_trade_diag = np.diag(S_trade[:, 0])

        # i'th column is the portfolio risk after executing the i'th VaR minimising trade
        S_min = S + S_trade_diag

        c_impact = np.sqrt(np.matmul(S_min.T, np.matmul(Q, S_min))) - c
        return np.diagonal(c_impact)[:, np.newaxis]

    """
    Allocation of VaR to each risk bucket
    """
    def covar_alloc(self, curve, Q):
        S, c = self.risk(curve), self.covar(curve, Q)
        S_diag = np.diag(S[:, 0])
        return (1 / c) * np.matmul(S_diag, np.matmul(Q, S))

    """
    Multi instrument VaR minimisation
    Select a subset of instruments and figure out the risks to execute in each of those to minimise Var
    """
    def covar_mmt(self, curve, Q, instruments):
        S = self.risk(curve=curve)
        # risks Si for 'instruments'
        S_hat = S[instruments, :]
        # covariance of 'instruments' with all pillars (M x N)
        Q_hat = Q[instruments, :]
        # covariance of 'instruments' with 'instruments'
        Q_hat_hat = Q_hat[:,instruments]

        # Risks to trade for each instrument
        # S_trade_hat * Q_hat_hat = - Q_hat . S
        S_trade_hat = np.linalg.solve(Q_hat_hat, -np.matmul(Q_hat, S))
        
        S_trade = np.zeros_like(S)
        for inst, S_trade_i in zip(instruments, S_trade_hat[:,0]):
            S_trade[inst, 0] = S_trade_i

        return S_trade

    # impact on c (c_new - c) after executing VaR minimising trades on instruments
    def covar_mmt_impact(self, curve, Q, instruments):
        S, c = self.risk(curve), self.covar(curve, Q)
        S_min = S + self.covar_mmt(curve, Q, instruments)
        return np.sqrt(np.matmul(S_min.T, np.matmul(Q, S_min)))[0, 0] - c