from datetime import datetime
from math import log, exp

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

class Curve:
    """
    nodes: { datetime: discount_factor }
    """
    def __init__(self, nodes: dict, interpolation: str):
        self.nodes = nodes.copy()
        self.node_dates = list(self.nodes.keys())
        self.interpolation = interpolation
    
    def __repr__(self):
        output = f"interpolation={self.interpolation}\ndiscount_factors=\n"
        for node_dt, df in self.nodes.items():
            output += f"{node_dt.strftime('%Y-%b-%d')}: {df:.6f}\n"
        return output 
    
    __str__ = __repr__

    # Return discount factor for given date
    def __getitem__(self, date: datetime):
        # find first node_date >= date or use last two dates if date> all node_dates
        for idx, next_date in enumerate(self.node_dates[1:]):
            if next_date >= date or (idx == len(self.node_dates)-2): 
                prev_date = self.node_dates[idx] 
                return interpolate(date, prev_date, self.nodes[prev_date], next_date, self.nodes[next_date], self.interpolation)
        


# Testing 
if __name__ == "__main__":
    curve = Curve(interpolation='log_linear', nodes = {
        datetime(2022, 1, 1) : 1.00,
        datetime(2022, 4, 1) : 0.9975,
        datetime(2022, 7, 1) : 0.9945,
    })

    print(f'{curve=}')
    print(f'{curve[datetime(2022, 3, 15)]=}')
    print(f'{curve[datetime(2022, 4, 1)]=}')