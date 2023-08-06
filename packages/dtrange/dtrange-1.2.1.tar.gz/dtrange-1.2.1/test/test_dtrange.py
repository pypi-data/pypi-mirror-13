from dtrange import dtrange
from datetime import datetime, timedelta
import unittest


class TestDtrange(unittest.TestCase):
    def test_dtrange_bad_args(self):
        raised = False
        try: dtrange(datetime(1,1,1))
        except: raised = True
        
        self.assertTrue(raised)
        
        raised = False
        try: dtrange(datetime(1,1,1), stop=datetime(2,2,2))
        except: raised = True
        
        self.assertTrue(raised)
        
        raised = False
        try: dtrange(datetime(1,1,1), units='y', n=10)
        except: raised = True
        
        self.assertTrue(raised)
        
    def test_dtrange_stop_step(self):
        start = datetime(2000, 1, 1)
        stop = datetime(2000, 2, 1)
        step = timedelta(1)

        for it in dtrange(start, stop, step):
            pass

        expect = datetime(2000, 1, 31)
        self.assertEqual(expect, it)

    def test_dtrange_stop_step_endpoint(self):
        start = datetime(2000, 1, 1)
        stop = datetime(2000, 2, 1)
        step = timedelta(1)

        for it in dtrange(start, stop, step, endpoint=True):
            pass

        expect = datetime(2000, 2, 1)
        self.assertEqual(expect, it)

    def test_dtrange_stop_step_units(self):
        start = datetime(2000, 1, 1)
        stop = datetime(2000, 2, 1)

        for units in ['w', 'd']:
            for it in dtrange(start, stop, step=1, units=units, endpoint=True):
                pass

        self.assertEqual(stop, it)

        stop = datetime(2000, 1, 2)
        for units in ['h', 'min', 's']:
            for it in dtrange(start, stop, step=1, units=units, endpoint=True):
                pass

        self.assertEqual(stop, it)

        stop = datetime(2000, 1, 1, 0, 0, 0, 10)
        for units in ['ms', 'us']:
            for it in dtrange(start, stop, step=1, units=units, endpoint=True):
                pass

        self.assertEqual(stop, it)

    def test_dtrange_stop_step_units_year(self):
        start = datetime(2000, 1, 1)
        stop = datetime(2020, 1, 1)

        for it in dtrange(start, stop, step=1, units='y'):
            pass

        expect = datetime(2019, 1, 1)
        self.assertEqual(expect, it)

    def test_dtrange_stop_step_units_month(self):
        start = datetime(2000, 1, 1)
        stop = datetime(2002, 1, 1)

        for it in dtrange(start, stop, step=1, units='m', endpoint=1):
            pass

        self.assertEqual(stop, it)

    def test_dtrange_stop_n(self):
        start = datetime(2000, 1, 1)
        stop = datetime(2001, 1, 1)
        n = 10

        for ctr, it in enumerate(dtrange(start, stop, n=n, endpoint=False)):
            pass

        self.assertEqual(n, ctr+1)
        self.assertTrue(it < stop)

        for ctr, it in enumerate(dtrange(start, stop, n=n, endpoint=True)):
            pass

        self.assertEqual(n, ctr+1)
        self.assertEqual(stop, it)

    def test_dtrange_step_n(self):
        start = datetime(2000, 1, 1)
        step = timedelta(1)

        for it in dtrange(start, step=step, n=31):
            pass

        expect = datetime(2000, 1, 31)
        self.assertEqual(expect, it)

    def test_dtrange_step_n_units(self):
        start = datetime(2000, 1, 1)
        n = 10

        for units in ['y', 'm', 'w', 'd', 'h', 'min', 's', 'ms', 'us']:
            for ctr, it in enumerate(dtrange(start, step=1, n=n, units=units)):
                pass

            self.assertTrue(it > start)
            self.assertEqual(n, ctr + 1)


if '__main__' == __name__:
    unittest.main(verbosity=2)
