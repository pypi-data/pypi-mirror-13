from Date import Date
from dtrange import dtrange
from utils import date_from_datetime

class drange(object):
    '''
    Date iterator.
    '''

    def __init__(self, start, stop=None, step=None, n=None, units='d',
                 endpoint=False, calendar='gregorian'):
        '''
        Parameters
        ----------
        start : date
            First inclusive datetime.
        stop : date, optional
            Optional. Inclusive if closed=True.
        step : timedelta or number, optional
            Requires units if is a number.
        n : number, optional
            Number of divisions between start and stop.
        units : str, optional
            y=year, m=month, w=week, d=day
            Default is 'd'.
        endpoint : bool, optional
            If true, then stop is included, otherwise use half-open bounds.
            Default is False.
        calendar : str
            One of [360, gregorian, julian, leap, noleap].
            Default is gregorian.
        '''
        self.dtrange = dtrange(start, stop=stop, step=step, n=n, units=units,
                               endpoint=endpoint, calendar=calendar)

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        self.dtrange.next()
        if 'gregorian' != self.dtrange.calendar:
            return Date(self.dtrange.current.year,
                        self.dtrange.current.month,
                        self.dtrange.current.day)
        else:
            return date_from_datetime(self.dtrange.current)


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
