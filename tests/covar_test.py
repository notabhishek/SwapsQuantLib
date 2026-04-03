from core.solvedcurve import SolvedCurve
from core.swap import Swap 
from core.dual import Dual 
from datetime import datetime, timedelta
from core.portfolio import Portfolio

nodes = {
    datetime(2022, 1, 1) : Dual(1, {'v0' : 1}),
    datetime(2023, 1, 1) : Dual(1, {'v1' : 1}),
    datetime(2024, 1, 1) : Dual(1, {'v2' : 1}),
    datetime(2027, 1, 1) : Dual(1, {'v3' : 1}),
    datetime(2032, 1, 1) : Dual(1, {'v4' : 1}),
}

# annual 1Y, 2Y, 5Y, 10Y swaps and their par market rates
par_swaps = {
    Swap(datetime(2022, 1, 1), 12 * 1, 12, 12)  : 1.210,
    Swap(datetime(2022, 1, 1), 12 * 2, 12, 12)  : 1.635,
    Swap(datetime(2022, 1, 1), 12 * 5, 12, 12)  : 1.885,
    Swap(datetime(2022, 1, 1), 12 * 10, 12, 12) : 1.930,
}

curve = SolvedCurve(nodes=nodes,
swaps=list(par_swaps.keys()),
obj_rates=list(par_swaps.values()),
                    interpolation='log_linear',
                    optimization_algo='levenberg_marquardt')
                

swaps = [
    Swap(datetime(2022, 1, 1), 12 * 2, 12, 12, fixed_rate=1.20, notional=-50.9e6),
    Swap(datetime(2022, 1, 1), 12 * 5, 12, 12, fixed_rate=1.66, notional=5.23e6),
    Swap(datetime(2022, 1, 1), 12 * 10, 12, 12, fixed_rate=1.93, notional=11.0e6),
    Swap(datetime(2022, 1, 1), 12 * 20, 12, 12, fixed_rate=2.20, notional=-1.81e6),
]

portfolio = Portfolio(objects=swaps)

portfolio.risk(curve)