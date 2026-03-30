# SwapsQuantLib
Swaps Curve construction and Pricing library, uses Dual numbers to do automatic algorithmic differentiation (AAD)

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
<details>
    <summary>Plot par rates for different swap tenors</summary>

<img src="./images/swap_plot.png" alt="Forward swap par rate curve" height="200px" />
</details>

### Dual number tests 
```
python -m tests.dual_test
```

### Solved curve tests 
```
python -m tests.solvedcurve_test
```
<img src="./images/solved_curve_plot.png" alt="Forward swap par rate curve" height="200px" />

### BSpline plots 
```
python -m tests.bspline_plot
```
Plotting B-splines of order 1 to 4, for knot seq t=[1, 1, 1, 1, 2, 2, 2, 3, 4, 4, 4, 4]
NOTE: only plotted non-zero values to avoid clutter

- 1st order splines Bi,k=1 are just steps between t[i] and t[i+1]
- 2nd order splines Bi,k=2 form mountains from t[i], t[i+1], t[i+2] with peak at t[i+1]
- 3rd order splines Bi,k=3 form parabolas using t[i] to t[i+3]
- 4th order splines Bi,k=4 are smooth bell curves

Notice how due to repeated knots (2) we kill the smoothness at B2,3

<img src="./images/bspline_plot.png" alt="Bsplines with repeated knots" height="600px" width="800px" />


Plotting B-Splines of order 1 to 4, for t = [1, 1, 1, 1, 2, 3, 4, 5, 6, 6, 6, 6], 
without repeated knots 

<img src="./images/bspline_plot2.png" alt="Bsplines with repeated knots" height="600px" width="800px" />