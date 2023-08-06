class Date:
    def __init__(self, y, m, d):
        self.year = y
        self.month = m
        self.day = d

    def __cmp__(self, other):
        return self.cmp(other.year, other.month, other.day)

    def __eq__(self, other):
        return self.cmp(other.year, other.month, other.day) == 0

    def __ge__(self, other):
        return self.cmp(other.year, other.month, other.day) >= 0

    def __gt__(self, other):
        return self.cmp(other.year, other.month, other.day) > 0

    def __le__(self, other):
        return self.cmp(other.year, other.month, other.day) <= 0

    def __lt__(self, other):
        return self.cmp(other.year, other.month, other.day) < 0

    def __ne__(self, other):
        return self.cmp(other.year, other.month, other.day) != 0

    def __repr__(self):
        return 'dtrange.Date(%d, %d, %d' % (self.year, self.month, self.day)

    def __str__(self):
        return '%04d-%02d-%02d' % (self.year, self.month, self.day)

    def cmp(self, y, m, d):
        c = self.year - y
        if c: return c

        c = self.month - m
        if c: return c

        c = self.day - d
        if c: return c

        return 0

