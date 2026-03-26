import math

def exp(x):
    if isinstance(x, Dual):
        return x.__exp__()
    return math.exp(x)

def log(x):
    if isinstance(x, Dual):
        return x.__log__()
    return math.log(x)

class Dual:
    def __init__(self, real, dual=None):
        """
        Dual number z is such that 
            z = x + b.e where e**2 = 0 and e != 0
        
        real: real part 
        dual: dict (key=name_index/tag and value=coefficient)
        """
        self.real = real
        self.dual = dual 
    
    def __repr__(self):
        output = f'{self.real}'
        for tag, coef in self.dual.items():
            output += f'{coef:+.3f}e_{tag}'
        return output 

    def __str__(self):
        output = f'f = {self.real:.8f}\n'
        for tag, coef in self.dual.items():
            output += f'df/d{tag} = {coef:.6f}\n'
        return output
    
    def __neg__(self):
        # -z = -x - bi.ei
        dual = {tag: -coef for tag, coef in self.dual.items()}
        return Dual(-self.real, dual)
    
    def __eq__(self, other):
        if not isinstance(other, Dual):
            return False
        return self.real == other.real and self.dual == other.dual
    
    def __ne__(self, other):
        return not self.__eq__(other)

    def conjugate(self):
        # conjugate(z)= x - bi.ei
        dual = {tag: -coef for tag, coef in self.dual.items()}
        return Dual(self.real, dual)

    def __add__(self, other):
        if not isinstance(other, Dual):
            return Dual(self.real + other, self.dual)
        
        dual = self.dual.copy()
        for tag, coef in other.dual.items():
            if tag not in dual:
                dual[tag] = coef 
            else:
                dual[tag] += coef 
        
        return Dual(self.real + other.real, dual)
    
    __radd__ = __add__ 

    def __sub__(self, other):
        return self + (-other)
    
    def __rsub__(self, other):
        return -(self - other)

    def __mul__(self, other):
        """
        z1 = a + be1
        z2 = c + de2 

        z1 * z2 = (ac + ade2 + cbe1 +  bd(e1e2))  and e1e2 = 0 
        """ 
        if not isinstance(other, Dual):
            dual = {tag: coef * other for tag, coef in self.dual.items() }
            return Dual(self.real * other, dual)
        
        dual = {}
        for tag, coef in self.dual.items():
            dual[tag] = other.real * coef 
        for tag, coef in other.dual.items():
            if not tag in dual: 
                dual[tag] = 0
            dual[tag] += self.real * coef  

        return Dual(self.real * other.real, dual)      

    __rmul__ = __mul__ 

    def __truediv__(self, other):
        if not isinstance(other, Dual):
            dual = {tag: coef / other for tag, coef in self.dual.items()}
            return Dual(self.real / other, dual)

        numerator = self * other.conjugate()
        return numerator / (self.real ** 2)
    
    def __rtruediv__(self, other):
        numerator = Dual(other, {})
        return numerator / self 
    
    def __pow__(self, power):
        """
        z = a + be 
        z^n = a^n + nC1 a^n-1 . be + nC2 a^n-2 . (be)^2 + ...  (all e^2 = 0)
        z^n = a^n + n.a^n-1.be 
        """
        mul = self.real ** (power - 1)
        dual = {tag : mul*coef for tag, coef in self.dual.items()}
        return Dual(self.real * mul, dual)
    
    def __exp__(self, power):
        """
        Taylor series: e^x = 1 + x/1! + x^2/2! + ...
        e^z = e^real . e ^ b.ei

        e^b.ei = 1 + b.ei/1 + 0.... (ei^2 = 0)

        e^z = e^a . (1 + be)
        """
        real = math.exp(self.real)
        dual = {tag : real * coef for tag, coef in self.dual.items()}
        return Dual(real, dual)

    def __log__(self):
        """
        ln(1+x) = x - x^2/2 + x^3 / 3 + x^4 / 4 + ...

        => ln(z) = ln(x + be) 
        => ln(x * (1 + be/x)) = ln(x) + ln(1 + be/x)
        => ln(x) + [(be/x) -(be/x)^2 / 2 + (be/x)^3/3 ..] (e^2 = 0)
        => ln(x) + be/x
        """
        dual = {tag: coef / self.real for tag, coef in self.dual.items()}
        return Dual(math.log(self.real), dual)