from datetime import datetime, timedelta

# Add n months to date, keeping modified following convention 
def add_months_modfollowing(start: datetime, months: int) -> datetime:
    year_roll = (start.month - 1 + months) // 12
    
    month = (start.month + months) % 12 
    month = month if month != 0 else 12 

    try:
        return datetime(start.year + year_roll, month, start.day)
    except ValueError: # Not a valid date (invalid day)
        # try with day-1
        return add_months_modfollowing(datetime(start.year, start.month, start.day - 1), months)

# add n days to date 
def add_days(start: datetime, days: int) -> datetime: 
    return start + timedelta(days = days)