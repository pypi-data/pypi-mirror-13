from datetime import date, datetime, timedelta
from Date import Date

DAYS_IN_MONTH = (0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
DAYS_IN_MONTH_LEAP = (0, 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)


def day_of_year(dt, c):
    '''
    >>> day_of_year(datetime(2000, 2, 1), 'julian')
    32
    '''
    dim = days_in_months(dt.year, c)
    result = dt.day
    m = 1
    while m < dt.month:
        result += dim[m]
        m += 1

    return result

def day_of_year_date(doy, year, c):
    '''
    >>> day_of_year_date(32, 2000, 'julian')
    2000, 2, 1
    >>> day_of_year_date(367, 2000, 'julian')
    2001, 1, 1
    '''
    done = False
    while 1:
        dim = days_in_months(year, c)
        for month in range(1, 13):
            if doy <= dim[month]:
                done = True
                break
            doy -= dim[month]
        if done:
            break
        year += 1

    return year, month, doy

def date_plus_days(dt, days, c):
    '''Add days (integer) to a date for calendar.'''
    if 'gregorian' == c:
        return dt + timedelta(days=days)

    doy = day_of_year(dt, c)
    future = doy + days
    y,m,d = day_of_year_date(future, dt.year, c)

    if type(dt) == datetime:
        result = datetime(y, m, d, dt.hour, dt.minute, dt.second, dt.microsecond, dt.tzinfo)
    elif 'gregorian' != c:
        # Python 'date' fails when 30 days are used in Feb.
        result = Date(y, m, d)
    else:
        result = date(y, m, d)

    return result

def days_in_month(m, y, c):
    if 'gregorian' == c:
        if is_leap_year_gregorian(y):
            return DAYS_IN_MONTH_LEAP[m]
        else:
            return DAYS_IN_MONTH[m]
    elif 'julian' == c:
        if is_leap_year_julian(y):
            return DAYS_IN_MONTH_LEAP[m]
        else:
            return DAYS_IN_MONTH[m]
    elif 'leap' == c:
        return DAYS_IN_MONTH_LEAP[m]
    elif 'noleap' == c:
        return DAYS_IN_MONTH[m]
    elif '360' == c:
        return 30
    else:
        raise Exception('Unsupported calendar={0}'.format(c))

def days_in_months(y, c):
    if is_leap_year(y, c):
        return DAYS_IN_MONTH_LEAP
    elif '360' == c:
        return [30]*13
    else:
        return DAYS_IN_MONTH

def days_in_year(y, c):
    if 'gregorian' == c:
        if is_leap_year_gregorian(y):
            return 366
        else:
            return 365
    elif 'julian' == c:
        if is_leap_year_julian(y):
            return 366
        else:
            return 365
    elif 'leap' == c:
        return 366
    elif 'noleap' == c:
        return 365
    elif '360' == c:
        return 360
    else:
        raise Exception('Unsupported calendar={0}'.format(c))

def is_leap_year(y, c):
    if 'gregorian' == c:
        return is_leap_year_gregorian(y)
    elif 'julian' == c:
        return is_leap_year_julian(y)
    elif 'leap' == c:
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

