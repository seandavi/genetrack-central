"""
Bed file transformer. It may be invoked in multiple ways::

    python bed2genetrack.py

As python modules via the python module loader::

    python -m genetrack.scripts.bed2genetrack

Or in other python scripts::

>>>
>>> from genetrack.scripts import bed2genetrack
>>> bed2genetrack( input_name, output_name, shift=0)
>>>

Run the script with no parameters to soo the options.
"""
import os, sys, csv
from genetrack import logger, conf, util

def transform(inpname, outname, shift=0):
    """
    Transforms reads stored in bedfile to a genetrack input file.
    Requires at least 6 bed columns to access the strand.

    A genetrack input file format is a tab delimited text file
    described in the API documentation of the LinearData 
    class: `genetrack.hdflib.LinearData`

    The transformation is a three step process, transform, 
    sort and consolidate. It will create files placed in the 
    temporary data directory.

    It will invoke the system `sort` command to sort the file. 
    """

    # find the basename of the outputname
    basename = os.path.basename(outname)
   
    # two files store intermediate results
    flat = conf.tempdata( '%s.flat' % basename )
    sorted  = conf.tempdata( '%s.sorted' % basename )

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

    timer, full = util.Timer(), util.Timer()

    logger.debug("parsing '%s'" % inpname)
    logger.debug("output to '%s'" % outname)

    # write the unsorted output file
    logger.debug("unsorted flat file '%s'" % flat)

    fp = file(flat, 'wt')
    for row in reader:
        chrom, start, end, strand = row[0], row[1], row[2], row[5]
        if strand == '+':
            # forward strand, 5' is at start
            idx = int(start) + shift
            fwd, rev, val = 1, 0, 1
        elif strand == '-':
            # reverse strand, 5' is at end
            idx = int(end) - shift
            fwd, rev, val = 1, 0, 1
        else:
            # no strand specified, display as interval centers
            idx = (int(start)+int(end))/2
            fwd, rev, val = 0, 0, 1
        fp.write('%s\t%09d\t%s\t%s\t%s\n' % (chrom, idx, fwd, rev, val))
    fp.close()

    logger.debug("parsing finished in %s" % timer.report() )

    # now let sorting commence
    cmd = "sort %s > %s" % (flat, sorted)
    logger.debug("sorting into '%s'" % sorted)
    os.system(cmd)
    logger.debug("sorting finished in %s" % timer.report() )

    logger.debug("consolidating into '%s'" % outname)
    #os.system(cmd)
    logger.debug("consolidate finished in %s" % timer.report() )
    logger.debug("full run finished in %s" % full.report() )

    # attempting a cleanup
    for name in (flat, sorted):
        os.remove(name)

if __name__ == '__main__':
    import optparse

    usage = "usage: %prog -i inputfile -o outputfile -s correction (default=0)"

    parser = optparse.OptionParser(usage=usage)

    # setting the input file name
    parser.add_option(
        '-i', '--input', action="store", 
        dest="inpname", type='str', default=None,
        help="the input file name"
    )

    # setting the output file name
    parser.add_option(
        '-o', '--output', action="store", 
        dest="outname", type='str', default=None,
        help="output file name"
    )

    # verbosity can be 0,1 and 2 (increasing verbosity)
    parser.add_option(
        '-v', '--verbosity', action="store", 
        dest="verbosity", type="int", default=1, 
        help="sets the verbosity (0, 1) [default]",
    )

    # correction shift added in 5' direction for start/end coordinates
    parser.add_option(
        '-s', '--shift', action="store", 
        dest="shift", type="int", default=0, 
        help="sets the correction shift for each strand (default=0)",
    )

    options, args = parser.parse_args()

    # set verbosity
    if options.verbosity > 0:
        logger.disable(None)

    # missing file names
    if not (options.inpname and options.outname):
        parser.print_help()
    else:
        transform(inpname=options.inpname, outname=options.outname, shift=options.shift)
