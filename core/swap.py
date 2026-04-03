from core.dateutils import add_months_modfollowing, add_days
from core.schedule import Schedule
from core.curve import Curve
from core.solvedcurve import SolvedCurve
from core.covar import Covar_

from datetime import datetime 
import numpy as np 

class Swap(Covar_): 
    def __init__(self, start: datetime, tenor: int, period_fix: int, period_float: int, tenor_type: str = 'M', fixed_rate=):
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
    
    def __repr__(self):
        format = '%Y-%b-%d'
        return f'Swap: {self.start.strftime(format)} -> {self.end.strftime(format)}\n\n' \
               f'fixed_schedule:\n{self.schedule_fix}\n' \
               f'float_schedule:\n{self.schedule_float}'
    
    
    # dv01 for 10k notional by default
    def analytic_delta(self, curve: Curve, leg: str = 'fix', notional: float = 1e4):
        delta = 0
        for period in getattr(self, f'schedule_{leg}').data:
            period_end = period[1]
            period_dcf = period[2]
            delta += curve[period_end] * period_dcf
        return delta * notional / 10000 # to convert to bp change

    
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
        rate = (curve[self.start] - curve[self.end]) / self.analytic_delta(curve)
        return rate * 100 # return rate in [0-100 scale]

    
    # Paying fixed NPV 
    def npv(self, curve: Curve, fixed_rate: float, notional: float = 1e6):
        """
        npv = (fixed_rate - par_rate) * sum_fixed_leg(vi*ti)
        """
        npv = (self.rate(curve) - fixed_rate) * self.analytic_delta(curve) 
        return npv * notional / 100 # divide as rates were in [0-100 scale]
    

    def risk(self, curve: SolvedCurve, fixed_rate: float, notional: float = 1e6):
        # gradient of PV of the swap wrt. change in market rates S 
        # d P(v)/ds = (dP/dv) .  (dv/ds) 
        # dv/ds we already have curve.grad_s_v 

        # column vector of d npv(swap)/dvi,  1<=i<len_v
        grad_v_P = np.array([
            [self.npv(curve, fixed_rate=fixed_rate, notional=notional).dual.get(f'v{v_idx}', 0)
            for v_idx in range (1, curve.len_v)]
        ]).transpose()

        # dP/ds = dv/ds . dP/dv 
        grad_s_P = np.matmul(curve.grad_s_v, grad_v_P)
        return grad_s_P / 100
