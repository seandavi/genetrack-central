#! /usr/bin/env python
"""
Test runner for main pygr tests.

Collects all files ending in _test.py and executes them.
"""

import os, sys, re, unittest, shutil, re, shutil
from testlib import testutil, testoptions
from testlib.unittest_extensions import TestRunner
from genetrack import logger, conf
import functional

def all_tests():
    "Returns all file names that end in _test.py"
    patt = re.compile("_tests.py$")
    mods = os.listdir(os.path.normpath(os.path.dirname(__file__)))
    mods = filter(patt.search, mods)
    mods = [ os.path.splitext(m)[0] for m in mods ]
    
    # some predictable order...
    mods.sort() 
    return mods

def run(targets, options):
    "Imports and runs the modules names that are contained in the 'targets'"
    
    success = errors = skipped = 0

    import_modules = [ 'doc_tests' ]
    # run the tests by importing the module and getting its test suite
    for name in targets:
        try:

            if name in import_modules:
                mod = __import__(name)
                suite = mod.get_suite()
            else:
                loader = unittest.TestLoader()
                suite = loader.loadTestsFromName(name)

            runner = TestRunner(verbosity=options.verbosity,
                                    descriptions=0)
            
            results = runner.run(suite)
            
            # count tests and errors
            success += results.testsRun - \
                       len(results.errors) - \
                       len(results.failures) - \
                       len(results.skipped)
            
            errors  += len(results.errors) + len(results.failures)
            skipped += len(results.skipped)

            # if we're in strict mode stop on errors
            if options.strict and errors:
                testutil.error( "strict mode stops on errors" )
                break

        except ImportError:
            testutil.error( "unable to import module '%s'" % name )

    # enable the logger
    logger.disable(None)

    # summarize the run
    testutil.info('=' * 59)
    testutil.info('''%s tests passed, %s tests failed, %s tests skipped; %d total''' % \
        (success, errors, skipped, success + errors + skipped))

    return (success, errors, skipped)

if __name__ == '__main__':
    # gets the prebuild option parser
    parser = testoptions.option_parser()

    # parse the options
    options, args = parser.parse_args()

    # modules: from command line args or all modules
    targets = args or all_tests()

    # get rid of the .py ending in case full module names were 
    # passed in the command line
    targets = [ t.rstrip(".py") for t in targets ]

    # exclusion mode
    if options.exclude:
        targets = [ name for name in all_tests() if name not in targets ]

    if options.verbosity == 0:
        logger.disable('INFO')
    elif options.verbosity == 1:
        logger.disable('DEBUG')
    elif options.verbosity >= 2:
        logger.disable(None)

    # cleans full entire test directory
    if options.reset:
        conf.reset_dir(conf.TEMP_DATA_DIR)
    
    # run all the tests
    if options.coverage:
        coverdir = conf.path_join(conf.TEST_DIR, 'coverage')
        good, bad, skip = testutil.generate_coverage(run, coverdir,
                                                     targets=targets,
                                                     options=options)
    else:
        good, bad, skip = run(targets=targets, options=options)

    if bad:
        sys.exit(-1)

    sys.exit(0)
