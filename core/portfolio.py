from core.solvedcurve import SolvedCurve
from core.covar import Covar_

class Portfolio(Covar_):
    def __init__(self, objects: list = []):
        self.objects = objects
    
    def risks(self, curve: SolvedCurve):
        risk = self.objects[0].risk(curve)
        for obj in objects[1:]:
            risk += obj.risk(curve)
        return risk 
    
    def npv(self, curve: SolvedCurve):
        npv = self.objects[0].npv(curve)
        for obj in objects[1:]:
            npv += obj.npv(curve)
        return npv