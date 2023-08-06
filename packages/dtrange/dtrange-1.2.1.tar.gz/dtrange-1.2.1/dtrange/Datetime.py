class Datetime:
    '''A container that won't fail like datetime with exotic calendars.'''
    def __init__(self, y, m, d, h=0, mn=0, s=0, us=0):
        self.year = y
        self.month = m
        self.day = d
        self.hour = h
        self.minute = mn
        self.second = s
        self.microsecond = us
        
    def __cmp__(self, other):
        return self.cmp(other)

    def __eq__(self, other):
        return self.cmp(other) == 0

    def __ge__(self, other):
        return self.cmp(other) >= 0

    def __gt__(self, other):
        return self.cmp(other) > 0

    def __le__(self, other):
        return self.cmp(other) <= 0

    def __lt__(self, other):
        return self.cmp(other) < 0

    def __ne__(self, other):
        return self.cmp(other) != 0

    def __repr__(self):
        return 'dtrange.Datetime(%d, %d, %d, %d, %d, %d, %d)' % \
                (self.year, self.month, self.day,
                 self.hour, self.minute, self.second, self.microsecond)

    def __str__(self):
        second = self.second
        if self.microsecond:
            subsec = self.microsecond / 1.0e6
            second += int(subsec) # In case overflow.
            frac = subsec % 1            
            micro = ('%f' % (frac)).lstrip('0')
        else:
            micro = ''
        
        return '%04d-%02d-%02d %02d:%02d:%02d%s' % \
                (self.year, self.month, self.day, self.hour, self.minute, second, micro)
    
    def cmp(self, other):
        if hasattr(other, 'second'):
            return self.cmp_datetime(other.year, other.month, other.day,
                                     other.hour, other.minute, other.second,
                                     other.microsecond)
        else:
            return self.cmp_date(other.year, other.month, other.day)
            
    def cmp_date(self, y, m, d):
        c = self.year - y
        if c: return c

        c = self.month - m
        if c: return c

        c = self.day - d
        if c: return c
    
        return 0
    
    def cmp_datetime(self, y, m, d, h, mn, s, us):
        c = self.cmp_date(y, m, d)
        if c: return c

        c = self.hour - h
        if c: return c

        c = self.minute - mn
        if c: return c

        c = self.second - s
        if c: return c

        c = self.microsecond - us
        if c: return c

        return 0

