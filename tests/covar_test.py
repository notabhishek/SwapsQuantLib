from core.solvedcurve import SolvedCurve
from core.swap import Swap 
from core.dual import Dual 
from datetime import datetime, timedelta
from core.portfolio import Portfolio

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

portfolio = Portfolio(objects=swaps)

print(f'{portfolio.npv(s_cv).real=}')
print(f'{portfolio.risk(s_cv).real=}')