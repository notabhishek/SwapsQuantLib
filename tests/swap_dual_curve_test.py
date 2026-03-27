from core.swap import Swap 
from core.curve import Curve 
from datetime import datetime
from core.dual import Dual

curve = Curve(interpolation='log_linear', nodes = {
    datetime(2022, 1, 1) : Dual(1.00, {'v0' : 1}),
    datetime(2022, 4, 1) : Dual(0.9975, {'v1' : 1}),
    datetime(2022, 7, 1) : Dual(0.9945, {'v2' : 1}),
})

swap = Swap(datetime(2022, 2, 14), tenor_m=4, period_fix_m=12, period_float_m=1)

print(swap)

print(f'par_rate              = {swap.rate(curve)}')
print(f'dv01 for 1e9 notional = {swap.analytic_delta(curve, notional=1e9)}')
print(f'npv  for 1e9 notional = {swap.npv(curve, fixed_rate=1.15, notional=1e9)}')

