"""
Provide support for test skipping.

Based on work by Titus Brown in pygr
"""

import unittest, time
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

    def run(self, test):
        "Run the given test case or test suite."
        result = self._makeResult()
        startTime = time.time()
        test(result)
        stopTime = time.time()
        timeTaken = stopTime - startTime
        result.printErrors()
        #self.stream.writeln(result.separator2)
        run = result.testsRun

        if self.verbosity>0:
            self.stream.writeln("Ran %d test%s in %.3fs" %
                               (run, run != 1 and "s" or "", timeTaken))
            self.stream.writeln()

        if not result.wasSuccessful():
            self.stream.write("FAILED (")
            failed, errored = map(len, (result.failures, result.errors))
            if failed:
                self.stream.write("failures=%d" % failed)
            if errored:
                if failed: self.stream.write(", ")
                self.stream.write("errors=%d" % errored)
            self.stream.writeln(")")
        else:
            #self.stream.writeln("OK")
            pass
        return result

class TestProgram(unittest.TestProgram):
    
    def __init__(self, **kwargs):
        verbosity = kwargs.pop('verbosity', 1)
        if verbosity != 2:
            logger.disable('DEBUG')
        if kwargs.get('testRunner') is None:
            kwargs['testRunner'] = TestRunner(verbosity=verbosity)

        unittest.TestProgram.__init__(self, **kwargs)
