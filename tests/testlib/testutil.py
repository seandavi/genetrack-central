import pathfix
from genetrack import conf
from genetrack.logger import debug, info, warn, error

import os, sys, unittest, re, time, shutil


# enables tests if biopython is present
try:
    import Bio
    biopython = True
except ImportError, exc:
    biopython = False

def path_join(*args):
    return os.path.abspath(os.path.join(*args))

def stop( text ):
    "Unrecoverable error"
    error ( text )
    sys.exit()

class Timer:
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        self.start = time.time()

    def display(self, msg, reps=1):
        total = (time.time() - self.start )

        if reps == 1:
            info( "%s takes %.3f seconds" % (msg, total) )
        else:
            value = total/reps
            info( "%s performs at %.3f per second" % (msg, value) )

        self.reset()

def reset_tempdir( tempdir=None ):
    "Deletes and recreates the temporary directory"
    tempdir = tempdir or conf.temp_data_dir
    if os.path.isdir( tempdir ):
        shutil.rmtree( tempdir )
    os.mkdir( tempdir )

def make_suite( tests ):
    "Makes a test suite from a list of TestCase classes"
    loader = unittest.TestLoader().loadTestsFromTestCase
    suites = map( loader, tests )
    return unittest.TestSuite( suites )

def generate_coverage( func, path, *args, **kwds):
    """
    Generates code coverage for the function 
    and places the results in the path
    """

    import figleaf
    from figleaf import annotate_html

    # Fix for figleaf misbehaving. It is adding a logger at root level 
    # and that will add a handler to all subloggers (ours as well)
    # needs to be fixed in figleaf
    import logging
    root = logging.getLogger()
    # remove all root handlers
    for hand in root.handlers: 
        root.removeHandler(hand)

    if os.path.isdir( path ):
        shutil.rmtree( path )       
    
    info( "collecting coverage information" )

    figleaf.start() 
    # execute the function itself
    return_vals = func( *args, **kwds)
    figleaf.stop()
    
    info( 'generating coverage' )
    coverage = figleaf.get_data().gather_files()
    
    annotate_html.prepare_reportdir( path )
    
    # skip python modules and the test modules
    regpatt  = lambda patt: re.compile( patt, re.IGNORECASE )
    patterns = map( regpatt, [ 'python', 'tests', 'django', 'path*' ] )
    annotate_html.report_as_html( coverage, path, exclude_patterns=patterns, files_list='')
    
    return return_vals

if __name__ == '__main__':
    pass