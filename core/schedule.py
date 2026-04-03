from datetime import datetime, timedelta
from core.dateutils import add_months_modfollowing

class Schedule:
    def __init__(self, start: datetime, tenor: int, period: int, tenor_type: str = 'M'):
        self.start = start 

        # TODO: add tenor_type W, Y
        if tenor_type == 'M':
            self.add_op = add_months_modfollowing
        elif tenor_type == 'D':
            self.add_op = add_days
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
