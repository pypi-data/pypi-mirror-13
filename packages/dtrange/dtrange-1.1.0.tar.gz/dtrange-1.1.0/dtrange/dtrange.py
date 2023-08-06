from calendar import days_in_month, days_in_year, date_plus_days
from datetime import datetime, timedelta
from utils import timedelta_from_uniform_units


class dtrange(object):
    '''
    datetime iterator.
    '''

    def __init__(self, start, stop=None, step=None, n=None, units='d',
                 endpoint=False, calendar='gregorian'):
        '''
        Parameters
        ----------
        start : datetime
            First inclusive datetime.
        stop : datetime, optional
            Optional. Inclusive if closed=True.
        step : timedelta or number, optional
            Requires units if is a number.
        n : number, optional
            Number of divisions between start and stop.
        units : str, optional
            y=year, m=month, w=week, d=day, h=hour, min=minutes
            s=seconds, ms=milliseconds, us=microseconds
            Default is 'd'.
        endpoint : bool, optional
            If true, then stop is included, otherwise use half-open bounds.
            Default is False.
        calendar : str
            One of [360, gregorian, julian, leap, noleap].
            Default is gregorian.
        '''
        self.calendar = calendar
        self.current = start
        self.endpoint = endpoint
        self.first_iteration = True
        self.n = n
        self.non_uniform_units = None
        self.step = step
        self.stop = stop

        def parse_step_as_number():
            if type(step) != timedelta:
                if not units:
                    raise Exception('Expected units.')
                if units in 'my':
                    self.non_uniform_units = units
                else:
                    self.step = timedelta_from_uniform_units(units)

        if stop:
            if step:
                parse_step_as_number()
            elif n:
                if endpoint:
                    n -= 1
                self.step = (stop - start) / n
            else:
                raise Exception('Expected step or n.')
        elif step and units and n:
            parse_step_as_number()

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        if not self.first_iteration:
            if self.non_uniform_units:
                self.next_non_uniform()
            else:
                self.next_uniform()
        else:
            self.first_iteration = False

        return self.next_return()

    def next_non_uniform(self):
        if 'y' == self.non_uniform_units:
            self.next_non_uniform_year()
        else:
            self.next_non_uniform_month()

    def next_non_uniform_month(self):
        for _ in range(self.step):
            days = days_in_month(self.current.month,
                                 self.current.year,
                                 self.calendar)
            self.current = date_plus_days(self.current, days, self.calendar)

    def next_non_uniform_year(self):
        for _ in range(self.step):
            days = days_in_year(self.current.year, self.calendar)
            self.current = date_plus_days(self.current, days, self.calendar)

    def next_return(self):
        if self.endpoint:
            if self.current > self.stop:
                raise StopIteration
        else:
            if self.stop:
                if self.current >= self.stop:
                    raise StopIteration
            elif self.n <= 0:
                raise StopIteration
            else:
                self.n -= 1

        return self.current

    def next_uniform(self):
        if 0 == self.step.microseconds + self.step.seconds:
            self.current = date_plus_days(self.current, self.step.days,
                                          self.calendar)
        else:
            # TODO: Exotic calendar time arithmetic.
            self.current += self.step


#     LICENSE BEGIN
#
#     dtrange - Datetime, date and time range iterators.
#     Copyright (C) 2016  Remik Ziemlinski
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#     LICENSE END
