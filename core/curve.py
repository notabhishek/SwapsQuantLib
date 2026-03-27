from datetime import datetime
from core.mathutils import interpolate

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
            output += f"{node_dt.strftime('%Y-%b-%d')}: {df}\n"
        return output 
    
    __str__ = __repr__

    # Return discount factor for given date
    def __getitem__(self, date: datetime):
        # find first node_date >= date or use last two dates if date> all node_dates
        for idx, next_date in enumerate(self.node_dates[1:]):
            if next_date >= date or (idx == len(self.node_dates)-2): 
                prev_date = self.node_dates[idx] 
                return interpolate(date, prev_date, self.nodes[prev_date], next_date, self.nodes[next_date], self.interpolation)
