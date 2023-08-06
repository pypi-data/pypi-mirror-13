import sys
import unittest
from test_bounds import *
from test_calendar import *
from test_Datetime import *
from test_drange import *
from test_dtrange import *
from test_fraction import *
from test_trange import *
from test_utils import *


if '__main__' == __name__:
    print(sys.version)
    unittest.main(verbosity=2)
