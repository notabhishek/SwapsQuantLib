"""
We will use numerical algorithms to solve for the discount factors (vi)
using observable market swap rates (S) and an objective function we are
trying to minimize

    Let v = discount factors to solve for (excluding v0 = 1)
        S = known swap rates from market 
        r = corresponding implied rates derived from solved curve (v) 

    v, r, S are column vectors,
            [v0], v0 = 1 
        v = [v1]
            [v2]
        
            [S0]
        S = [S1]
            [S2]
        
            [r0]
        r = [r1]
            [r2]

    Objective function f = min f(v, S), is euclidean distance between market and implied rates
        min f(v, S) = (r-S)^T . (r-S)  [^T is transpose]
        f is a scaler value,

                                        [r0-S0]
        f = [(r0-S0) (r1-S1) (r2-S2)] . [r1-S1]
                                        [r2-S2]
    

    Let Grad_v(f) be the derivatie of f wrt v. [denoted by nabla, inverted triangle in text]

    Grad_v(f) = 2.J.(r-S)             J = dr/dv (Jacobian of r with respect to v, Jij = drj/dvi) 
                        [dr0/dv0  dr1/dv0  dr2/dv0]
    J = Grad_v(r^T) =   [dr0/dv1  dr1/dv1  dr2/dv1]
                        [dr0/dv2  dr1/dv2  dr2/dv2]
"""


import numpy as np 
from core.curve import Curve

class SolvedCurve(Curve):
    def __init__(self, 
                    nodes: dict, 
                    interpolation: str, 
                    swaps: list, 
                    obj_rates: list,
                    optimization_algo = 'levenberg_marquardt'):
        
        super().__init__(interpolation=interpolation, nodes=nodes)

        self.swaps, self.obj_rates, self.algo = swaps, obj_rates, optimization_algo

        self.len_v = len(nodes.keys())
        self.len_s = len(swaps)

        self.n, self.m = len(nodes.keys() - 1), len(swaps)
        
        # column vector of market swap rates
        self.s = np.array([self.obj_rates]).transpose()

        # Damping param lambda used to blend Guass-Newton with Gradient Descent
        self.default_lam = 1000 # used to reset lam after solving 
        self.lamda = self.default_lam


    def calculate_metrics(self):
        # Column vector of implied rates 
        self.r = np.array([[swap.rate(self) for swap in self.swaps]]).transpose()

        # Column vector of discount factors (excluding v0)
        self.v = np.array([[v for v in self.nodes.values()[1:]]]).transpose()

        # error column vector x = (r-s) 
        self.x = self.r - self.s 

        # objective function f = x^T . x
        self.f = np.matmul(self.x.transpose(), self.x)[0][0]

        # Grad_v(f) : gradient of f wrt. vi
        self.grad_v_f = np.array(
            [[self.f.dual[f'v_{i}'] for i in range(1, self.len_v)]]
        )

        # Jacobian J = Grad_v(r^T)
        self.J = np.array(
            [rate.dual[f'v_{j}'] for rate in self.r[:, 0]]
            for j in range(1, self.len_v)
        )
    
    def iterate(self, max_iterations=2000, tolerance =1e-10):
        msg = None # final output msg 
        self.f_prev = 1e10 # previous error 

        for i in range(max_iterations):
            # Calculate r, v, f, grad_v_f, J
            self.calculate_metrics()

            # Check if tolerance reached and we can stop
            if self.f.real < self.f_prev and (self.f_prev - self.f.real) < tolerance:
                msg = f'tolerance reached ({self.algo} after {i} iterations)'
                break 
            
            # Get next set of discount factors using optimization algo 
            v_next = getattr(self, f'update_step_{self.algo}')

            for i, date, v in enumerate(self.nodes.items()):
                if i == 0:
                    continue 
                self.nodes[date] = v_next[i-1, 0]
            self.f_prev = self.f.real 

            # reset lambda 
            self.lam = self.default_lam

            if msg is None:
                msg = f'after max_iters:{max_iterations} ({self.algo}), f: {self.f.real}'
            return msg
        
    def update_step_levenberg_marquardt():
        pass 

    def update_step_guass_newton():
        pass 

    def update_step_gradient_descent():
        pass 
