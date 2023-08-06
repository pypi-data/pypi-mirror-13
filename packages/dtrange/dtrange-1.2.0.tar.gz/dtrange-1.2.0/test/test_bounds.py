from bounds import bounds
from datetime import date
import unittest


class TestBounds(unittest.TestCase):
    def test_bounds(self):
        items = [1,2,3,4,10,15,20]
        n = len(items)
        
        res = bounds(items, 0)
        expect = (0,0)
        self.assertEqual(expect, res) 

        res = bounds(items, 1)
        expect = (0,0)
        self.assertEqual(expect, res) 

        res = bounds(items, 3.5)
        expect = (2,3)
        self.assertEqual(expect, res) 

        res = bounds(items, 13)
        expect = (4,5)
        self.assertEqual(expect, res) 

        res = bounds(items, 20)
        expect = (n-1,n-1)
        self.assertEqual(expect, res) 

        res = bounds(items, 30)
        expect = (n-1,n-1)
        self.assertEqual(expect, res) 

    def test_bounds_date(self):
        d0 = date(1,1,2)
        d1 = date(1,2,1)
        d2 = date(1,6,1)
        d3 = date(1,12,1)
        items = [d0,d1,d2,d3]

        res = bounds(items, date(1,1,1))
        expect = (0,0)
        self.assertEqual(expect, res) 

        res = bounds(items, date(1,1,2))
        expect = (0,0)
        self.assertEqual(expect, res) 

        res = bounds(items, date(1,1,10))
        expect = (0,1)
        self.assertEqual(expect, res) 

        res = bounds(items, date(1,2,1))
        expect = (1,2)
        self.assertEqual(expect, res) 

        res = bounds(items, date(1,3,1))
        expect = (1,2)
        self.assertEqual(expect, res) 

        res = bounds(items, date(1,6,1))
        expect = (2,3)
        self.assertEqual(expect, res) 

        res = bounds(items, date(3,1,1))
        expect = (3,3)
        self.assertEqual(expect, res) 


if '__main__' == __name__:
    unittest.main(verbosity=2)
