from .calendar import ordinal


def time_ordinal(dt):
    '''Return fraction of day [0-1].'''
    if hasattr(dt, 'hour'):
        t = dt.hour*3600. + dt.minute*60. + dt.second + dt.microsecond/1.0e6
        return t / 86400.
    else:
        return 0.

def dtfraction(lower, mid, upper, calendar='gregorian'):
    '''Return fraction [0,1] for datetime between lower and upper bounds.'''
    ld = ordinal(lower, calendar) + time_ordinal(lower)
    md = ordinal(mid,   calendar) + time_ordinal(mid)
    ud = ordinal(upper, calendar) + time_ordinal(upper)
    denom = ud - ld
    if denom:
        return (md - ld) / denom
    else:
        return 0.

def dfraction(lower, mid, upper, calendar='gregorian'):
    return dtfraction(lower, mid, upper, calendar)

def tfraction(lower, mid, upper):
    lt = time_ordinal(lower)
    mt = time_ordinal(mid)
    ut = time_ordinal(upper)
    denom = ut - lt
    if denom:
        return (mt - lt) / denom
    else:
        return 0.
