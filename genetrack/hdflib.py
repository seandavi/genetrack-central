"""
Utilities for the hierarchical data format (HDF).

"""
from tables import openFile
from tables import IsDescription, IntCol, FloatCol
from genetrack import logger, util, conf
from itertools import *
import os, bisect, gc, csv

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

class LinearData(object):
    """
    A linear data class instance is an HFD representation of millions of 
    coordinates with one or more values associated with each of these 
    coordinates. The class can store such data for various labels (chromosomes). 
    The default parser built into the class can process files in the following 
    format::

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
    and reverse strands. The input file must be sorted by both coordinates 
    and chromosome (increasing order). Processing is performed in the 
    following manner:

    >>> from genetrack import conf
    >>>
    >>> fname = conf.testdata('test-hdflib-input.txt')
    >>> index = LinearData(fname=fname, workdir=conf.TEMP_DATA_DIR)   
    
    Upon the first instantiation the index will be created if it did
    not exist or if the `update=True` parameter was set.

    The `workdir` parameter is optional and if present must point 
    to the directory into which the resulting index file will be placed. 
    The contents of the linear data object may be accessed as a list 
    but note that only the accessed slice is loaded into memory (lazy access).

    >>> index.labels
    ['chr1', 'chr2', 'chr3']
    >>>
    >>> # this will return the HDF table as implmenented in pytables
    >>> table = index.table('chr1')
    >>>
    >>> list (table.cols.idx[:10])
    [146, 254, 319, 328, 330, 339, 341, 342, 345, 362]
    >>>
    >>> list( table.cols.fwd[:10])
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 1.0, 0.0, 1.0]
    >>>
    >>> list( table.cols.rev[:10])
    [1.0, 3.0, 1.0, 1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 0.0]
    
    We may also find the indices for real coordinates. For example the genomic
    coordinates 400 and 600 map to internal data indices of 20 to 31 
    (it works as a binary search that returns the left index)

    >>>
    >>> start, end = index.indices('chr1', 400, 600)
    >>> (start, end)
    (20, 31)

    We may also query for slices of data that span over an interval

    >>> results = index.query( 'chr1', 400, 600)
    >>> 
    >>> # the attributes are numeric arrays, here are cast to list
    >>>
    >>> list(results.idx)
    [402, 403, 411, 419, 427, 432, 434, 443, 587, 593, 596]
    >>>
    >>> list(results.fwd)
    [0.0, 1.0, 0.0, 0.0, 0.0, 2.0, 1.0, 0.0, 0.0, 0.0, 1.0]
    >>>
    >>> list(results.rev)
    [3.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0]
    >>>
    >>> list(results.val)
    [3.0, 1.0, 1.0, 1.0, 1.0, 2.0, 1.0, 1.0, 1.0, 1.0, 1.0]
    >>> index.close()
    >>>

    In order to provide the fastes parsing the internal parser
    is not overridable. There are transformers that can 
    change bed and gff files to this input format. See the 
    `genetrack.scripts' module.
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

        logger.info( "file='%s'" % self.fname )
        logger.info( "index='%s'" % self.index)

        # check file for existance
        if missing(self.fname):
            raise IOError('missing data %s' % self.fname)

        # provides timing information
        timer = util.Timer()

        # iterate over the file 
        reader = csv.reader( file(self.fname, 'rt'), delimiter='\t' )
    
        # unwind the reader until it hits the header
        for row in reader:
            if row[0] == 'chrom':
                break

        # helper function that flushes a table
        def flush( table, name ):
            # commit the changes
            table.flush() 
            # nicer information
            size = util.commify( len(table) )
            logger.info('table=%s, contains %s rows' % (name, size) )
        
        # print messages at every CHUNK line
        last_chrom = table = None
        db = openFile( self.index, mode='w', title='HDF index database')

        # continue on with reading, optimized for throughput
        # with minimal function calls (expensive in python)
        for index, row in izip(count(1), reader):

            # prints progress on processing
            if (index % CHUNK) == 0:
               liondb.info("... processed %s lines" % util.commify(index))    
            
            # get the values from each row
            chrom, index, fwd, rev, value = row
            fwd, rev, value = float(fwd), float(rev), float(value)
        
            # flush when switching chromosomes
            if chrom != last_chrom:
                # table==None at the beginning
                if table:
                    flush( table, last_chrom )

                # creates the new HDF table here
                table = db.createTable(  "/", chrom, TripletSchema, 'no description' )
                logger.info("creating table:%s" % chrom)
                last_chrom = chrom

            table.append( [ (index, fwd, rev, value) ] )

        # flush for last chromosome, report some timing information
        flush(table, chrom)
        lineno = util.commify(index)
        elapsed = timer.report()
        logger.info("finished inserting %s lines in %s" % (index, elapsed) )

        # close database
        db.close()

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

        idx = table.cols.idx[istart:iend:step]
        fwd = table.cols.fwd[istart:iend:step]
        rev = table.cols.rev[istart:iend:step]
        val = table.cols.val[istart:iend:step]
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
    
    def __del__(self):
        self.close()

def test( verbose=0 ):
    """
    Test runner
    """
    import doctest
    doctest.testmod(optionflags=doctest.ELLIPSIS)
    
if __name__ == "__main__":
    test()
