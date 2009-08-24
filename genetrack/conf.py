"""
Configuration namespace.


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
    errflag = False
    names = ( 'numpy', 'tables', 'django', 'pychartdir', 'Image' )

    for name in names:
        try:
            __import__(name)
        except ImportError, exc:
            if not errflag:
                logger.error('Software requirements not met!')
                logger.error('See http://genetrack.bx.psu.edu for installation instructions')
                logger.error('-' * 20)
                errflag = True
            logger.error('missing module: %s' % name)

    if errflag:
        logger.error('-' * 20)
        sys.exit()

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
