from datetime import datetime, timedelta
from core.swap import Swap 
from core.advancedcurve import AdvancedCurve
from core.dual import Dual 
from core.solvedcurve import SolvedCurve
import matplotlib.pyplot as plt
from core.swapspread import SwapSpread
def get_test_data():
    init_v = 1
    nodes = {
        datetime(2022, 1, 1) : Dual(init_v, {'v0' : 1}),
        datetime(2023, 1, 1) : Dual(init_v, {'v1' : 1}),
        datetime(2024, 1, 1) : Dual(init_v, {'v2' : 1}),
        datetime(2025, 1, 1) : Dual(init_v, {'v3' : 1}),
    }

    # annual 1Y, 2Y, 5Y, 10Y swaps and their par market rates
    par_swaps = {
        Swap(datetime(2022, 1, 1), 12 * 1, 12, 12)  : 1.0,
        Swap(datetime(2022, 1, 1), 12 * 2, 12, 12)  : 1.5,
        Swap(datetime(2022, 1, 1), 12 * 3, 12, 12)  : 2.0,
    }

    return nodes, par_swaps

def plot_on_rfr_curves(nodes: dict, swaps: dict, t: list = [], plot_start:datetime = None, plot_days: int = 365 * 10):
    s_cv_lin = SolvedCurve(nodes=nodes, interpolation='linear',
                    swaps=list(swaps.keys()), obj_rates=list(swaps.values()),
                    optimization_algo='levenberg_marquardt')
    
    s_cv_log = SolvedCurve(nodes=nodes, interpolation='log_linear',
                    swaps=list(swaps.keys()), obj_rates=list(swaps.values()),
                    optimization_algo='levenberg_marquardt')

    if len(t) == 0:
        # construct t 
        t.extend([list(nodes.keys())[0]] * 3) # uses t[0] repeated 4 times
        for ti in nodes.keys():
            t.append(ti)
        t.extend([list(nodes.keys())[-1]] * 3) # uses t[-1] repeated 4 times
        print(f'knot seq t was empty, constructed using nodes, t={t}')
    
    adv_cv = AdvancedCurve(nodes=nodes, interpolation='log_linear', 
                        swaps=list(swaps.keys()), obj_rates=list(swaps.values()),
                        optimization_algo='levenberg_marquardt',
                        t=t)

    print(f'Solving SolvedCurve(lin)                            :{s_cv_lin.iterate()}')
    print(f'Solving SolvedCurve(log_linear)                     :{s_cv_log.iterate()}')
    print(f'Solving AdvancedCurve(mixed cubic + log_linear)     :{adv_cv.iterate()}')

    fig, ax = plt.subplots()
    if plot_start is None: 
        plot_start = t[0] - timedelta(days=365)
    x = [plot_start + i * timedelta(days=1) for i in range(plot_days)]

    y = [adv_cv.rate(date, days=1).real for date in x]
    z = [s_cv_log.rate(date, days=1).real for date in x]
    w = [s_cv_lin.rate(date, days=1).real for date in x]

    ax.plot(x, w, label='Linear interpolation')
    ax.plot(x, z, label='Log-linear interpolation')
    ax.plot(x, y, label='Mixed interpolation(Log-cubic + Log-linear)')
    plt.title('Overnight forward RF rates')
    plt.xlabel('Date')
    plt.ylabel('RFR(%)')
    plt.legend()
    plt.show()

def plot_on_ex1():
    nodes, swaps = get_test_data()
    
    t_l = datetime(2023, 1, 1)
    t_r = datetime(2025, 1, 1)
    t = [
        t_l, t_l, t_l, t_l,
        datetime(2024, 1, 1),
        t_r, t_r, t_r, t_r
    ]
    plot_on_rfr_curves(nodes, swaps, t, plot_start=datetime(2022, 1, 1), plot_days=365 * 3)

