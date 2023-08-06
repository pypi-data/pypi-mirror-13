from datetime import datetime, timedelta


DAYS_IN_MONTH = (0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
DAYS_IN_MONTH_LEAP = (0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)


def is_leap_year(y):
    if y % 400 == 0:
        return True
    elif y % 100 == 0:
        return False
    elif y % 4 == 0:
        return True
    else:
        return False


def timedelta_from_uniform_units(units):
    '''Return timedelta for units char.'''
    c = units[0]
    if 'd' == c:
        r = timedelta(1)
    elif 'w' == c:
        r = timedelta(7)
    elif 's' == c:
        r = timedelta(seconds=1)
    elif 'h' == c:
        r = timedelta(hours=1)
    elif 'us' == units:
        r = timedelta(microseconds=1)
    elif 'ms' == units:
        r = timedelta(milliseconds=1)
    elif 'min' == units:
        r = timedelta(minutes=1)
    else:
        raise Exception('Unsupported timedelta units={0}'.format(units))

    return r


class dtrange(object):
    '''
    Gregorian datetime iterator.
    '''

    def __init__(self, start, stop=None, step=None, n=None, units='d',
                 endpoint=False):
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
        '''
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
            if is_leap_year(self.current.year):
                days = DAYS_IN_MONTH_LEAP[self.current.month]
            else:
                days = DAYS_IN_MONTH[self.current.month]

            self.current += timedelta(days=days)

    def next_non_uniform_year(self):
        for _ in range(self.step):
            if is_leap_year(self.current.year):
                days = 366
            else:
                days = 365

            self.current += timedelta(days=days)

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
