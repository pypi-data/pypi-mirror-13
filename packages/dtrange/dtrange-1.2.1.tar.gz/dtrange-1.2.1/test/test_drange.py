from drange import drange
from datetime import date, timedelta
import unittest


class TestDrange(unittest.TestCase):
    def test_drange_stop_step(self):
        start = date(2000, 1, 1)
        stop = date(2000, 2, 1)
        step = timedelta(1)

        for it in drange(start, stop, step):
            pass
        expect = date(2000, 1, 31)
        self.assertEqual(expect, it)

        for it in drange(start, stop, step, endpoint=True):
            pass
        self.assertEqual(stop, it)


if '__main__' == __name__:
    unittest.main(verbosity=2)
