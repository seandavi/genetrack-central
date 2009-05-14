"""
Utility functions
"""
import os, sys, random, hashlib, re, string, csv, gc
import tempfile, os, random, glob, time

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

def bedreads2genetrack(inpname, outname, shift=0):
    """
    Transforms reads stored in bedfile to a genetrack input file.
    Requires at least 6 bed columns.
    """

    # check for track information on first line, 
    # faster this way than conditional checking on each line
    fp = file(inpname, 'rU')
    first = fp.readline()
    fp.close()

    # create the reader
    reader = csv.reader(file(inpname, 'rU'), delimiter='\t')

    # skip if trackline exists
    if first.startswith == 'track':
        reader.next()

    # write to the output file
    op = file(outname, 'wt')
    op.write('#\n# transformed from \%s\n#\n' % inpname)
    op.write('chrom\tindex\tforward\treverse\tvalue\n')
    for row in reader:
        chrom, start, end, strand = row[0], row[1], row[2], row[5]
        if strand == '+':
            start = int(start)
            idx = start + shift 
            fwd, rev, val = 1, 0, 1
        elif strand == '-':
            end = int(end)
            idx = end - shift
            fwd, rev, val = 1, 0, 1
        else:
            start = int(start)
            end = int(end)
            idx = (start+end)/2
            fwd, rev, val = 1, 0, 1
        op.write('%s\t%09d\t%s\t%s\t%s\n' % (chrom, idx, fwd, rev, val))
    op.close()
    
def make_stream(fname):
    """
    Creates a django style chunked file stream (used in testing)

    >>> stream = make_stream(__file__)
    >>> for chunk in stream.chunks(size=10):
    ...     pass
    >>>
    """
   
    class Chunks:
        def __init__(self,fname):
            self.fname = fname
        
        def chunks(self, size=2**10):
            "Returns chunks of data"
            fp = open(self.fname,'rb')
            while 1:
                data = fp.read(size)
                if not data:
                    raise StopIteration()
                yield data

    return Chunks(fname)

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
