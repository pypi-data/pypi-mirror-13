from calendar import ordinal


def total_seconds(dt):
    if hasattr(dt, 'hour'):
        return dt.hour*3600. + dt.minute*60. + dt.second + dt.microsecond
    else:
        return 0.

def dtfraction(lower, mid, upper, calendar='gregorian'):
    '''Return fraction [0,1] for datetime between lower and upper bounds.'''
    ld = ordinal(lower, calendar) + total_seconds(lower)
    md = ordinal(mid,   calendar) + total_seconds(mid)
    ud = ordinal(upper, calendar) + total_seconds(upper)
    denom = ud - ld
    if denom:
        return (md - ld) / denom
    else:
        return 0. 

def dfraction(lower, mid, upper, calendar='gregorian'):
    return dtfraction(lower, mid, upper, calendar)

def tfraction(lower, mid, upper):
    lt = total_seconds(lower)
    mt = total_seconds(mid)
    ut = total_seconds(upper)
    denom = ut - lt
    if denom:
        return (mt - lt) / denom
    else:
        return 0.
