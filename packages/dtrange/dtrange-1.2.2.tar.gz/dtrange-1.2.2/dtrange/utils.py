from datetime import date, timedelta


def date_from_datetime(dt):
    return date(dt.year, dt.month, dt.day)

def timedelta_from_uniform_units(units):
    '''Return timedelta for units [day, week, sec, hour, min, us, ms].'''
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

