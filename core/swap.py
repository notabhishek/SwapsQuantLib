from core.dateutils import add_months_modfollowing, add_days
from core.schedule import Schedule
from core.curve import Curve
from core.solvedcurve import SolvedCurve
from core.dual import Dual
from core.covar import Covar_
from core.pca import PCA_

from datetime import datetime 
import numpy as np 

class Swap(Covar_, PCA_): 
    def __init__(self, start: datetime, tenor: int, period_fix: int, 
                 period_float: int, tenor_type: str = 'M', 
                 fixed_rate: float = None, notional: float = None):
        self.start = start 

        # TODO: add tenor_type W, Y
        if tenor_type == 'M':
            self.add_op = add_months_modfollowing
        elif tenor_type == 'D':
            self.add_op = add_days
        else: 
            raise ValueError(f'Only support tenor_type D, M but got {tenor_type}')
        
        self.end = self.add_op(start, tenor)
        self.schedule_fix = Schedule(start, tenor, period_fix, tenor_type=tenor_type)
        self.schedule_float = Schedule(start, tenor, period_float, tenor_type=tenor_type)
        self.tenor = tenor
        self.fixed_rate = fixed_rate
        self.notional = 1e6 if notional is None else notional
    
    def __repr__(self):
        format = '%Y-%b-%d'
        return f'Swap: {self.start.strftime(format)} -> {self.end.strftime(format)}\n\n' \
               f'fixed_schedule:\n{self.schedule_fix}\n' \
               f'float_schedule:\n{self.schedule_float}'
    
    
    # dv01 for 10k notional by default
    def analytic_delta(self, curve: Curve, leg: str = 'fix'):
        delta = 0
        for period in getattr(self, f'schedule_{leg}').data:
            period_end = period[1]
            period_dcf = period[2]
            delta += curve[period_end] * period_dcf
        return delta * self.notional / 10000 # to convert to bp change

    
    def rate(self, curve: Curve):
        """
        vi = discount_factor at i 
        fi = fixing rate at i 
        
        
        float_leg: 
            PV_float = sum(ti * fi * vi)
        fixed_leg:
            PV_fixed = r * sum(ti * vi)

        and we know that 
        vi * (1 + fi*ti) = vi-1  
        =>vi + vi*fi*ti = vi-1
        =>vi*fi*ti = vi-1 - vi
        =>sum(vi*fi*ti) = (v0-v1) + (v1-v2) + .. (vn-1-vn)
        =>sum(vi*fi*ti) = v0-vn
        
        => PV_float = v0-vn 
        par_rate = (v0-vn) / sum(vi * ti),   analytic_delta = sum(vi*ti)
        """
        if self.notional == 0:
            self.notional = 1
            analytic_delta = self.analytic_delta(curve) * 10000 / self.notional
            rate = (curve[self.start] - curve[self.end]) / analytic_delta
            self.notional = 0
        else:
            analytic_delta = self.analytic_delta(curve) * 10000 / self.notional
            rate = (curve[self.start] - curve[self.end]) / analytic_delta
        return rate * 100 # return rate in [0-100 scale]

    
    # Paying fixed NPV 
    def npv(self, curve: Curve):
        """
        npv = (fixed_rate - par_rate) * sum_fixed_leg(vi*ti)
        """
        # set fixed_rate to self.fixed_rate or par rate from curve
        self.set_fixed_rate(fixed_rate=self.fixed_rate, curve=curve)

        npv = (self.rate(curve) - self.fixed_rate) * self.analytic_delta(curve) 
        return npv * 100
    

    def risk(self, curve: SolvedCurve):
        # gradient of PV of the swap wrt. change in market rates S 
        # d P(v)/ds = (dP/dv) .  (dv/ds) 
        # dv/ds we already have curve.grad_s_v 

        # column vector of d npv(swap)/dvi,  1<=i<len_v
        grad_v_P = np.array([
            [self.npv(curve).dual.get(f'v{v_idx}', 0)
            for v_idx in range (1, curve.len_v)]
        ]).transpose()

        # dP/ds = dv/ds . dP/dv 
        grad_s_P = np.matmul(curve.grad_s_v, grad_v_P)
        return grad_s_P / 100

    def set_fixed_rate(self, fixed_rate: float = None, *args, **kwargs):
        if fixed_rate is None:
            fixed_rate = self.rate(*args, **kwargs) 
            if isinstance(fixed_rate, Dual):
                fixed_rate = fixed_rate.real 
        self.fixed_rate = fixed_rate


