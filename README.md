# SwapsQuantLib
Swaps Curve construction and Pricing library

### Running tests
#### Curve tests
```
python -m tests.curve_test   
python -m tests.curve_plot 
```
We used linear and log linear interpolation on discount factors to build the curve,
and then also plotted the O/N forward rates implied by the DF curve 

- Log-linear gives flat rate between knots, and has discontinuous jumps at knots 
- Linear has an upward slope between knots and has a sharpe elbow at knots
- TODO: cubic-spline (B-splines) to produce smoother forward curve

<img src="./images/curve_plot.png" alt="Discount factor curve" height="400px" width="800px"/>

#### Schedule tests
```
python -m tests.schedule_test
```

#### Swap tests 
```
python -m tests.swap_test
python -m tests.swap_dual_curve_test
```
<img src="./images/swap_plot.png" alt="Forward swap par rate curve" height="200px" />

### Dual number tests 
```
python -m tests.dual_test
```

### Solved curve tests 
```
python -m tests.solvedcurve_test
```
<img src="./images/solved_curve_plot.png" alt="Forward swap par rate curve" height="200px" />