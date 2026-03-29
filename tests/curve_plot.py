from matplotlib import pyplot as plt
from core.curve import Curve 
from datetime import datetime, timedelta
import numpy as np 

# Testing 
nodes = {
    datetime(2022, 1, 1) : 1.00,
    datetime(2022, 4, 1) : 0.9975,
    datetime(2022, 7, 1) : 0.9945,
}

curve_log_linear = Curve(interpolation='log_linear', nodes=nodes)
curve_linear = Curve(interpolation='linear', nodes=nodes)

# generate points 
def generate_points(curve: Curve, start_date: datetime, end_date: datetime):
    day_count = (end_date - start_date).days + 1 # end_date included

    dates = []
    dfs = []
    for cur_date in (start_date + timedelta(days=n) for n in range(day_count)):
        dates.append(cur_date)
        dfs.append(curve[cur_date])

    x = np.array(dates)
    y = np.array(dfs)

    # calculating forward O/N rates 
    # DF(t) = e ^ integration(-fi . ti)
    # ln(DF) = integration(-fi.ti)
    # -d ln(DF)/dt = fi
    log_df = np.log(y)
    numerator = -(log_df[1:] - log_df[:-1])
    denominator = 1 / 365 # ACT/365 DCF
    
    fwds = numerator / denominator
    fwd_dates = x[:-1]

    return x, y, fwd_dates, fwds

start_date = datetime(2022, 1, 1)
end_date = datetime(2022, 12, 31)

x_log_linear, y_log_linear, fwd_d_log, fwds_log = generate_points(curve_log_linear, start_date, end_date)
x_linear, y_linear, fwd_d_lin, fwds_lin = generate_points(curve_linear, start_date, end_date)

plt.subplot(1, 2, 1)
plt.title("Discount factor Vs date")
plt.xlabel("Date(T)")
plt.ylabel("DF(t0, T)")
plt.plot(x_log_linear, y_log_linear, label='log_linear interpolation')
plt.plot(x_linear, y_linear, label='linear interpolation')
plt.legend()

plt.subplot(1, 2, 2)
plt.title("O/N forward rate curve")
plt.xlabel("Date(T)")
plt.ylabel("f(Ti, Ti+1)")
plt.plot(fwd_d_log, fwds_log, label='log_linear interpolation')
plt.plot(fwd_d_lin, fwds_lin, label='linear interpolation')

plt.legend()
plt.show()