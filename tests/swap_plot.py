from core.swap import Swap 
from core.curve import Curve 
from datetime import datetime
import numpy as np 
import matplotlib.pyplot as plt 

curve_log_linear = Curve(interpolation='log_linear', nodes = {
    datetime(2022, 1, 1) : 1.00,
    datetime(2022, 4, 1) : 0.9975,
    datetime(2022, 7, 1) : 0.9945,
})

curve_linear = Curve(interpolation='log_linear', nodes = {
    datetime(2022, 1, 1) : 1.00,
    datetime(2022, 4, 1) : 0.9975,
    datetime(2022, 7, 1) : 0.9945,
})


start_date = datetime(2022, 1, 1)
tenors = []
par_rates_log_linear = []
par_rates_linear = []
for m in range(1, 50 * 12 + 1):
    # Annual swap with tenor m months
    swap = Swap(start_date, tenor=m, period_fix=12, period_float=12)
    tenors.append(m)
    par_rates_log_linear.append(swap.rate(curve_log_linear))
    par_rates_linear.append(swap.rate(curve_linear))

# plot tenor vs rate 
x = np.array(tenors)
y_1 = np.array(par_rates_log_linear)
y_2 = np.array(par_rates_linear)

plt.plot(x, y_1, label='log_linear_interpolation')
plt.plot(x, y_2, label='linear_interpolation')

plt.title("Forward curve for swap par rates")
plt.xlabel("Term (months)")
plt.ylabel("Par rate")
plt.legend()
plt.show()