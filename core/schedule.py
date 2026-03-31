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

class Schedule:
    def __init__(self, start: datetime, tenor: int, period: int, tenor_type: str = 'M'):
        self.start = start 
        
        # TODO: add tenor_type W, Y
        if tenor_type == 'M':
            self.add_op = add_months_modfollowing
        elif tenor_type == 'D':
            self.add_op == add_days
        else: 
            raise ValueError(f'Only support tenor_type D, M but got {tenor_type}')
        
        self.end = self.add_op(start, tenor)
        self.tenor = tenor
        self.period = period
        
        self.dcf_convention = timedelta(days = 365) # Using ACT/365 for day count fraction
        self.num_periods = (self.tenor + self.period - 1) // self.period 
    
    @property
    def data(self):
        schedule = []
        period_start = self.start 
        
        # Insert num_periods-1 periods (start, end, dcf)
        for _ in range(self.num_periods - 1):
            period_end = self.add_op(period_start, self.period)
            period_dcf = (period_end - period_start) / self.dcf_convention

            period = [period_start, period_end, period_dcf]
            schedule.append(period)
            period_start = period_end

        last_period_dcf = (self.end - period_start) / self.dcf_convention
        schedule.append([period_start, self.end, last_period_dcf])
        return schedule
    
    def __repr__(self):
        output = "period_start | period_end | period_DCF\n"
        format = '%Y-%b-%d'
        for period in self.data:
            output += f'{period[0].strftime(format)} | ' \
                      f'{period[1].strftime(format)} | ' \
                      f'{period[2]:.6f}\n'
        
        return output