def plot_on_ex2():
    nodes = {
        datetime(2022, 1, 1): 1.00,
        datetime(2023, 1, 1): 1.00,
        datetime(2024, 1, 1): 1.00,
        datetime(2025, 1, 1): 1.00,
        datetime(2027, 1, 1): 1.00,
        datetime(2029, 1, 1): 1.00,
        datetime(2032, 1, 1): 1.00,
    }
    nodes_dual = {k: Dual(v, {f"v{i}": 1}) for i, (k,v) in enumerate(nodes.items())}
    
    swaps = {
        Swap(datetime(2022, 1, 1), 12*1, 3, 3): 1.0,
        Swap(datetime(2022, 1, 1), 12*2, 3, 3): 1.4,
        Swap(datetime(2022, 1, 1), 12*3, 3, 3): 1.64,
        Swap(datetime(2022, 1, 1), 12*5, 3, 3): 1.84,
        Swap(datetime(2022, 1, 1), 12*7, 3, 3): 1.90,
        Swap(datetime(2022, 1, 1), 12*10, 3, 3): 1.97,
    }

    plot_on_rfr_curves(nodes_dual, swaps, plot_start=datetime(2021, 1, 1), plot_days=365 * 10)

# Plot with turns
def plot_ON_ex3():
    nodes = {
        datetime(2022, 1, 1): 1.00,
        datetime(2022, 12, 31): 1.00, # -.25 bp turn here
        # don't need another node to undo Dec31 as we already have a node on Jan 1
        
        datetime(2023, 1, 1): 1.00,

        datetime(2023, 6, 30): 1.00, # -0.25bp turn here
        datetime(2023, 7, 1): 1.00,  # +0.25bp here to undo turn 
        
        datetime(2024, 1, 1): 1.00,
        datetime(2025, 1, 1): 1.00,
    }

    nodes_dual = {k: Dual(v, {f"v{i}": 1}) for i, (k,v) in enumerate(nodes.items())}
    
    swaps = {
        Swap(datetime(2022, 1, 1), 12 * 1, 12, 12, tenor_type='M')  : 1.0,
        Swap(datetime(2022, 1, 1), 12 * 2, 12, 12, tenor_type='M')  : 1.5,
        Swap(datetime(2022, 1, 1), 12 * 3, 12, 12, tenor_type='M')  : 2.0,
        # 1D turn -0.25bp on 31st Dec 2022. 1Y Swap ending on 1st Jan 2023 
        # will undo this so don't need opposite turn
        SwapSpread(
            Swap(datetime(2022, 12, 30), 1, 1, 1, tenor_type='D'),
            Swap(datetime(2022, 12, 31), 1, 1, 1, tenor_type='D'),
        ) : -0.25,

        # # 1D turn -0.25bp on 30th June 2022
        SwapSpread(
            Swap(datetime(2023, 6, 29), 1, 1, 1, tenor_type='D'),
            Swap(datetime(2023, 6, 30), 1, 1, 1, tenor_type='D'),
        ) : -0.25,
        # # undo the turn for next day with +0.25bp
        SwapSpread(
            Swap(datetime(2023, 6, 30), 1, 1, 1, tenor_type='D'),
            Swap(datetime(2023, 7, 1), 1, 1, 1, tenor_type='D'),
        ) : 0.25,
    }

    s_cv_log = SolvedCurve(nodes=nodes_dual, interpolation='log_linear',
                    swaps=list(swaps.keys()), obj_rates=list(swaps.values()),
                    optimization_algo='levenberg_marquardt')
    print(f'Solving SolvedCurve(log_linear)                     :{s_cv_log.iterate()}')
    fig, ax = plt.subplots()
    plot_start = datetime(2022, 1, 1)
    x = [plot_start + i * timedelta(days=1) for i in range(3 * 365)]

    z = [s_cv_log.rate(date, days=1).real for date in x]

    ax.plot(x, z, label='Log-linear interpolation')
    plt.title('Overnight forward RFR with -0.25bp turns on 31-Dec-2022 and 30-June-2023')
    plt.xlabel('Date')
    plt.ylabel('RFR(%)')
    plt.legend()
    plt.show()

if __name__ == '__main__':
    plot_on_ex1()
    plot_on_ex2()
    plot_ON_ex3()