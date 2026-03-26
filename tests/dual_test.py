from core.dual import Dual 

def f(x, y):
    return (x ** 2) * y 

"""
f = x^2 * y
df / dx = 2xy 
df / dy = x^2
"""

# Only calculates f(x,y)
print(f'{f(x=2.5, y=3.5)=}')

# Calculates f(x,y), df/dx, df/dy
print(f'{f(x=Dual(2.5, {'x' : 1}), y=Dual(3.5, {'y': 1}))}')