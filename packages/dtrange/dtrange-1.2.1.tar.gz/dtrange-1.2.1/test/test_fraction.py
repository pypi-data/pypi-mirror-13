from datetime import date, datetime, time
from fraction import dtfraction, dfraction, tfraction
import unittest


class TestFraction(unittest.TestCase):
    def test_dfraction(self):
        d1 = date(1,1,1)
        d2 = date(1,1,2)
        d3 = date(1,1,3)
        
        self.assertEqual(0., dfraction(d1, d1, d1))
        self.assertEqual(1., dfraction(d1, d2, d2))
        self.assertEqual(0., dfraction(d1, d1, d3))
        self.assertEqual(.5, dfraction(d1, d2, d3))

    def test_dtfraction(self):
        dt1 = datetime(1,1,1)
        dt2 = datetime(1,1,2)
        dt3 = datetime(1,1,3)
        
        self.assertEqual(0., dtfraction(dt1, dt1, dt1))
        self.assertEqual(1., dtfraction(dt1, dt2, dt2))
        self.assertEqual(0., dtfraction(dt1, dt1, dt3))
        self.assertEqual(.5, dtfraction(dt1, dt2, dt3))

    def test_tfraction(self):
        t1 = time(0,0,0)
        t2 = time(10,0,0)
        t3 = time(20,0,0)

        self.assertEqual(0., tfraction(t1, t1, t3))
        self.assertEqual(1., tfraction(t1, t3, t3))
        self.assertEqual(.5, tfraction(t1, t2, t3))

if '__main__' == __name__:
    unittest.main(verbosity=2)
