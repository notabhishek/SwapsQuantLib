from core.schedule import Schedule
from datetime import datetime

schedule = Schedule(start=datetime(2022, 1, 1), tenor_months=11, period_months=3)
print(schedule)