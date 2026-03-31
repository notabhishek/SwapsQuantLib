from core.schedule import Schedule
from datetime import datetime

schedule = Schedule(start=datetime(2022, 1, 1), tenor=11, period=3, tenor_type='M')
print(schedule)