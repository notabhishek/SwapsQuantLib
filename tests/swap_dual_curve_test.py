from core.swap import Swap 
from core.curve import Curve 
from datetime import datetime, timedelta
from core.dual import Dual

def value_test_swap(curve: Curve): 
    swap = Swap(datetime(2022, 2, 14), tenor_m=4, period_fix_m=12, period_float_m=1)

    print(swap)

    print(f'par_rate              = {swap.rate(curve)}')
    print(f'dv01 for 1e9 notional = {swap.analytic_delta(curve, notional=1e9)}')
    print(f'npv  for 1e9 notional = {swap.npv(curve, fixed_rate=1.15, notional=1e9)}')

# Using dual numbers to build swap curve and also get sensitivities 
# to vi (discount factors at node points) when calculating 
# par_rate, dv01, npv
def swap_dual_curve():
    t0, t1, t2 = datetime(2022, 1, 1), datetime(2022, 4, 1), datetime(2022, 7, 1)
    v0, v1, v2 = 1.00, 0.9975, 0.9945

    nodes = {
        t0 : Dual(v0, {'v0' : 1}),
        t1 : Dual(v1, {'v1' : 1}),
        t2 : Dual(v2, {'v2' : 1}),
    }

    curve = Curve(interpolation='log_linear', nodes=nodes)
    value_test_swap(curve)
    

# Building on to previous example, this one builds swap curves as above, but we 
# also calculate sensitivites to equivalent Zero rates Zi
"""
Let vi = discount factor t0 to ti 
Let Di = day count fraction for t0 to ti
Let Zi = equivalent CC zero coupon rate for t0 to ti

We know, 
    vi = e ** (-Zi.Di) [discounting]

    dvi/dZi = (e**(-Zi.Di)) . (-Di) = -vi.Di -------------(1)

So if we want to calculate df / dZi
    df/dZi = (df/dvi) * (dvi/dZi)   [and df/dvi we already calculated in previous curve (sensitivity to discount factors at node points)]

    substituting equation (1)
    => df/dZi = -vi.Di . (df/dvi)

    we can parameterize our dual numbers with coef (-vi.Di) for Zi tag
"""
def swap_dual_curve_zero_rate_sensitivities():
    t0, t1, t2 = datetime(2022, 1, 1), datetime(2022, 4, 1), datetime(2022, 7, 1)
    v0, v1, v2 = 1.00, 0.9975, 0.9945
    dcf_conv = timedelta(days=365)
    D0, D1, D2 = 0, (t1 - t0)/dcf_conv, (t2-t0)/dcf_conv
    bp_scale = 1e-4 # We want sensitivities to 1bp shift of zero rates
    nodes = {
        t0 : Dual(v0, {'v0' : 1, 'Z0' : -v0 * D0 * bp_scale}),
        t1 : Dual(v1, {'v1' : 1, 'Z1' : -v1 * D1 * bp_scale}),
        t2 : Dual(v2, {'v2' : 1, 'Z2' : -v2 * D2 * bp_scale}),
    }

    curve = Curve(interpolation='log_linear', nodes=nodes)
    value_test_swap(curve)

    results_interpretation = """
    Looking at the sensitivity of the par_rate to zero-rates Z1 and Z2 for (3M and 6M time)
    df/dZ1: 
        We have -0.224% sensitivity to 1bp change in 3M rate (or ~23% to change in 3M rate)
    df/dZ2: 
        We have 1.23% sensitivity to 1bp change in 6M rate (or 123% to change in 6M rate) 
"""
    print(results_interpretation)



if __name__ == "__main__":
    swap_dual_curve()
    swap_dual_curve_zero_rate_sensitivities()
