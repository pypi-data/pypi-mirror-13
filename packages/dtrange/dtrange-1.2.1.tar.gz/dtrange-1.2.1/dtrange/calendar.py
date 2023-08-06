from datetime import date, datetime, timedelta
from Datetime import Datetime

DAYS_IN_MONTH = (0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
DAYS_IN_MONTH_LEAP = (0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
DAYS_BEFORE_MONTH = (0, 0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334)
DAYS_BEFORE_MONTH_LEAP = (0, 0, 31, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335)

def day_of_year(dt, calendar):
    '''
    >>> day_of_year(datetime(2000, 2, 1), 'julian')
    32
    '''
    dim = days_in_months(dt.year, calendar)
    result = dt.day
    m = 1
    while m < dt.month:
        result += dim[m]
        m += 1

    return result

def day_of_year_date(doy, year, calendar):
    '''
    >>> day_of_year_date(32, 2000, 'julian')
    2000, 2, 1
    >>> day_of_year_date(367, 2000, 'julian')
    2001, 1, 1
    '''
    done = False
    while 1:
        dim = days_in_months(year, calendar)
        for month in range(1, 13):
            if doy <= dim[month]:
                done = True
                break
            doy -= dim[month]
        if done:
            break
        year += 1

    return year, month, doy

def date_plus_days(dt, days, calendar):
    '''Add days (integer) to a date for calendar.'''
    if 'gregorian' == calendar:
        return dt + timedelta(days=days)

    doy = day_of_year(dt, calendar)
    future = doy + days
    y,m,d = day_of_year_date(future, dt.year, calendar)

    if type(dt) == datetime:
        result = datetime(y, m, d, dt.hour, dt.minute, dt.second, dt.microsecond, dt.tzinfo)
    elif 'gregorian' != calendar:
        # Python 'date' fails when 30 days are used in Feb.
        result = Datetime(y, m, d)
    else:
        result = date(y, m, d)

    return result
    
def days_in_month(m, y, calendar):
    if 'gregorian' == calendar:
        if is_leap_year_gregorian(y):
            return DAYS_IN_MONTH_LEAP[m]
        else:
            return DAYS_IN_MONTH[m]
    elif 'julian' == calendar:
        if is_leap_year_julian(y):
            return DAYS_IN_MONTH_LEAP[m]
        else:
            return DAYS_IN_MONTH[m]
    elif 'leap' == calendar:
        return DAYS_IN_MONTH_LEAP[m]
    elif 'noleap' == calendar:
        return DAYS_IN_MONTH[m]
    elif '360' == calendar:
        return 30
    else:
        raise Exception('Unsupported calendar={0}'.format(calendar))

def days_in_months(y, calendar):
    '''Return array of days per month (index 1 is January).'''
    if is_leap_year(y, calendar):
        return DAYS_IN_MONTH_LEAP
    elif '360' == calendar:
        return [30]*13
    else:
        return DAYS_IN_MONTH

def days_in_year(y, calendar):
    if 'gregorian' == calendar:
        if is_leap_year_gregorian(y):
            return 366
        else:
            return 365
    elif 'julian' == calendar:
        if is_leap_year_julian(y):
            return 366
        else:
            return 365
    elif 'leap' == calendar:
        return 366
    elif 'noleap' == calendar:
        return 365
    elif '360' == calendar:
        return 360
    else:
        raise Exception('Unsupported calendar={0}'.format(calendar))

def is_leap_year(y, calendar):
    if 'gregorian' == calendar:
        return is_leap_year_gregorian(y)
    elif 'julian' == calendar:
        return is_leap_year_julian(y)
    elif 'leap' == calendar:
        return True
    else:
        return False

def is_leap_year_gregorian(y):
    if y % 400 == 0:
        return True
    elif y % 100 == 0:
        return False
    elif y % 4 == 0:
        return True
    else:
        return False

def is_leap_year_julian(y):
    return y % 4 == 0

def leap_years_before(y, calendar):
    '''Return number of years before input year that are leap.'''
    y -= 1
    if 'gregorian' == calendar:
        return y * 0.2425
    elif 'julian' == calendar:
        return y/4 
    elif 'leap' == calendar:
        return y
    else:
        return 0
    
def ordinal(dt, calendar):
    '''
    >>> ordinal(datetime(1,1,1), 'gregorian')
    1
    >>> ordinal(datetime(2,1,1), 'gregorian')
    366
    '''
    if 'gregorian' == calendar:
        t = type(dt)
        if t not in (date, datetime):
            dt = datetime(dt.year, dt.month, dt.day) 
        return dt.toordinal()
    elif 'julian' == calendar:
        if is_leap_year_julian(dt.year):
            mdays = DAYS_BEFORE_MONTH_LEAP[dt.month]
        else:
            mdays = DAYS_BEFORE_MONTH[dt.month]            
        nleap = int(dt.year/4)
        return 366*nleap + 365*(dt.year-nleap-1) + mdays + dt.day 
    elif 'noleap' == calendar:
        return 365*(dt.year-1) + DAYS_BEFORE_MONTH[dt.month] + dt.day 
    elif 'leap' == calendar:
        return 366*(dt.year-1) + DAYS_BEFORE_MONTH_LEAP[dt.month] + dt.day 
    else:
        return 360*(dt.year-1) + 30*(dt.month-1) + dt.day 
    
