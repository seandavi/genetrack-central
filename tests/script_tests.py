import os, unittest, random

import testlib
from genetrack import conf, util, logger, scripts

class ScriptTests( unittest.TestCase ):
    'basic sequence class tests'
    
    def test_bed2genetrack(self):
        "Testing bed2genetrack transformation"
        from genetrack.scripts import bed2genetrack

        inpfile = conf.testdata('short-data.bed', verify=True)
        outfile = conf.tempdata('short-data.genetrack')
        bed2genetrack.transform(inpfile, outfile)

def get_suite():
    "Returns the testsuite"
    tests  = [ 
        ScriptTests,
    ]

    return testlib.make_suite( tests )

if __name__ == '__main__':
    suite = get_suite()
    logger.disable(None)
    unittest.TextTestRunner(verbosity=2).run( suite )

    