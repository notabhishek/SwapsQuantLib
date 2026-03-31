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
    
    # Mixed interpolation 
    def __getitem__(self, date: datetime):
        # Fallback to log_linear interpolation when date < first_knot seq value
        if date <= self.t[0]:
            return super().__getitem__(date)
        else:
            # sum of piecewise polynomial sum of bsplines
            return self.bs.ppev_single(date).__exp__()
    
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