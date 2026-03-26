from matplotlib import pyplot as plt
from curve import Curve 
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
    return x, y 

start_date = datetime(2022, 1, 1)
end_date = datetime(2022, 12, 31)

x_log_linear, y_log_linear = generate_points(curve_log_linear, start_date, end_date)
x_linear, y_linear = generate_points(curve_linear, start_date, end_date)

plt.plot(x_log_linear, y_log_linear)
plt.plot(x_linear, y_linear)

plt.show()