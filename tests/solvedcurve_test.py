from datetime import datetime
from core.dual import Dual
from core.swap import Swap 
from core.solvedcurve import SolvedCurve
import numpy as np
import matplotlib.pyplot as plt 

def get_test_data():
    init_v = 1
    nodes = {
        datetime(2022, 1, 1) : Dual(init_v, {'v0' : 1}),
        datetime(2023, 1, 1) : Dual(init_v, {'v1' : 1}),
        datetime(2024, 1, 1) : Dual(init_v, {'v2' : 1}),
        datetime(2027, 1, 1) : Dual(init_v, {'v3' : 1}),
        datetime(2032, 1, 1) : Dual(init_v, {'v4' : 1}),
    }

    # annual 1Y, 2Y, 5Y, 10Y swaps and their par market rates
    par_swaps = {
        Swap(datetime(2022, 1, 1), 12 * 1, 12, 12)  : 1.210,
        Swap(datetime(2022, 1, 1), 12 * 2, 12, 12)  : 1.635,
        Swap(datetime(2022, 1, 1), 12 * 5, 12, 12)  : 1.885,
        Swap(datetime(2022, 1, 1), 12 * 10, 12, 12) : 1.930,
    }

    return nodes, par_swaps

def get_solvedcurve(algorithm: str ='levenberg_marquardt'):
    # intial discount factor guess
    nodes, par_swaps = get_test_data()

    s_cv = SolvedCurve(nodes=nodes,
                       swaps=list(par_swaps.keys()),
                       obj_rates=list(par_swaps.values()),
                       interpolation='log_linear',
                       optimization_algo=algorithm)

    return s_cv

def plot_curve(curve: SolvedCurve):
    start_date = datetime(2022, 1, 1)
    
    nodes, market_swaps = get_test_data()
    market_tenors = [swap.tenor_m for swap in market_swaps.keys()]
    market_rates = [rate.real for rate in market_swaps.values()]

    implied_tenors = []
    implied_rates = []

    # solve
    curve.iterate()

    for m in range(1, 50 * 12 + 1):
        swap = Swap(start_date, tenor_m=m, period_fix_m=12, period_float_m=12)
        implied_tenors.append(m)
        implied_rates.append(swap.rate(curve).real)

    x1, y1 = np.array(market_tenors), np.array(market_rates)
    x2, y2 = np.array(implied_tenors), np.array(implied_rates)

    plt.plot(x1, y1, label='market')
    plt.plot(x2, y2, label='implied')
    plt.title("Forward curve for swap Market vs Implied rates")
    plt.xlabel("Term (months)")
    plt.ylabel("Rate (Market/Implied)")

    plt.legend()
    plt.show()

def test_diff_opt_algos():
    for algo in ['guass_newton', 'gradient_descent', 'levenberg_marquardt']:
        s_cv = get_solvedcurve(algo)

        # print('Initial curve')
        # print(s_cv)

        # print('Solving')
        print(s_cv.iterate())

        print('\nSolved curve')
        print(s_cv)

def test_plot_curve_against_market():
    s_cv = get_solvedcurve('levenberg_marquardt')
    # plot the solved curve against market rates
    plot_curve(s_cv)

def test_do_risk(): 
    # curve with lm optimization
    s_cv = get_solvedcurve('levenberg_marquardt')
    print(s_cv.iterate())

    # 5y fwd starting 5y swap
    swap5y5y = Swap(datetime(2027, 1, 1), 12 * 5, 12, 12)
    risk5y5y = swap5y5y.risk(s_cv, fixed_rate=swap5y5y.rate(s_cv).real, notional=100e6) 

    print(f'{risk5y5y=}')

if __name__ == '__main__':
    # test_diff_opt_algos()
    test_do_risk()
    # test_plot_curve_against_market()
   
    