from Datetime import Datetime
import unittest


class TestBounds(unittest.TestCase):
    def test_str(self):
        d = Datetime(1,2,3)
        self.assertEqual('0001-02-03 00:00:00', str(d)) 

        d = Datetime(1,2,3,4,5,6)
        self.assertEqual('0001-02-03 04:05:06', str(d)) 

        d = Datetime(1,2,3,4,5,6,7)
        self.assertEqual('0001-02-03 04:05:06.000007', str(d)) 


if '__main__' == __name__:
    unittest.main(verbosity=2)