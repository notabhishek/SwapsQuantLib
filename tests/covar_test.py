from core.solvedcurve import SolvedCurve
from core.swap import Swap 
from core.dual import Dual 
from datetime import datetime, timedelta
from core.portfolio import Portfolio

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np 

nodes = {
    datetime(2022, 1, 1): Dual(1, {"v0": 1}),
    datetime(2024, 1, 1): Dual(1, {"v1": 1}),
    datetime(2027, 1, 1): Dual(1, {"v2": 1}),
    datetime(2032, 1, 1): Dual(1, {"v3": 1}),
    datetime(2052, 1, 1): Dual(1, {"v4": 1}),
}
swaps = {
    Swap(datetime(2022, 1, 1), 12*2, 12, 12): 1.20,
    Swap(datetime(2022, 1, 1), 12*5, 12, 12): 1.66,
    Swap(datetime(2022, 1, 1), 12*10, 12, 12): 1.93,
    Swap(datetime(2022, 1, 1), 12*30, 12, 12): 2.20,
}
s_cv = SolvedCurve(nodes=nodes, interpolation="log_linear", swaps=list(swaps.keys()), obj_rates=list(swaps.values()))
s_cv.iterate() 

print(s_cv.iterate())             

swaps = [
    Swap(datetime(2022, 1, 1), 12 * 2, 12, 12, fixed_rate=1.20, notional=-50.9e6),
    Swap(datetime(2022, 1, 1), 12 * 5, 12, 12, fixed_rate=1.66, notional=5.23e6),
    Swap(datetime(2022, 1, 1), 12 * 10, 12, 12, fixed_rate=1.93, notional=11.0e6),
    Swap(datetime(2022, 1, 1), 12 * 20, 12, 12, fixed_rate=2.20, notional=-1.81e6),
]

"""
N = 5

2  4  8 0 -5 

1.8 1.8 1.8 1.8 1.8

Mean: (u) : sum / N = 9/5 = 1.8

Variance: sum((Xi - u)**2)/N

Covariance; sum((Xi-ux) * (Xj - uj)) / N

Variance: [(0.2)**2 + 2.2**2 + .. ] / 5
Std.deviation = sqrt(variance)


"""
portfolio = Portfolio(objects=swaps)

print(f'{portfolio.npv(s_cv).real=}')
print(f'{portfolio.risk(s_cv).real=}')

# Building covariance matrix
historical_rates = pd.DataFrame({
    "2Y": [1.199, 1.228, 1.210, 1.215, 1.203, 1.159, 1.175, 1.188, 1.159, 1.100],
    "5Y": [1.663, 1.696, 1.665, 1.680, 1.677, 1.657, 1.673, 1.676, 1.653, 1.600],
    "10Y": [1.928, 1.945, 1.934, 1.93, 1.934, 1.931, 1.958, 1.972, 1.932, 1.900],
    "30Y": [2.201, 2.217, 2.228, 2.239, 2.226, 2.235, 2.242, 2.236, 2.22, 2.200],
})

print('Daily prices')
print(historical_rates)
print('Diffs')
daily_changes_bp = historical_rates.diff(periods=-1) * 100
print(daily_changes_bp)

Q = daily_changes_bp.cov()

print('Covariance matrix')
print(Q)

print(f'Portfolio standard deviation: c = {portfolio.covar(s_cv, Q)=}')

key_x = [50, 84.13447, 90, 95, 99]
key_y = [portfolio.covar(s_cv, Q, alpha=(1-xi/100)) for xi in key_x]

for x, covar_x in zip(key_x, key_y):
    print(f'{x}% of the time loss <= {covar_x}')
    plt.annotate(f'({x}%, {covar_x:.0f})', 
                 xy=(x, covar_x), 
                 xytext=(5, 5), 
                 textcoords='offset points',
                 fontsize=9)
    
x = [i for i in range(0, 100)]
y = [portfolio.covar(s_cv, Q, alpha=(1-xi/100)) for xi in x]


plt.plot(np.array(x), np.array(y), label='Portfolio loss (negative is gain)')
plt.scatter(key_x, key_y, label='Key confidence levels')

plt.xlabel('Confidence Level (%)')
plt.ylabel('Loss value')


plt.legend()
plt.show()