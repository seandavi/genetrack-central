"""
Logging functions.

Upon import creates a module level log class (log) and 
the following logging functions::

    debug, info, warn and error

The default formatters will print out the function the log was triggered from.
"""

import sys, logging

# python 2.5 logging will be differnt
PYTHON25 = sys.version_info >= (2, 5)

def get_logger( name='yeti-logger', stream=sys.stdout, formatter=None):
    """
    Returns a logger

    >>> disable('INFO')
    >>> info( 'logtest, this message SHOULD NOT be visible' )
    >>> disable()
    >>> info( 'logtest, this message should be visible' )
    >>> disable('DEBUG')
    >>> debug( 'logtest, this message SHOULD NOT be visible' )
    >>> info( 'logtest, this message should be visible' )   
    """
    logp = logging.getLogger(name)

    # this is needed in case the process is 
    # forked/multithreaded; loggers exist in a global scope 
    # we don't want each import to duplocate this handler
    if not logp.handlers:
        console = logging.StreamHandler(stream)
        console.setLevel(logging.DEBUG )
        if PYTHON25:
            format = '%(levelname)s %(module)s.%(funcName)s: %(message)s'    
        else:
            format = '%(levelname)s %(module)s: %(message)s'    

        formatter = formatter or logging.Formatter(format)
        console.setFormatter(formatter)
        logp.addHandler(console)
        logp.setLevel(logging.DEBUG)
    return logp

def disable( level=None ):
    """
    Disables logging levels
    Levels: DEBUG, INFO, WARNING, ERROR

    >>> disable('INFO')
    >>> info( 'logtest, this message SHOULD NOT be visible' )
    """
    level = str(level)
    store = dict( NOTSET=0, DEBUG=10, INFO=20, WARNING=30, ERROR=40)
    
    # also take numerical values
    store['0'] = 20
    store['1'] = 10
    store['2'] = 0

    value = store.get( level.upper(), 0)
    logging.disable( value )

# populate some loggers by default
log = get_logger()
debug, info, warn, error = log.debug, log.info, log.warn, log.error

# disable DEBUG level logging by default
disable('DEBUG')

def test( verbose=0 ):
    "Performs module level testing"
    import doctest
    doctest.testmod( verbose=verbose )

def OptionParser(usage=None):
    "An option parser that can disable various logger levels"
    from optparse import OptionParser

    parser = OptionParser(usage=usage)
    
    parser.add_option(
        '-v', '--verbosity', action="store", 
        dest="verbosity", type="int", default=1, 
        help="sets the verbosity (0, 1) (default=1)",
    )

    return parser

if __name__ == "__main__":
    test()
   