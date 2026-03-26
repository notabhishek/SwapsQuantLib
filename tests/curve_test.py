from core.curve import Curve
from datetime import datetime

curve = Curve(interpolation='log_linear', nodes = {
    datetime(2022, 1, 1) : 1.00,
    datetime(2022, 4, 1) : 0.9975,
    datetime(2022, 7, 1) : 0.9945,
})

print(f'{curve=}')
print(f'{curve[datetime(2022, 3, 15)]=}')
print(f'{curve[datetime(2022, 4, 1)]=}')