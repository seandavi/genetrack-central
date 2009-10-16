"""
Utility functions.


"""
import logger, conf
import os, sys, random, hashlib, re, string, csv, gc
import tempfile, os, random, glob, time

# dealing with roman numerals for chromosomes
from genetrack import roman

def path_join(*args):
    "Builds absolute path"
    return os.path.abspath(os.path.join(*args))

def chromosome_remap(text):
    """
    Attempts to produce the standardized chromosome from 
    multiple possible inputs::
        
        chr5, chr05, chrV, chrom5, chrom05, chromV -> chr5

    >>>
    >>> map(chromosome_remap, 'chr1 chr06 chrIX chrom02 chrom12 chromV'.split())
    ['chr1', 'chr6', 'chr9', 'chr2', 'chr12', 'chr5']
    >>>
    """

    if not text.startswith('chr'):
        return text

    text = text.replace('chrom','')
    text = text.replace('chr','')
    
    try:
        # cast to integer
        text = int(text)
    except ValueError, exc:
        try:
            # cast to roman numerals
            text = roman.fromRoman(text)
        except Exception, exc:
            pass

    return 'chr%s' % text

class Params(object):
    """
    >>> p = Params(a=1, b=2, c=None, d=None)
    >>> p.a, p.b
    (1, 2)
    >>> p.c, p.d
    (None, None)
    """
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

    def update(self, other):
        self.__dict__.update( other )

    def defaults(self, other):
        "Sets default values for non-existing attributes"
        store = dict()
        store.update( other )
        store.update( self.__dict__ )
        self.__dict__.update( store )

    def dict(self):
        return self.__dict__

    def get(self, key, default=None):
        return self.__dict__.get(key, default)

    def __repr__(self):
        return repr(self.__dict__)

def uuid(KEY_SIZE=128):
    "Genenerates a unique id"
    id  = str( random.getrandbits( KEY_SIZE ) )
    return hashlib.md5(id).hexdigest()
    
def nice_bytes( value ):
    """
    Returns a size as human readable bytes
    
    >>> nice_bytes(100), nice_bytes(10**4), nice_bytes(10**8), nice_bytes(10**10)
    ('100 bytes', '9 Kbytes', '95 Mbytes', '9 Gbyte')
    """
    if value < 1024: return "%s bytes" % value
    elif value < 1048576: return "%s Kbytes" % int(value/1024)
    elif value < 1073741824: return "%s Mbytes" % int(value/1048576)
    else: return "%s Gbyte" % int(value/1073741824)

def nice_sort( data ):
    """
    Sort the given list data in the way that humans expect. 
    Adapted from a posting by Ned Batchelder: http://nedbatchelder.com/blog/200712.html#e20071211T054956
    
    >>> data = [ 'chr1', 'chr2', 'chr10', 'chr100' ]
    >>> data.sort()
    >>> data
    ['chr1', 'chr10', 'chr100', 'chr2']
    >>> nice_sort(data)
    >>> data
    ['chr1', 'chr2', 'chr10', 'chr100']
    """
    def convert(text): 
        if text.isdigit():
            return int(text)
        else:    
            return text
            
    split    = lambda key: re.split('([0-9]+)', key)
    alphanum = lambda key: map(convert, split(key) )
    data.sort( key=alphanum )

def commify(n):
    """
    Formats numbers with commas

    >>> commify(10000)
    '10,000'
    """
    n = str(n)
    while True:
        (n, count) = re.subn(r'^([-+]?\d+)(\d{3})', r'\1,\2', n)
        if count == 0: 
            break
    return n 

class Timer(object):
    """
    A timer object for display elapsed times.

    >>> timer = Timer()
    >>> timer.format(30)
    '30.00 seconds'
    >>> timer.format(320)
    '5.3 minutes'
    >>> timer.format(3200)
    '53.3 minutes'
    >>> timer.format(30500)
    '8.5 hours'
    """
    def __init__(self):
        self.start()

    def start(self):
        self.start_time = time.time()

    def format(self, value):
        min1 = 60.0
        hour = 60 * min1
        if value < 60:
            return '%4.2f seconds' % value
        elif value < hour:
            return '%3.1f minutes' % (value/min1)
        else:
            return '%3.1f hours' % (value/hour)

    def report(self):
        elapsed = self.stop()
        return self.format( elapsed )

    def stop(self):
        elapsed = time.time() - self.start_time
        self.start()
        return elapsed

def gc_off( func ):
    """ 
    A decorator that turns the off the garbage collector 
    during the lifetime of the wrapped function

    >>> @gc_off
    ... def foo():
    ...    pass
    >>> foo()
    """
    def newfunc(*args,**kargs):
        try:
            gc.disable()
            result = func( *args, **kargs)
        finally:
            gc.enable()
        return result
    return newfunc

def make_tempfile( fname=None, dir='', prefix='temp-', suffix='.png'):
    """
    Returns a filename and filepath to a temporary file
    
    If the {tid} parameter is not specified it will generate a random id
    >>> make_tempfile(fname=1, prefix='img')[0]
    'img1.png'
    >>> len(make_tempfile())
    2
    """
    
    if fname == None:
        if dir:
            fd, fpath = tempfile.mkstemp( suffix=suffix, prefix=prefix, dir=dir, text='wb')
        else:
            fd, fpath = tempfile.mkstemp( suffix=suffix, prefix=prefix, text='wb')
        os.close(fd)
        head, fname = os.path.split( fpath )
    else:
        fname = '%s%s%s' % (prefix, fname, suffix)
        fpath = os.path.join( dir, fname )

    return fname, fpath
   
def test( verbose=0 ):
    "Performs module level testing"
    import doctest
    doctest.testmod( verbose=verbose )

if __name__ == "__main__":
    test()
