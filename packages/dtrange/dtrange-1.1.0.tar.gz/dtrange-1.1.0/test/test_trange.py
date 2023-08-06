from trange import trange
from datetime import time, timedelta
import unittest


class TestTrange(unittest.TestCase):
    def test_trange_stop_step(self):
        start = time(0, 0, 0)
        stop = time(0, 1, 0)
        step = timedelta(seconds=1)

        for i,it in enumerate(trange(start, stop, step)):
            pass
        expect = time(0, 0, 59)
        self.assertEqual(expect, it)

        for i,it in enumerate(trange(start, stop, step, endpoint=True)):
            pass
        self.assertEqual(stop, it)


if '__main__' == __name__:
    unittest.main(verbosity=2)
