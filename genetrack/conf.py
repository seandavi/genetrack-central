"""
Module that contains configuration
"""
import sys, os, shutil
import logger

# Python version check
if sys.version_info < (2, 5):
    logger.error( 'genetrack requires python 2.5 or higher' )
    sys.exit()

def path_join(*args):
    "Builds absolute path"
    return os.path.abspath(os.path.join(*args))

# set up paths relative to the location of this file
curr_dir = os.path.dirname( __file__ )
BASE_DIR = path_join( curr_dir, '..' )
TEST_DIR = path_join( BASE_DIR, 'tests' )
TEST_DATA_DIR = path_join( TEST_DIR, 'testdata' )
TEMP_DATA_DIR = path_join( TEST_DIR, 'tempdir' )
COVERAGE_DIR = path_join( TEST_DIR, 'coverage' )

def module_check():
    "Verifies that required modules are present"

    # required modules
    try:
        import numpy, tables, django
    except ImportError, exc:
        logger.error('software requirements not met: %s' % exc)
        logger.error('see http://genetrack.bx.psu.edu for installation instructions')
        sys.exit()

    # optional modules
    try:
        import pychartdir
    except ImportError, exc:
        logger.error('software requirements not met: %s' % exc)
        logger.error('charting module missing, some visualizations may not work')
        logger.error('see http://genetrack.bx.psu.edu for installation instructions')

#perform the module check    
module_check()

def reset_dir(path):
    "Resets a directory path"
    if os.path.isdir( path ):
        shutil.rmtree( path)
        os.mkdir( path )

# create the temporary data directory if not present
if not os.path.isdir( TEMP_DATA_DIR ):
    os.mkdir( TEMP_DATA_DIR )

def testdata(*args, **kwds):
    "Generates paths to test data"
    path = path_join(TEST_DATA_DIR, *args)
    if 'verify' in kwds:
        if not os.path.isfile(path):
            raise IOError("file '%s' not found" % path )
    return path

def tempdata(*args):
    "Generates paths to temporary data"
    return path_join(TEMP_DATA_DIR, *args)

def test(verbose=0):
    "Performs module level testing"
    import doctest
    doctest.testmod( verbose=verbose )

if __name__ == "__main__":
    test()