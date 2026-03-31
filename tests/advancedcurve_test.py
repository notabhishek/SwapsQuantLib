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

def get_testdata_with_curvature_conds(include_curvature_conds: bool = False, layer: int = 1, curve: AdvancedCurve = None):
    nodes_short = {
        datetime(2022, 1, 1): 1.00,  # today's DF
        datetime(2022, 2, 3): 1.00,  # defined MPC dates..
        datetime(2022, 3, 17): 1.00,
        datetime(2022, 3, 31): 1.00, # turn1
        datetime(2022, 4, 1): 1.00,  # turn1
        datetime(2022, 5, 5): 1.00,
        datetime(2022, 6, 16): 1.00,
        datetime(2022, 6, 30): 1.00, # turn2
        datetime(2022, 7, 1): 1.00,  # turn2
        datetime(2022, 8, 4): 1.00,
        datetime(2022, 9, 15): 1.00,
        datetime(2022, 9, 30): 1.00,  # turn3
        datetime(2022, 10, 1): 1.00,  # turn3
        datetime(2022, 11, 3): 1.00,
        datetime(2022, 12, 15): 1.00,
        datetime(2022, 12, 31): 1.00, # turn4
        datetime(2023, 1, 1): 1.00,  # turn4
        datetime(2023, 2, 2): 1.00,  # provisional MPC dates..
        datetime(2023, 3, 23): 1.00,
        datetime(2023, 3, 31): 1.00, # turn5
        datetime(2023, 4, 1): 1.00,  # turn5
        datetime(2023, 5, 11): 1.00,
        datetime(2023, 6, 22): 1.00,
        datetime(2023, 6, 30): 1.00,  # turn6
        datetime(2023, 7, 1): 1.00,  # turn6
        datetime(2023, 8, 3): 1.00,
        datetime(2023, 9, 21): 1.00,
        datetime(2023, 9, 30): 1.00,  # turn7
        datetime(2023, 10, 1): 1.00,  # turn7
        datetime(2023, 11, 2): 1.00,
        datetime(2023, 12, 14): 1.00,
        datetime(2023, 12, 31): 1.00,  # turn8
        datetime(2024, 1, 1): 1.00,  # turn8
        datetime(2024, 2, 8): 1.00,  # estimated MPC dates..
        datetime(2024, 3, 21): 1.00,
        datetime(2024, 5, 16): 1.00,
        datetime(2024, 6, 20): 1.00,
        datetime(2024, 8, 8): 1.00,
        datetime(2024, 9, 19): 1.00,
        datetime(2024, 11, 7): 1.00,
        datetime(2024, 12, 12): 1.00
    }
    nodes_long = {
        datetime(2025, 3, 19): 1.00,  # long term tenors..
        datetime(2027, 3, 17): 1.00,
        datetime(2029, 3, 15): 1.00,
        datetime(2032, 3, 15): 1.00,
        datetime(2037, 3, 15): 1.00,
        datetime(2042, 3, 15): 1.00,
        datetime(2052, 3, 15): 1.00,
        datetime(2062, 3, 15): 1.00,
        datetime(2072, 3, 15): 1.00,
    }
    nodes = {**nodes_short, **nodes_long}
    nodes_dual = {k: Dual(v, {f"v{i}": 1}) for i, (k,v) in enumerate(nodes.items())}

    ini_swaps = {
        Swap(datetime(2022, 1, 1), 34, 34, 34, tenor_type='D'): 0.695,
        Swap(datetime(2022, 2, 3), 42, 42, 42, tenor_type='D'): 0.95,
        Swap(datetime(2022, 3, 16), 3, 3, 3): 1.40,
        Swap(datetime(2022, 6, 15), 3, 3, 3): 1.89,
        Swap(datetime(2022, 9, 16), 3, 3, 3): 2.245,
        Swap(datetime(2022, 12, 21), 3, 3, 3): 2.53,
        Swap(datetime(2023, 3, 15), 3, 3, 3): 2.69,
        Swap(datetime(2023, 6, 21), 3, 3, 3): 2.69,
        Swap(datetime(2023, 9, 20), 3, 3, 3): 2.62,
        Swap(datetime(2023, 12, 20), 3, 3, 3): 2.5,
        Swap(datetime(2024, 3, 20), 3, 3, 3): 2.375,
        Swap(datetime(2024, 6, 19), 3, 3, 3): 2.27,
        Swap(datetime(2024, 9, 18), 3, 3, 3): 2.215,
        Swap(datetime(2024, 12, 18), 3, 3, 3): 2.17,
        Swap(datetime(2022, 1, 1), 12*5, 12, 12): 2.195,
        Swap(datetime(2022, 1, 1), 12*7, 12, 12): 2.193,
        Swap(datetime(2022, 1, 1), 12*10, 12, 12): 2.186,
        Swap(datetime(2022, 1, 1), 12*15, 12, 12): 2.181,
        Swap(datetime(2022, 1, 1), 12*20, 12, 12): 2.162,
        Swap(datetime(2022, 1, 1), 12*30, 12, 12): 2.12,
        Swap(datetime(2022, 1, 1), 12*40, 12, 12): 2.10,
        Swap(datetime(2022, 1, 1), 12*50, 12, 12): 2.09,
    }

    # turns
    turns = {
        SwapSpread(
            Swap(datetime(2022, 3, 30), 1, 1, 1, tenor_type = 'D'),
            Swap(datetime(2022, 3, 31), 1, 1, 1, tenor_type = 'D'),
        ): -0.03,
        SwapSpread(
            Swap(datetime(2022, 3, 31), 1, 1, 1, tenor_type = 'D'),
            Swap(datetime(2022, 4, 1), 1, 1, 1, tenor_type = 'D'),
        ): 0.03,  # turn 1
        SwapSpread(
            Swap(datetime(2022, 6, 29), 1, 1, 1, tenor_type = 'D'),
            Swap(datetime(2022, 6, 30), 1, 1, 1, tenor_type = 'D'),
        ): -0.05,
        SwapSpread(
            Swap(datetime(2022, 6, 30), 1, 1, 1, tenor_type = 'D'),
            Swap(datetime(2022, 7, 1), 1, 1, 1, tenor_type = 'D'),
        ): 0.05,  # turn 2
        SwapSpread(
            Swap(datetime(2022, 9, 29), 1, 1, 1, tenor_type = 'D'),
            Swap(datetime(2022, 9, 30), 1, 1, 1, tenor_type = 'D'),
        ): -0.03,
        SwapSpread(
            Swap(datetime(2022, 9, 30), 1, 1, 1, tenor_type = 'D'),
            Swap(datetime(2022, 10, 1), 1, 1, 1, tenor_type = 'D'),
        ): 0.03,  # turn 3
        SwapSpread(
            Swap(datetime(2022, 12, 30), 1, 1, 1, tenor_type = 'D'),
            Swap(datetime(2022, 12, 31), 1, 1, 1, tenor_type = 'D'),
        ): -0.05,
        SwapSpread(
            Swap(datetime(2022, 12, 31), 1, 1, 1, tenor_type = 'D'),
            Swap(datetime(2023, 1, 1), 1, 1, 1, tenor_type = 'D'),
        ): 0.05,  # turn 4
        SwapSpread(
            Swap(datetime(2023, 3, 30), 1, 1, 1, tenor_type = 'D'),
            Swap(datetime(2023, 3, 31), 1, 1, 1, tenor_type = 'D'),
        ): -0.03,
        SwapSpread(
            Swap(datetime(2023, 3, 31), 1, 1, 1, tenor_type = 'D'),
            Swap(datetime(2023, 4, 1), 1, 1, 1, tenor_type = 'D'),
        ): 0.03,  # turn 5
        SwapSpread(
            Swap(datetime(2023, 6, 29), 1, 1, 1, tenor_type = 'D'),
            Swap(datetime(2023, 6, 30), 1, 1, 1, tenor_type = 'D'),
        ): -0.05,
        SwapSpread(
            Swap(datetime(2023, 6, 30), 1, 1, 1, tenor_type = 'D'),
            Swap(datetime(2023, 7, 1), 1, 1, 1, tenor_type = 'D'),
        ): 0.05,  # turn 6
        SwapSpread(
            Swap(datetime(2023, 9, 29), 1, 1, 1, tenor_type = 'D'),
            Swap(datetime(2023, 9, 30), 1, 1, 1, tenor_type = 'D'),
        ): -0.03,
        SwapSpread(
            Swap(datetime(2023, 9, 30), 1, 1, 1, tenor_type = 'D'),
            Swap(datetime(2023, 10, 1), 1, 1, 1, tenor_type = 'D'),
        ): 0.03,  # turn 7
        SwapSpread(
            Swap(datetime(2023, 12, 30), 1, 1, 1, tenor_type = 'D'),
            Swap(datetime(2023, 12, 31), 1, 1, 1, tenor_type = 'D'),
        ): -0.05,
        SwapSpread(
            Swap(datetime(2023, 12, 31), 1, 1, 1, tenor_type = 'D'),
            Swap(datetime(2024, 1, 1), 1, 1, 1, tenor_type = 'D'),
        ): 0.05,  # turn 8
    }
    
    mpc_1 = Swap(datetime(2022, 2, 3), 1, 1, 1, tenor_type = 'D')
    mpc_2 = Swap(datetime(2022, 3, 17), 1, 1, 1, tenor_type = 'D')
    mpc_3 = Swap(datetime(2022, 5, 5), 1, 1, 1, tenor_type = 'D')
    mpc_4 = Swap(datetime(2022, 6, 16), 1, 1, 1, tenor_type = 'D')
    mpc_5 = Swap(datetime(2022, 8, 4), 1, 1, 1, tenor_type = 'D')
    mpc_6 = Swap(datetime(2022, 9, 15), 1, 1, 1, tenor_type = 'D')
    mpc_7 = Swap(datetime(2022, 11, 3), 1, 1, 1, tenor_type = 'D')
    mpc_8 = Swap(datetime(2022, 12, 15), 1, 1, 1, tenor_type = 'D')
    mpc_9 = Swap(datetime(2023, 2, 2), 1, 1, 1, tenor_type = 'D')
    mpc_10 = Swap(datetime(2023, 3, 23), 1, 1, 1, tenor_type = 'D')
    mpc_11 = Swap(datetime(2023, 5, 11), 1, 1, 1, tenor_type = 'D')
    mpc_12 = Swap(datetime(2023, 6, 22), 1, 1, 1, tenor_type = 'D')
    mpc_13 = Swap(datetime(2023, 8, 3), 1, 1, 1, tenor_type = 'D')
    mpc_14 = Swap(datetime(2023, 9, 21), 1, 1, 1, tenor_type = 'D')
    mpc_15 = Swap(datetime(2023, 11, 2), 1, 1, 1, tenor_type = 'D')
    mpc_16 = Swap(datetime(2023, 12, 14), 1, 1, 1, tenor_type = 'D')
    mpc_17 = Swap(datetime(2024, 2, 8), 1, 1, 1, tenor_type = 'D')
    mpc_18 = Swap(datetime(2024, 3, 21), 1, 1, 1, tenor_type = 'D')
    mpc_19 = Swap(datetime(2024, 5, 16), 1, 1, 1, tenor_type = 'D')
    mpc_20 = Swap(datetime(2024, 6, 20), 1, 1, 1, tenor_type = 'D')
    mpc_21 = Swap(datetime(2024, 8, 8), 1, 1, 1, tenor_type = 'D')
    mpc_22 = Swap(datetime(2024, 9, 19), 1, 1, 1, tenor_type = 'D')
    mpc_23 = Swap(datetime(2024, 11, 7), 1, 1, 1, tenor_type = 'D')
    mpc_24 = Swap(datetime(2024, 12, 12), 1, 1, 1, tenor_type = 'D')
    mpc_25 = Swap(datetime(2025, 3, 20), 1, 1, 1, tenor_type = 'D')

    curvature_conds = {
        SwapSpread(SwapSpread(mpc_1, mpc_2), SwapSpread(mpc_2, mpc_3)): 0,
        SwapSpread(SwapSpread(mpc_2, mpc_3), SwapSpread(mpc_3, mpc_4)): 0,
        SwapSpread(SwapSpread(mpc_3, mpc_4), SwapSpread(mpc_4, mpc_5)): 0,
        SwapSpread(SwapSpread(mpc_4, mpc_5), SwapSpread(mpc_5, mpc_6)): 0,
        SwapSpread(SwapSpread(mpc_5, mpc_6), SwapSpread(mpc_6, mpc_7)): 0,
        SwapSpread(SwapSpread(mpc_6, mpc_7), SwapSpread(mpc_7, mpc_8)): 0,
        SwapSpread(SwapSpread(mpc_7, mpc_8), SwapSpread(mpc_8, mpc_9)): 0,
        SwapSpread(SwapSpread(mpc_8, mpc_9), SwapSpread(mpc_9, mpc_10)): 0,
        SwapSpread(SwapSpread(mpc_9, mpc_10), SwapSpread(mpc_10, mpc_11)): 0,
        SwapSpread(SwapSpread(mpc_10, mpc_11), SwapSpread(mpc_11, mpc_12)): 0,
        SwapSpread(SwapSpread(mpc_11, mpc_12), SwapSpread(mpc_12, mpc_13)): 0,
        SwapSpread(SwapSpread(mpc_12, mpc_13), SwapSpread(mpc_13, mpc_14)): 0,
        SwapSpread(SwapSpread(mpc_13, mpc_14), SwapSpread(mpc_14, mpc_15)): 0,
        SwapSpread(SwapSpread(mpc_14, mpc_15), SwapSpread(mpc_15, mpc_16)): 0,
        SwapSpread(SwapSpread(mpc_15, mpc_16), SwapSpread(mpc_16, mpc_17)): 0,
        SwapSpread(SwapSpread(mpc_16, mpc_17), SwapSpread(mpc_17, mpc_18)): 0,
        SwapSpread(SwapSpread(mpc_17, mpc_18), SwapSpread(mpc_18, mpc_19)): 0,
        SwapSpread(SwapSpread(mpc_18, mpc_19), SwapSpread(mpc_19, mpc_20)): 0,
        SwapSpread(SwapSpread(mpc_19, mpc_20), SwapSpread(mpc_20, mpc_21)): 0,
        SwapSpread(SwapSpread(mpc_20, mpc_21), SwapSpread(mpc_21, mpc_22)): 0,
        SwapSpread(SwapSpread(mpc_21, mpc_22), SwapSpread(mpc_22, mpc_23)): 0,
        SwapSpread(SwapSpread(mpc_22, mpc_23), SwapSpread(mpc_23, mpc_24)): 0,
        SwapSpread(SwapSpread(mpc_23, mpc_24), SwapSpread(mpc_24, mpc_25)): 0,
    }

    # layer 2 data
    nodes_2 = {**nodes_short, **{
        datetime(2025, 3, 19): 1.00,  # long term tenors..
        datetime(2026, 3, 17): 1.00,
        datetime(2027, 3, 17): 1.00,
        datetime(2028, 3, 15): 1.00,
        datetime(2029, 3, 17): 1.00,
        datetime(2030, 3, 17): 1.00,
        datetime(2031, 3, 17): 1.00,
        datetime(2032, 3, 15): 1.00,
        datetime(2034, 3, 15): 1.00,
        datetime(2037, 3, 15): 1.00,
        datetime(2042, 3, 15): 1.00,
        datetime(2047, 3, 15): 1.00,
        datetime(2052, 3, 15): 1.00,
        datetime(2057, 3, 15): 1.00,
        datetime(2062, 3, 15): 1.00,
        datetime(2067, 3, 15): 1.00,
        datetime(2072, 3, 15): 1.00,
    }}
    skews_layer_2 = {
        Swap(datetime(2022, 1, 1), 12*4, 12, 12): -0.0015,
        Swap(datetime(2022, 1, 1), 12*6, 12, 12): +0.0015,
        Swap(datetime(2022, 1, 1), 12*8, 12, 12): -0.0005,
        Swap(datetime(2022, 1, 1), 12*9, 12, 12): -0.0005,
        Swap(datetime(2022, 1, 1), 12*12, 12, 12): -0.001,
        Swap(datetime(2022, 1, 1), 12*25, 12, 12): 0,
        Swap(datetime(2022, 1, 1), 12*35, 12, 12): -0.0005,
        Swap(datetime(2022, 1, 1), 12*45, 12, 12): 0,
    }

    

    # 2nd layer data with skew adjustments
    if layer == 2:
        if curve is None: 
            raise ValueError('Need a curve to solve for swap rates for layer-2 data')
        nodes_dual_2 = {k: Dual(v, {f"v{i}": 1}) for i, (k,v) in enumerate(nodes_2.items())}
        swaps_layer_2 = {swap: swap.rate(curve).real + skew for (swap, skew) in skews_layer_2.items()}
        swaps_2 = {**ini_swaps, **swaps_layer_2, **turns, **curvature_conds}
        weights_2 = [1]*(len(ini_swaps)+len(swaps_layer_2)+len(turns)) + [0.0001]*len(curvature_conds)
        return nodes_dual_2, swaps_2, weights_2
    
    # layer 1 data
    swaps = {**ini_swaps, **turns, **curvature_conds} if include_curvature_conds else {**ini_swaps, **turns}
    w = [1] * (len(ini_swaps) + len(turns))
    # 0.0001 weight for curvature conditions
    if include_curvature_conds: 
        w.extend([0.0001] * len(curvature_conds))
    return nodes_dual, swaps, w

