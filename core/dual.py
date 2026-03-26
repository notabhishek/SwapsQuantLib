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
        pass 