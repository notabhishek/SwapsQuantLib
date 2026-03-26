import math 
from core.dual import Dual 

def exp(x):
    if isinstance(x, Dual):
        return x.__exp__()
    return math.exp(x)

def log(x):
    if isinstance(x, Dual):
        return x.__log__()
    return math.log(x)

def interpolate(x, x1, y1, x2, y2, method):
    # Interpolate and find y for given x, using (x1,y1) and (x2, y2)
    if method == 'linear':
        """
        (y-y1)/(x-x1)  = (y2-y1)/(x2-x1)
        y =  (y2-y1) * (x - x1) / (x2-x1) + y1
        """
        return (y2 - y1) * (x - x1) / (x2 - x1) + y1
    
    if method == 'log_linear':
        """
        logrithms of y are linearly interpolated
        let ly1 = log(y1), then we can linearly interpolate these and get 

        ly = (ly2 - ly1) * (x-x1) / (x2 - x1) + ly1
        y = exp(ly)
        """
        logy = interpolate(x, x1, log(y1), x2, log(y2), 'linear')
        return exp(logy)
    
    raise f'Unsupported interpolation: {method}'