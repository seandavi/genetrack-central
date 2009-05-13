"""
Utitility classes that wrap files in the HDF (hierarchical data format).
"""
from tables import openFile
from tables import IsDescription, IntCol, FloatCol
from genetrack import logger, util, conf
from itertools import *
import os, bisect, gc

# missing file
missing = lambda f: not os.path.isfile(f)

# prints messages after processing chunk  number of lines
CHUNK = 10**5 

class TripletSchema( IsDescription ):
    """
    Stores a triplet of float values for each index. 
    """
    # the position arguments must be present
    idx = IntCol  ( pos=1 )  # index
    fwd = FloatCol( pos=2 )  # values on the forward strand
    rev = FloatCol( pos=3 )  # value on the reverse strand
    val = FloatCol( pos=4 )  # weighted value on the combined strands

def triplet_list_parser( row ):
    """
    Default parser. Takes as a list and returns a tuple that fits the schema.

    Note: a parser *MUST* return items in the same order as they are listed pos 
    argument of each field of the schema
    """
    return int(row[0]), float(row[1]), float(row[2]), float(row[3])

def triplet_dict_parser( row ):
    """
    Takes as input a dictionary keyed by the data header,
    returns a tuple that fits the schema.

    Note: a parser *MUST* return items in the same order as they are listed pos 
    argument of each field of the schema
    """
    idx = int  ( row['index']   )
    fwd = float( row['forward'] )
    rev = float( row['reverse'] )
    val = float( row['value'] )
    return idx, fwd, rev, val

class LinearData(object):
    """
    A linear data consists of a coordinate and one or more values associated with the 
    coordinate. It may contain various labels (chromosomes). In the input data within one 
    label the coordinates must be sorted (increasing order). The default parsers 
    can process files in the following format

        chrom	index	forward	reverse	value
        chr1	146	0.0	1.0	1.0
        chr1	254	0.0	3.0	3.0
        chr1	319	0.0	1.0	1.0
        chr1	328	0.0	1.0	1.0
        chr1	330	0.0	1.0	1.0
        chr1	339	0.0	1.0	1.0
        chr1	341	1.0	0.0	1.0
        ...

    The default representation is to store a value for the forward and reverse strands, 
    and to produce a composite value (stored as `value` column). In the most common
    case the composite value is simply the sum of the values on the forward 
    and reverse strands. Processing is performed in the following manner:

    >>> from genetrack import conf
    >>>
    >>> fname = conf.testdata('hdflib-testinput.txt')
    >>> index = LinearData(fname=fname, workdir=conf.temp_dir)   
    
    """

    """
   
    >>>
    >>> index.labels
    ['chr01', 'chr02', 'chr03']
    
    The `workdir` parameter is optional and if present must point 
    to the directory into which the resulting index file will be placed. 
    The contents of the linear data object
    may be accessed as a list but note that only the accessed slice 
    is loaded into memory (lazy access).

    >>> table = index.table('chr01')
    >>>
    >>> list (table.cols.idx[:10] )
    [146, 254, 319, 328, 330, 339, 341, 342, 345, 362]
    >>>
    >>> list( table.cols.fwd[:10] )
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0]
    >>>
    >>> list( table.cols.rev[:10] )
    [1.0, 3.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 0.0]
    
    We may also find the indices for real coordinates. For example the genomic
    coordinates 400 and 600 map to internap indices 20 to 31 (it is a binary search 
    that returns the left index)

    >>> start, end = index.indices( 'chr01', 400, 600)
    >>> (start, end)
    (20, 31)
    
    We may also query for slices of data that span over a real genomic interval

    >>> results = index.query( 'chr01', 400, 600)
    >>> results.idx
    [402, 403, 411, 419, 427, 432, 434, 443, 587, 593, 596]
    >>> results.fwd
    [0.0, 1.0, 0.0, 0.0, 0.0, 2.0, 1.0, 0.0, 0.0, 0.0, 1.0]
    >>> results.rev
    [3.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0]
    >>> results.val
    [3.0, 1.0, 1.0, 1.0, 1.0, 2.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    >>> index.close()
    """

    def __init__(self, fname, workdir=None, update=False ):
        """
        Create the LinearData
        """
        self.fname = fname
        
        # split the incoming name to find the real name, and base directory
        basedir, basename = os.path.split(self.fname)

        # the index may be stored in the workdir if it was specified
        basedir = workdir or basedir

        # this is the HDF index name that the file operates on
        self.index = conf.path_join(basedir, '%s.hdf' % basename)

        # debug messages
        logger.debug('file path %s' % self.fname)
        logger.debug('index path %s' % self.index)

        # creating indices if these are missing or an update is forced
        if update or missing(self.index):
            self.build()

        # operates on the HDF file
        self.db=openFile(self.index, mode='r')
        self.root = self.db.root
        
        # shows the internal labels
        logger.debug('index labels -> %s' % self.labels)

    def build(self):
        "May be overriden to use different parsers and schemas"

        # it is calling an module level function with two parameters
        # original file name and desired index location
        build_index(self.fname, self.index)

    @property
    def labels(self):
        "Labels in the file"
        labs = [ x.name for x in self.root._f_listNodes() ]
        util.nice_sort( labs )
        return labs
    
    def indices( self, label, start, end, colattr='idx'):
        """
        Returns the array indices that correspond the start, end values of index column
        
        Note that for this to work the values for the column attribute 'colattr' 
        in the table must be sorted in increasing order 
        """
        table  = self.table( label )
        column = getattr(table.cols, colattr)
        istart = bisect.bisect_left( column, start )
        iend   = bisect.bisect_left( column, end  )
        return istart, iend

    def query(self, label, start, end, pad=0 ):
        """
        Returns data that spans star to end as a class 
        with attributes for idx, fwd, rev and val
        """

        step  = 1
        table = self.table( label )
        istart, iend = self.indices(label=label, start=start-pad, end=end+pad)
        idx = table.cols.idx[istart:iend:step].tolist()
        fwd = table.cols.fwd[istart:iend:step].tolist()
        rev = table.cols.rev[istart:iend:step].tolist()
        val = table.cols.val[istart:iend:step].tolist()        
        params = util.Params( idx=idx, fwd=fwd, rev=rev, val=val )
        return params
    
    def chunks(self, label, size=10**6, step=1 ):
        """
        Returns the data as chunks of size. All columns are
        simultaneously iterated over.
        """
        table = self.table( label )
        for start in xrange(0, 10**9, size):
            end = start + size
            idx = table.cols.idx[start:end:step].tolist()
            if not idx:
                break
            fwd = table.cols.fwd[start:end:step].tolist()
            rev = table.cols.rev[start:end:step].tolist()
            val = table.cols.val[start:end:step].tolist()        
            yield idx, fwd, rev, val
        
    def table(self, label):
        return getattr( self.root, label )

    def close(self):
        self.db.close()
    
