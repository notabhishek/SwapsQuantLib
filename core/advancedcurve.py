from core.solvedcurve import SolvedCurve
from core.bspline import BSpline
from datetime import datetime 
import numpy as np

class AdvancedCurve(SolvedCurve):
    def __init__(self, nodes: dict, interpolation: str, swaps: list, obj_rates: list, t: list, optimization_algo: str = 'guass_newton', w: list = None):
        super().__init__(nodes, interpolation, swaps, obj_rates, optimization_algo, w)
        
        # Knot sequence of dates
        self.t = t 
        self.bs = BSpline(4, t) # 4th order B-splines 
        self.not_iterated = True
    
    # Mixed interpolation 
    def __getitem__(self, date: datetime):
        # Fallback to log_linear interpolation when date < first_knot seq value
        if date <= self.t[0]:
            return super().__getitem__(date)
        else:
            # sum of piecewise polynomial sum of bsplines
            return self.bs.ppev_single(date).__exp__()
    
    def __copy__(self):
        ret = super().__copy__()
        ret.bs = copy(self.bs)
        return ret

    def solve_bspline(self):
        # dates and values to use for caliberating 
        tau = [k for k in self.nodes.keys() if k >= self.t[0]]
        y = [v.__log__() for k, v in self.nodes.items() if k >= self.t[0]]

        # use constraints for 2nd derivative values at endpoints 
        tau.insert(0, self.t[0])
        y.insert(0, 0)

        tau.append(self.t[-1])
        y.append(0)

        # solve bspline, specifying that the 0th and -1th constraint are 2nd dervative values
        # updates the alpha vector internally
        self.bs.bsplsolve(np.array(tau), np.array(y), 2, 2)
    

    # solves spline to udpate piecewise polynomial coefficients 
    # before calculating metrics each time
    def calculate_metrics(self):
        self.solve_bspline()
        return super().calculate_metrics()
    
    # Optimization: First solves the log-linear curve use 
    # LM and then uses guass_newton for next few iterations
    def iterate(self):
        if self.not_iterated:
            w = None if self.W is None else np.diagonal(self.W)
            base_solve = SolvedCurve(self.nodes, self.interpolation, self.swaps, self.obj_rates, optimization_algo=self.algo, w=w)
            print('Basic solve:', base_solve.iterate())
            self.nodes = base_solve.nodes
            self.not_iterated, self.algo = False, 'guass_newton'
        return super().iterate()

    @property
    def grad_s_v(self):
        if getattr(self, 'grad_s_v_', None) is None: 
            self.grad_s_v_numeric(t = self.t)
        return self.grad_s_v_ 