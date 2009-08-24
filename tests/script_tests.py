import os, unittest, random

import testlib
from genetrack import conf, util, logger, scripts

class ScriptTests( unittest.TestCase ):
    """
    Testing scripts
    """
    
    def test_tabs2genetrack(self):
        "Testing bed2genetrack transformation"
        from genetrack.scripts import tabs2genetrack

        inpfile = conf.testdata('short-data.bed', verify=True)
        outfile = conf.tempdata('short-data.genetrack')
        tabs2genetrack.transform(inpfile, outfile, format='BED')

def get_suite():
    "Returns the testsuite"
    tests  = [ 
        ScriptTests,
    ]

    return testlib.make_suite( tests )

if __name__ == '__main__':
    suite = get_suite()
    logger.disable('DEBUG')
    unittest.TextTestRunner(verbosity=2).run( suite )

    