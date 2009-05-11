"""
Module that contains configuration
"""
import sys, os
import logger

def error(msg):
    "Fatal error handler"
    logger.error( msg )
    sys.exit()

# version check
if sys.version_info < (2, 5):
    error( 'genetrack requires python 2.5 or higher' )

def path_join(*args):
    "Builds absolute path"
    return os.path.abspath(os.path.join(*args))

# set up paths relative to the location of this file
curr_dir = os.path.dirname( __file__ )
base_dir = path_join( curr_dir, '..' )
test_dir = path_join( base_dir, 'tests' )
temp_dir = path_join( test_dir, 'tempdir' )
test_data_dir = path_join( test_dir, 'testdata' )
coverage_dir = path_join( test_dir, 'coverage' )

def module_check():
    "Verifies that required modules are present"
    try:
        import numpy, tables, django, twill
    except ImportError, exc:
        error('software requirements not met: %s' % exc)

    try:
        import pychartdir
    except ImportError, exc:
        logger.error('software requirements not met: %s' % exc)
        logger.error('charting module missing, some visualizations may not work')

#perform the module check    
module_check()

# make the temporary data directory
if not os.path.isdir( temp_dir ):
    os.mkdir( temp_dir )

# path creation utilites
def appdata(*args):
    "Path to temporary test"
    return path_join( *args )

def testdata(*args):
    "Path to test data"
    return appdata(test_data_dir, *args)

def tempdata(*args):
    "Path to temporary test data"
    return appdata(temp_dir, *args)

def test(verbose=0):
    "Performs module level testing"
    import doctest
    doctest.testmod( verbose=verbose )

if __name__ == "__main__":
    test()