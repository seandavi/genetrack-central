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


def module_check(names, loglevel, exit=True):
    "Verifies that required modules are present"

    # required modules
    errflag = False
    

    loglevel = loglevel
    for name in names:
        try:
            __import__(name)
        except ImportError, exc:
            if not errflag:
                loglevel('Software requirements not met!')
                loglevel('See http://genetrack.bx.psu.edu for installation instructions')
                loglevel('-' * 20)
                errflag = True
            loglevel('missing module: %s' % name)
    
    # missing dependecies
    if exit and errflag:
        sys.exit()


def version_check():
    # verify some of the versions
    module_versions = [ ('tables', '2.0'), ('numpy', '1.1') ]
    for name, version in module_versions:
        try:
            mod = __import__(name)
            if mod.__version__ < version:
                raise Exception('%s of version %s or higher is required' % (name, version))
        except Exception, exc:
            logger.error( str(exc) )
            sys.exit()

#perform the module check    
required = ( 'numpy', 'tables', )
module_check( required, loglevel=logger.error )
version_check()

def check_server():
    "Checks for modules that are required to run the server"
    optional = ( 'django', 'pychartdir', 'Image' )
    module_check( optional, loglevel=logger.error )

try:
    # monkeypath pytables to disable the Natural Name warning
    import re
    from tables import path
    path._pythonIdRE = re.compile('.')
except:
    logger.warn( 'could not patch the Natural Name warning' )

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
