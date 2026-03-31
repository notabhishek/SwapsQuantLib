import core.bspline as bspl
import matplotlib.pyplot as plt
import numpy as np 


def plot_spline(i, k, t, subplt, step=1000):
    x = [xi + (i/step) for xi in range(t[0], t[-1]) for i in range(step)]
    x.append(t[-1])

    y = [bspl.bsplev_single(xi, i, k, t, 4) for xi in x]
    # print(x, '\n', y)

    X, Y = [], []
    for xi, yi in zip(x, y):
        if yi == 0:
            continue
        X.append(xi)
        Y.append(yi)
    
    plot_method = subplt.plot
    if len(X) == 0:
        return
    if len(X) == 1:
        plot_method = subplt.scatter
    plot_method(np.array(X), np.array(Y), label=f'Bi={i},k={k}')


def subplot_spline_for_k(k, t, subplt):
    num_splines = len(t) - k 
    for i in range(num_splines):
        plot_spline(i, k, t, subplt)

    subplt.set_xlabel('x')
    subplt.set_ylabel(f'Bi,{k},t(x)')
    subplt.legend()

def plot_splines_for(k, t):
    rows = (k + 1) // 2 
    cols = 2
    for k1 in range(1, k+1):
        subplt = plt.subplot(rows, cols, k1)
        subplot_spline_for_k(k=k1, t=t, subplt=subplt)

# Plotting nth derivatives for Bi,k,t
def plot_spline_dn(i, k, n, t, subplt, step=100):
    x = [xi + (i/step) for xi in range(t[0], t[-1]) for i in range(step)]
    x.append(t[-1])

    y = [bspl.bspldnev_single(xi, i, k, t, n) for xi in x]
    # print(x, '\n', y)

    X, Y = [], []
    for xi, yi in zip(x, y):
        if yi == 0:
            continue
        X.append(xi)
        Y.append(yi)

    plot_method = subplt.plot
    if len(X) == 0:
        # For derviatives plot zeros
        X, Y = x, y
    if len(X) == 1:
        plot_method = subplt.scatter
    plot_method(np.array(X), np.array(Y), label=f'Bi={i},k={k}')

def subplot_spline_dn(k, t, n, subplt):
    num_splines = len(t) - k 
    for i in range(num_splines):
        plot_spline_dn(i, k, n, t, subplt)

    subplt.set_xlabel('x')
    subplt.set_ylabel(f'd{n} (Bi,{k},t)/dx')
    subplt.legend()

def plot_splines_derivative_for(k, t):
    plots = 1
    cols = 1
    rows = (plots + cols - 1) // cols 
    plot_idx = 1

    for d in range(1, 2): # update for di
        for k1 in range(k, k+1): # only plot Bi,k
            subplt = plt.subplot(rows, cols, plot_idx)
            subplot_spline_dn(k=k1, t=t, n=d, subplt=subplt)
            plot_idx += 1

if __name__ == '__main__':
    k = 4
    t = [1, 1, 1, 1, 2, 2, 2, 3, 4, 4, 4, 4]
    # t = [1, 1, 1, 1, 2, 3, 4, 5, 5, 5, 5]
    # plt.title(f'Plot of B-splines of order 1<=k<={k} for knot seq t={t}')
    # plot_splines_for(k=k, t = t)
    
    plt.title(f'Plot of f = d(Bi,k={k},t)/dx for knot seq t={t}')
    plot_splines_derivative_for(k=k, t=t)

    plt.show()