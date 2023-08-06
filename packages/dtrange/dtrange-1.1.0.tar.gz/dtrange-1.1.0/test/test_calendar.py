from calendar import day_of_year, day_of_year_date, date_plus_days
from datetime import datetime
import unittest


class TestCalendar(unittest.TestCase):
    def test_day_of_year(self):
        dt = datetime(2000, 2, 1)
        doy = day_of_year(dt, 'julian')
        expect = 32
        self.assertEqual(expect, doy)

        dt = datetime(2000, 3, 1)
        doy = day_of_year(dt, 'julian')
        expect = 61
        self.assertEqual(expect, doy)

        dt = datetime(2000, 12, 31)
        doy = day_of_year(dt, 'julian')
        expect = 366
        self.assertEqual(expect, doy)

        dt = datetime(2012, 2, 1)
        doy = day_of_year(dt, 'gregorian')
        expect = 32
        self.assertEqual(expect, doy)

        dt = datetime(2012, 3, 1)
        doy = day_of_year(dt, 'gregorian')
        expect = 61
        self.assertEqual(expect, doy)

        dt = datetime(2012, 12, 31)
        doy = day_of_year(dt, 'gregorian')
        expect = 366
        self.assertEqual(expect, doy)

        dt = datetime(2011, 12, 31)
        doy = day_of_year(dt, 'gregorian')
        expect = 365
        self.assertEqual(expect, doy)

        dt = datetime(2012, 3, 1)
        doy = day_of_year(dt, '360')
        expect = 61
        self.assertEqual(expect, doy)

        dt = datetime(2012, 12, 30)
        doy = day_of_year(dt, '360')
        expect = 360
        self.assertEqual(expect, doy)

        dt = datetime(2012, 3, 1)
        doy = day_of_year(dt, 'noleap')
        expect = 60
        self.assertEqual(expect, doy)

        dt = datetime(2012, 12, 31)
        doy = day_of_year(dt, 'noleap')
        expect = 365
        self.assertEqual(expect, doy)

        dt = datetime(2011, 2, 1)
        doy = day_of_year(dt, 'leap')
        expect = 32
        self.assertEqual(expect, doy)

        dt = datetime(2011, 3, 1)
        doy = day_of_year(dt, 'leap')
        expect = 61
        self.assertEqual(expect, doy)

        dt = datetime(2011, 12, 31)
        doy = day_of_year(dt, 'leap')
        expect = 366
        self.assertEqual(expect, doy)

    def test_day_of_year_date(self):
        ymd = day_of_year_date(31, 2000, 'julian')
        expect = (2000,1,31)
        self.assertEqual(expect, ymd)

        ymd = day_of_year_date(32, 2000, 'julian')
        expect = (2000,2,1)
        self.assertEqual(expect, ymd)

        ymd = day_of_year_date(366, 2000, 'julian')
        expect = (2000,12,31)
        self.assertEqual(expect, ymd)

        ymd = day_of_year_date(367, 2000, 'julian')
        expect = (2001,1,1)
        self.assertEqual(expect, ymd)

    def test_date_plus_days(self):
        d = datetime(2000,1,1)
        n = 30
        c = 'julian'
        res = date_plus_days(d, n, c)
        expect = datetime(2000,1,31)
        self.assertEqual(expect, res)

        d = datetime(2000,1,1)
        n = 60
        c = 'julian'
        res = date_plus_days(d, n, c)
        expect = datetime(2000,3,1)
        self.assertEqual(expect, res)

        d = datetime(2001,1,1)
        n = 60
        c = 'julian'
        res = date_plus_days(d, n, c)
        expect = datetime(2001,3,2)
        self.assertEqual(expect, res)

        d = datetime(2000,1,1)
        n = 365
        c = 'julian'
        res = date_plus_days(d, n, c)
        expect = datetime(2000,12,31)
        self.assertEqual(expect, res)

        d = datetime(2000,1,1)
        n = 366
        c = 'julian'
        res = date_plus_days(d, n, c)
        expect = datetime(2001,1,1)
        self.assertEqual(expect, res)

        d = datetime(2011,1,1)
        n = 30
        c = 'gregorian'
        res = date_plus_days(d, n, c)
        expect = datetime(2011,1,31)
        self.assertEqual(expect, res)

        d = datetime(2011,1,1)
        n = 59
        c = 'gregorian'
        res = date_plus_days(d, n, c)
        expect = datetime(2011,3,1)
        self.assertEqual(expect, res)

        d = datetime(2012,1,1)
        n = 60
        c = 'gregorian'
        res = date_plus_days(d, n, c)
        expect = datetime(2012,3,1)
        self.assertEqual(expect, res)

        d = datetime(2011,1,1)
        n = 365
        c = 'gregorian'
        res = date_plus_days(d, n, c)
        expect = datetime(2012,1,1)
        self.assertEqual(expect, res)

        d = datetime(2012,1,1)
        n = 366
        c = 'gregorian'
        res = date_plus_days(d, n, c)
        expect = datetime(2013,1,1)
        self.assertEqual(expect, res)

        d = datetime(2012,1,1)
        n = 365
        c = 'noleap'
        res = date_plus_days(d, n, c)
        expect = datetime(2013,1,1)
        self.assertEqual(expect, res)

        d = datetime(2012,1,1)
        n = 366
        c = 'noleap'
        res = date_plus_days(d, n, c)
        expect = datetime(2013,1,2)
        self.assertEqual(expect, res)

        d = datetime(2011,1,1)
        n = 365
        c = 'leap'
        res = date_plus_days(d, n, c)
        expect = datetime(2011,12,31)
        self.assertEqual(expect, res)

        d = datetime(2011,1,1)
        n = 366
        c = 'leap'
        res = date_plus_days(d, n, c)
        expect = datetime(2012,1,1)
        self.assertEqual(expect, res)

        d = datetime(2011,1,1)
        n = 360
        c = '360'
        res = date_plus_days(d, n, c)
        expect = datetime(2012,1,1)
        self.assertEqual(expect, res)


if '__main__' == __name__:
    unittest.main(verbosity=2)