def build_index( data_path, index_path, parser=None, schema=None):
    """
    Indexer for the data
    """

    # fetch the default parsers if these are missing
    parser = parser or triplet_parser
    schema = schema or TripletSchema

    logger.info( "file='%s'" % data_path )
    logger.info( "index='%s'" % index_path )

    if missing(data_path):
        raise IOError('missing data %s' % data_path)

    # provides timing information
    timer = util.Timer()

    def flush( table, name ):
        "Helper function to flush a table"
        if table is not None:
            table.flush() # commit the changes
            size = util.commify( len(table) )
            logger.info('table=%s, wrote %s rows' % (name, size) )
    
    # print messages at every CHUNK line
    last_chrom = table = None
    db = openFile( index_path, mode='w', title='HDF index database')
   
    # iterate over the file and insert into table
    reader = util.dict_reader( data_path )
    
    #reader = islice(reader, 0, 13000)
    
    for lineno, row in reader:
        if (lineno % CHUNK) == 0:
           liondb.info("... processed %s lines" % util.commify(lineno) )    
        
        chrom = row['chrom']
        
        if chrom != last_chrom:
            # flush when switching chromosomes
            flush( table, last_chrom )
            table = db.createTable(  "/", chrom, schema, 'no description' )
            last_chrom = chrom
            logger.info("creating table:%s" % chrom)

        # parser must match schema
        row = parser( row )
        table.append( [ row ] )

    # flush for last chromosome
    flush(table, chrom)
    lineno = util.commify(lineno)
    elapsed = timer.report()
    logger.info("finished inserting %s lines in %s" % (lineno, elapsed) )

    db.close()

def test( verbose=0 ):
    """
    Test runner
    """
    import doctest
    doctest.testmod(optionflags=doctest.ELLIPSIS)
    
if __name__ == "__main__":
    test()
