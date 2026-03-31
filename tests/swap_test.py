from core.swap import Swap 
from core.curve import Curve 
from datetime import datetime

curve = Curve(interpolation='log_linear', nodes = {
    datetime(2022, 1, 1) : 1.00,
    datetime(2022, 4, 1) : 0.9975,
    datetime(2022, 7, 1) : 0.9945,
})

swap = Swap(datetime(2022, 2, 14), tenor=4, period_fix=12, period_float=1)

print(swap)

print(f'par_rate              = {swap.rate(curve)}')
print(f'dv01 for 1e9 notional = {swap.analytic_delta(curve, notional=1e9)}')
print(f'npv  for 1e9 notional = {swap.npv(curve, fixed_rate=1.15, notional=1e9)}')

