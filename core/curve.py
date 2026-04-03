from datetime import datetime, timedelta
from core.mathutils import interpolate
from core.swap import add_months_modfollowing

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

    def __copy__(self):
        W = getattr(self, "W", None)
        return type(self)(
            nodes=self.nodes,
            interpolation=self.interpolation,
            swaps=getattr(self, "swaps", None),
            optimization_algo=getattr(self, "algo", None),
            obj_rates=getattr(self, "obj_rates", None),
            w=None if W is None else np.diagonal(W),
            t=getattr(self, "t", None),
        )

    # Return discount factor for given date
    def __getitem__(self, date: datetime):
        # find first node_date >= date or use last two dates if date> all node_dates
        for idx, next_date in enumerate(self.node_dates[1:]):
            if next_date >= date or (idx == len(self.node_dates)-2): 
                prev_date = self.node_dates[idx] 
                return interpolate(date, prev_date, self.nodes[prev_date], next_date, self.nodes[next_date], self.interpolation)

    def rate(self, start: datetime, months: int = None, days: int = None):
        if months is not None:
            end = add_months_modfollowing(start, months)
        elif days is not None:
            end = start + timedelta(days=days)
        else:
            end = None
        # (1+r*dcf)*df_end = df_start
        # 1+r*dcf = df_start/df_end
        # r = [(df_start/df_end) - 1] / dcf 
        df_ratio = self[start] / self[end]
        rate = (df_ratio - 1) * timedelta(days=365) / (end - start) # ACT/365
        return rate * 100