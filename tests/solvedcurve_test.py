from datetime import datetime
from core.dual import Dual
from core.swap import Swap 
from core.solvedcurve import SolvedCurve

def test(algorithm='levenberg_marquardt'):
    # intial discount factor guess
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
        Swap(datetime(2022, 1, 1), 12 * 10, 12, 12) : 1.935,
    }

    s_cv = SolvedCurve(nodes=nodes,
                       swaps=list(par_swaps.keys()),
                       obj_rates=list(par_swaps.values()),
                       interpolation='log_linear',
                       optimization_algo=algorithm)

    # print('Initial curve')
    # print(s_cv)

    # print('Solving')
    print(s_cv.iterate())

    # print('\nSolved curve')
    # print(s_cv)

if __name__ == '__main__':
    for algo in ['guass_newton', 'gradient_descent', 'levenberg_marquardt']:
        test(algo)