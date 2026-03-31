from core.swap import Swap
from core.curve import Curve

class SwapSpread:
    def __init__(self, swap1: Swap, swap2: Swap):
        # weights [-1, 1]
        self.swap1 = swap1 
        self.swap2 = swap2 
    
    def rate(self, curve: Curve):
        return self.swap2.rate(curve) - self.swap1.rate(curve)