import os, unittest, random

import testlib
from genetrack import conf, util, logger

class Hdflib( unittest.TestCase ):
    'basic sequence class tests'
    
    def test_all(self):
        "Testing sequence operations"
        #self.assertEqual(1, 0)

def get_suite():
    "Returns the testsuite"
    tests  = [ 
        Hdflib,
    ]

    return testlib.make_suite( tests )

if __name__ == '__main__':
    suite = get_suite()
    logger.disable(None)
    unittest.TextTestRunner(verbosity=2).run( suite )

    