def plot_ON_ex4(include_curvature_conds: bool = True):
    # Solved curve without curvature constraints
    nodes_dual, swaps, wts = get_testdata_with_curvature_conds(include_curvature_conds=include_curvature_conds)
    ini_s_cv = SolvedCurve(
        nodes=nodes_dual, interpolation="log_linear", 
        swaps=list(swaps.keys()), obj_rates=list(swaps.values()),
        optimization_algo="levenberg_marquardt",
        w=wts 
    )
    print(ini_s_cv.iterate())   
    fig, ax = plt.subplots()
    x = [datetime(2022,1,1) + i * timedelta(days=1) for i in range(365*10)]
    z = [ini_s_cv.rate(date, days=1).real for date in x]
    ax.plot(x, z, label=f'Includes curvature constraints:{include_curvature_conds}')
    # ax.set_xlim(datetime(2023,1,1),datetime(2024,9,30))
    # ax.set_ylim(2.3,2.75)
    plt.xticks(rotation=90)
    plt.title('O/N forward RF rates(log-linear)')
    plt.xlabel('Date')
    plt.ylabel('RFR(%)')
    plt.legend()
    plt.show()

# AdvancedCurve with log-cubic interpolation
def plot_ON_ex5():
    nodes_dual, swaps, wts = get_testdata_with_curvature_conds(include_curvature_conds=True)

    t_layer_1 = [
        datetime(2025, 3, 19), datetime(2025, 3, 19), datetime(2025, 3, 19), datetime(2025, 3, 19),
        datetime(2027, 3, 15),
        datetime(2029, 3, 15),
        datetime(2032, 3, 15),
        datetime(2037, 3, 15),
        datetime(2042, 3, 15),
        datetime(2052, 3, 15),
        datetime(2062, 3, 15),
        datetime(2072, 3, 15), datetime(2072, 3, 15), datetime(2072, 3, 15), datetime(2072, 3, 15),
    ]

    adv_cv_1 = AdvancedCurve(
        nodes=nodes_dual, interpolation="log_linear", 
        swaps=list(swaps.keys()), obj_rates=list(swaps.values()), t=t_layer_1,
        optimization_algo="levenberg_marquardt", 
        w=wts,
    )
    print(adv_cv_1.iterate())   

    # Build layer-2 curve 
    t_layer_2 = [
        datetime(2025, 3, 19), datetime(2025, 3, 19), datetime(2025, 3, 19), datetime(2025, 3, 19),
        datetime(2026, 3, 15),  # 4y
        datetime(2027, 3, 15),
        datetime(2028, 3, 15),  # 6y
        datetime(2029, 3, 15), 
        datetime(2030, 3, 15),  # 8y
        datetime(2031, 3, 15),  # 9y
        datetime(2032, 3, 15),
        datetime(2034, 3, 15),  # 12y
        datetime(2037, 3, 15),
        datetime(2042, 3, 15),
        datetime(2047, 3, 15),  # 25y
        datetime(2052, 3, 15),
        datetime(2057, 3, 15),  # 35y
        datetime(2062, 3, 15),
        datetime(2067, 3, 15),  # 45y
        datetime(2072, 3, 15), datetime(2072, 3, 15), datetime(2072, 3, 15), datetime(2072, 3, 15),
    ]
    nodes_dual2, swaps2, wts2 = get_testdata_with_curvature_conds(include_curvature_conds=True, layer=2, curve=adv_cv_1)
    adv_cv_2 = AdvancedCurve(
        nodes=nodes_dual2, interpolation="log_linear", 
        swaps=list(swaps2.keys()), obj_rates=list(swaps2.values()), t=t_layer_2,
        optimization_algo="levenberg_marquardt", 
        w=wts2,
    )
    print(adv_cv_2.iterate())  

    fig, ax = plt.subplots()
    x = [datetime(2022,1,1) + i * timedelta(days=1) for i in range(365*10)]
    z = [adv_cv_1.rate(date, days=1).real for date in x]
    y = [adv_cv_2.rate(date, days=1).real for date in x]
    ax.plot(x, z, label=f'Layer-1')
    ax.plot(x, y, label=f'Layer-2')
    # ax.set_xlim(datetime(2023,1,1),datetime(2024,9,30))
    # ax.set_ylim(2.3,2.75)
    plt.xticks(rotation=90)
    plt.title('O/N RFR (2-layer Mixed Interpolation with Turns & Curvature conditions)')
    plt.xlabel('Date')
    plt.ylabel('RFR(%)')
    plt.legend()
    plt.show()

if __name__ == '__main__':
    # 3Y RFR curves
    plot_on_ex1()
    # 10Y RFR curves
    plot_on_ex2()
    # log-linear curve with turns
    plot_ON_ex3()

    # log-linear curve with and without curvature constraints
    plot_ON_ex4(include_curvature_conds=False)
    plot_ON_ex4(include_curvature_conds=True)

    # Plot 2 layer curve with Turns, Mixed interp & curvature constraints
    plot_ON_ex5()