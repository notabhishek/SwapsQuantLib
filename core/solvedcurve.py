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
        
        # column vector of market swap rates
        self.s = np.array([self.obj_rates]).transpose()

        # Damping param lambda used to blend Guass-Newton with Gradient Descent
        self.default_lam = 1000 # used to reset lam after solving 
        self.lam = self.default_lam


    def calculate_metrics(self):
        # Column vector of implied rates 
        self.r = np.array([[swap.rate(self) for swap in self.swaps]]).transpose()

        # Column vector of discount factors (excluding v0)
        self.v = np.array([[v for v in list(self.nodes.values())[1:]]]).transpose()

        # error column vector x = (r-s) 
        x = self.r - self.s 

        # objective function f = x^T . x
        self.f = np.matmul(x.transpose(), x)[0][0]

        # Grad_v(f) : gradient of f wrt. vi
        self.grad_v_f = np.array(
            [[self.f.dual.get(f'v_{i}') for i in range(1, self.len_v)]]
        ).transpose()

        # Jacobian J = Grad_v(r^T)
        self.J = np.array([
            [rate.dual.get(f'v_{j}',0) for rate in self.r[:, 0]]
            for j in range(1, self.len_v)
        ])
    
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
            step_method = getattr(self, f'update_step_{self.algo}')
            v_next = step_method()

            for i, (date, v) in enumerate(self.nodes.items()):
                if i == 0:
                    continue 
                self.nodes[date] = v_next[i-1, 0]
            self.f_prev = self.f.real 

        # reset lambda 
        self.lam = self.default_lam

        if msg is None:
            msg = f'after max_iters:{max_iterations} ({self.algo}), f: {self.f.real}'
        return msg

    
    def update_step_gradient_descent(self):
        """
        We move in the negative direction of the gradient (Grad_v(f)), 
        the step_size alpha_i is solved by second equation 

        Pro: Stable algorithm
        Con: Slow, takes multiple iterations, especially when closer to target

        vi+1 = vi - aplha_i.Grad_v(f)
        alpha_i = (yi^T (ri-S)) / yi^T.yi, where yi = Ji^T.Grad_v(f)
        """ 
        y = np.matmul(self.J.transpose(), self.grad_v_f)
        alpha = np.matmul(y.transpose(), self.r - self.s) / np.matmul(y.transpose(), y)
        alpha = alpha[0][0].real 

        v_1 = self.v - self.grad_v_f * alpha
        return v_1

    def update_step_guass_newton(self):
        """
        Similar to gradient_descent except we solve for search_direction and step 
        size in a single equation 

        Pro: rate of converagance is faster than grad descent 
        Con: sometimes not numerically stable, especially when initial guess is bad.
             Usually since we have a reasonable good guess (previous solved curve), 
             this is the best aglorithm to use

        vi+1 = vi + delta_i
        where Ji.Ji^T.delta_i = -(1/2).Grad_v(f)  
        """
        A = np.matmul(self.J, self.J.transpose())
        b = -0.5 * self.grad_v_f

        # Solve for A.delta = b
        delta = np.linalg.solve(A, b)

        v_1 = self.v + delta
        return v_1

    def update_step_levenberg_marquardt(self):
        """
        Blend of gradient_descent (stable but slow) with guass_newton(unstable but fast)
        We use lambda (damping parameter) to control the blend
        
        Initially gradient_descent has higher weightage but as we get closer to the target
        we let guass_newton to take over
        
        vi+1 = vi + delta_i

        (Ji.Ji^T + lam * I).delta_i = -(1/2).Grad_v(f)
        """

        # Update damping param 
        self.lam *= (2 if self.f.real > self.f_prev else 0.5)

        a1 = np.matmul(self.J, self.J.transpose())
        a2 = self.lam * np.eye(self.J.shape[0]) 

        A = a1 + a2
        b = -0.5 * self.grad_v_f

        # solve for A*delta = b
        delta = np.linalg.solve(A, b)

        v_1 = self.v + delta
        return v_1
    

    # sensitivity of discount factors wrt. change in market rates
    @property
    def grad_s_v(self):
        if getattr(self, 'grad_s_v_', None) is None:
            self.grad_s_v_numeric()
        return self.grad_s_v_


    # Solve Grad_s(v) numerically using forward finite difference method
    def grad_s_v_numeric(self):
        # grad_s_v i,j is dvi/dvj 
        # 0 <= i < len_s
        # 1 <= j < len_v
        grad_s_v = np.zeros(shape=(self.len_s, self.len_v - 1))
        ds = 1e-3 

        # solved forward curve 
        s_cv_fwd = SolvedCurve(nodes=self.nodes, interpolation=self.interpolation, swaps=self.s, obj_rates=self.obj_rates, optimization_algo='guass_newton')

        # calculate the small change dv in discount factors(vi) for a small change ds in the ith swap rate
        for s_idx in range(self.len_s):
            # reset the dfs and swap market rates 
            s_cv_fwd.nodes, s_cv_fwd.s = self.nodes(), self.s.copy()
            # add small change ds to s_idx'th swap
            s_cv_fwd.s[s_idx, 0] += ds 

            # iterate and solve the curve(we are using guass_newton since we had a good guess(solved curve))
            s_cv_fwd.iterate()

            # calculate dv/ds = (v_new - v)/ds
            dvds_fwd = np.array([v.real for v in (s_cv_fwd.v[:,0] - self.v[:,0])/ds])
            
            # update the change in v for a small change in s_idx market swap rate
            grad_s_v[s_idx, :] = dvds_fwd 
        
        # store this gradient matrix once
        self.grad_s_v_ = grad_s_v
