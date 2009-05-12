"""
Provide support for test skipping.

Based on work by Titus Brown in pygr
"""

import unittest
import pathfix
from genetrack import logger

class SkipTest(Exception):
    pass

class TestResult(unittest._TextTestResult):

    def __init__(self, *args, **kwargs):
        unittest._TextTestResult.__init__(self, *args, **kwargs)
        self.skipped = []
        
    def addError(self, test, err):
        exc_type, val, _ = err
        if issubclass(exc_type, SkipTest):
            self.skipped.append((self, val))
            if self.showAll:                         
                # report skips: SKIP/S
                self.stream.writeln("SKIP")
            elif self.dots:
                self.stream.write('S')
        else:
            unittest._TextTestResult.addError(self, test, err)

class TestRunner(unittest.TextTestRunner):
    """
    Support running tests that understand SkipTest.
    """
    def _makeResult(self):
        return TestResult(self.stream, self.descriptions,
                              self.verbosity)

class TestProgram(unittest.TestProgram):
    
    def __init__(self, **kwargs):
        verbosity = kwargs.pop('verbosity', 1)
        if verbosity != 2:
            logger.disable('DEBUG')
        if kwargs.get('testRunner') is None:
            kwargs['testRunner'] = TestRunner(verbosity=verbosity)

        unittest.TestProgram.__init__(self, **kwargs)
